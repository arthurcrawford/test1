import getpass
import os
import uuid
import pytest
from raptly.aptly_api import AptlyApi, RaptlyError, local, AptlyApiError


@pytest.fixture
def api():
    return AptlyApi(repo_url='http://localhost:9876/api')


@pytest.fixture
def empty_test_repo(api):
    """Create empty repo and return its name"""
    # Create a unique-ish repo name
    public_repo_name = generate_repo_name()
    # Create the repo
    api.create(public_repo_name)
    return public_repo_name


@pytest.fixture
def primed_test_repo(api, empty_test_repo):
    """Create new repo with three packages released to stable"""
    # Deploy packages
    packages = ['capricciosa_2.1.0_all',
                'fiorentina_0.9.7_all',
                'margherita_1.0.0_all']
    package_file_names = []
    for package in packages:
        package_file_names.append(get_path('%s.deb' % package))

    api.deploy(empty_test_repo, package_file_names, '', api.local_user)

    # Move through test, staging & stable
    release_id = generate_release_id()
    union, new_packages, snapshot_release_candidate = \
        api.test(public_repo_name=empty_test_repo,
                 package_query='fiorentina_0.9.7_all|margherita_1.0.0_all|capricciosa_2.1.0_all',
                 release_id=release_id,
                 dry_run=False)

    api.stage(public_repo_name=empty_test_repo, testing_distribution_name=api.testing_name,
              staging_distribution_name=api.staging_name, release_id=release_id)

    api.release(public_repo_name=empty_test_repo, staging_distribution_name=api.staging_name,
                stable_distribution_name=api.stable_name, release_id=release_id)

    return empty_test_repo


def generate_repo_name():
    return str(uuid.uuid1())[:13].replace('-', '/')


def generate_release_id():
    return 'TKT-%s' % str(uuid.uuid1())[:4]


def test_create(api):
    # Record how many repos there are before
    before = api.get_published_repos()
    repo_public_name = generate_repo_name()
    # Create the repo
    api.create(repo_public_name)
    after = api.get_published_repos()
    assert len(after) - len(before) == 1

    repo_local_name = api.get_local_repo(repo_public_name)['Name']
    assert repo_local_name == local(repo_public_name)


def test_create_failure_already_exists(api, empty_test_repo):
    # Record how many repos there are before
    before = api.get_published_repos()
    repo_public_name = empty_test_repo
    # Create the repo, expecting failure
    with pytest.raises(AptlyApiError):
        api.create(repo_public_name)

    after = api.get_published_repos()
    assert len(after) == len(before)


def test_upload(api):
    # api = AptlyApi('http://localhost:9876/api', verbose=True)
    upload_dir = "%s" % getpass.getuser()
    package_filenames = [get_path('margherita_1.0.0_all.deb'),
                         get_path('margherita_1.1.0_all.deb'),
                         get_path('fiorentina_1.0.2_all.deb')]
    paths = api.upload(package_filenames=package_filenames, upload_dir=upload_dir)
    assert len(paths) == len(package_filenames)
    for i in range(0, len(paths)):
        assert '%s/%s' % (upload_dir, os.path.basename(package_filenames[i])) in paths

    with pytest.raises(IOError):
        api.upload(package_filenames=['non-existent'], upload_dir=upload_dir)


def test_check_failure_no_repo(api, empty_test_repo):
    """Error handling and exceptions in the check API call"""
    # No such repo exists
    with pytest.raises(RaptlyError):
        api.check('non-existent', package_files=[], upload_dir=api.local_user)


def test_check_failure_no_stable(api, empty_test_repo):
    """Error handling and exceptions in the check API call"""
    # Repo exists but no stable distribution
    with pytest.raises(RaptlyError):
        api.check(public_repo_name=empty_test_repo, package_files=[], upload_dir=api.local_user)


def test_check_no_packages(api, primed_test_repo):
    """Test correct behaviour when creating a check repo and specifying empty package list.
    Correct behaviour in this case is for new check repo check distribution to contain exactly
    the same packages as the stable distribution.
    """

    # Get the packages in the stable distribution
    stable_pkgs = api.pkg_list(primed_test_repo, 'stable')

    # Create a check distribution, but don't specify any packages to check
    api.check(public_repo_name=primed_test_repo, package_files=[], upload_dir=api.local_user)

    check_repo_public_name = "%s.@%s@" % (primed_test_repo, api.local_user)
    check_repo_local_name = api.get_local_repo(check_repo_public_name)['Name']
    assert check_repo_local_name == local(check_repo_public_name)

    check_pkgs = api.pkg_list(check_repo_public_name, 'check')

    # Assert that contents of stable_pkgs and check_pkgs are the same
    assert len(set(stable_pkgs) & set(check_pkgs)) == len(stable_pkgs)

    api.check_clean(public_repo_name=primed_test_repo)

    # Check that the repo has been removed
    with pytest.raises(RaptlyError):
        api.get_local_repo(check_repo_public_name)


def test_check_with_packages(api, primed_test_repo):
    # Create a check distribution
    check_packages = ['fiorentina_1.0.0_all',
                      'margherita_1.1.0-beta_all']
    check_package_file_names = []
    for check_package in check_packages:
        check_package_file_names.append(get_path('%s.deb' % check_package))

    api.check(public_repo_name=primed_test_repo, package_files=check_package_file_names,
              upload_dir=api.local_user)


def test_deploy(api):
    # api = AptlyApi('http://localhost:9876/api')
    # Create a unique-ish 8 character repo name
    repo_name = str(uuid.uuid1())[:8]
    # Create the repo
    distribution = 'unstable'
    api.create(repo_name, distribution)
    before = api.pkg_list(repo_name, distribution)
    packages = ['fiorentina_0.9.7_all',
                'fiorentina_1.0.0_all',
                'fiorentina_1.0.1-beta_all',
                'margherita_1.1.0-beta_all',
                'margherita_1.0.0_all']
    package_file_names = []
    for package in packages:
        package_file_names.append(get_path('%s.deb' % package))

    api.deploy(repo_name, package_file_names, '', 'test', distribution)
    after = api.pkg_list(repo_name, distribution)
    assert len(after) - len(before) == len(package_file_names)
    api.undeploy(repo_name, packages[0], distribution, False)
    api.undeploy(repo_name, packages[1], distribution, False)
    final = api.pkg_list(repo_name, distribution)
    assert len(packages) - len(final) == 2


def test_test(api, empty_test_repo):
    # api = AptlyApi('http://localhost:9876/api')
    # Create a unique-ish 8 character repo name
    repo_name = empty_test_repo
    before = api.pkg_list(repo_name, 'unstable')
    api.deploy(repo_name, [get_path('margherita_1.0.0_all.deb')], '', 'test', 'unstable')

    # Create a test candidate
    union, new_packages, snapshot_release_candidate = api.test(public_repo_name=repo_name,
                                                               package_query='margherita_1.0.0_all',
                                                               release_id=repo_name,
                                                               dry_run=False)
    assert len(union) == 1
    assert len(new_packages) == 1

    # Move to staging

    #
    #
    # api.deploy(repo_name, get_path('margherita_1.1.0-2_all.deb'), '', distribution)
    # time.sleep(2)
    # after = api.pkg_list(repo_name, distribution)
    # assert len(after) - len(before) == 2
    # api.undeploy(repo_name, 'margherita_1.0.0_all', distribution, False)
    # time.sleep(2)
    # api.undeploy(repo_name, 'margherita_1.1.0-2_all', distribution, False)
    # time.sleep(2)
    # final = api.pkg_list(repo_name, distribution)
    # assert len(before) == len(final)


def get_path(deb):
    return os.path.join(os.path.dirname(__file__), deb)
