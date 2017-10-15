import getpass
import os
import uuid
from pytest import raises

from raptly.aptly_api import AptlyApi, RaptlyError


def test_create():
    api = AptlyApi('http://localhost:9876/api')
    # Record how many repos there are before
    before = api.get_published_repos()
    # Create a unique-ish 8 character repo name
    repo_name = str(uuid.uuid1())[:8]
    # Create the repo
    api.create(repo_name, 'unstable')
    after = api.get_published_repos()
    assert len(after) - len(before) == 1


def test_upload():
    api = AptlyApi('http://localhost:9876/api', verbose=True)
    upload_dir = "%s" % getpass.getuser()
    package_filenames = [get_path('margherita_1.0.0_all.deb'),
                         get_path('margherita_1.1.0_all.deb'),
                         get_path('fiorentina_1.0.2_all.deb')]
    paths = api.upload(package_filenames=package_filenames, upload_dir=upload_dir)
    assert len(paths) == len(package_filenames)
    for i in range(0, len(paths)):
        assert '%s/%s' % (upload_dir, os.path.basename(package_filenames[i])) in paths

    with raises(IOError):
        api.upload(package_filenames=['non-existent'], upload_dir=upload_dir)


def test_check_fails():
    """Error handling and exceptions in the check API call"""
    api = AptlyApi('http://localhost:9876/api')
    # Create a unique-ish repo name
    public_repo_name = str(uuid.uuid1())[:13].replace('-', '/')
    # Create the repo
    distribution = 'unstable'
    api.create(public_repo_name, distribution)

    # Repo exists but no stable distribution
    with raises(RaptlyError):
        api.check(public_repo_name=public_repo_name, package_files=[], upload_dir=api.local_user)

    # No such repo exists
    with raises(RaptlyError):
        api.check('non-existent', package_files=[], upload_dir=api.local_user)


def test_check():
    api = AptlyApi('http://localhost:9876/api')
    # Create a unique-ish repo name
    public_repo_name = str(uuid.uuid1())[:13].replace('-', '/')
    # Create the repo
    distribution = 'unstable'
    api.create(public_repo_name, distribution)
    packages = ['fiorentina_0.9.7_all',
                'margherita_1.0.0_all']
    package_file_names = []
    for package in packages:
        package_file_names.append(get_path('%s.deb' % package))

    api.deploy(public_repo_name, package_file_names, '', distribution, api.local_user)

    # Move through test, staging & stable
    release_id = 'TKT-999'
    union, new_packages, snapshot_release_candidate = \
        api.test(public_repo_name=public_repo_name,
                 package_query='fiorentina_0.9.7_all|margherita_1.0.0_all',
                 release_id=release_id,
                 unstable_distribution_name='unstable',
                 testing_distribution_name='testing',
                 stable_distribution_name='stable',
                 dry_run=False)

    api.stage(public_repo_name=public_repo_name, testing_distribution_name=api.testing_name,
              staging_distribution_name=api.staging_name, release_id=release_id)

    api.release(public_repo_name=public_repo_name, staging_distribution_name=api.staging_name,
                stable_distribution_name=api.stable_name, release_id=release_id)

    # Create a check distribution
    check_packages = ['fiorentina_1.0.0_all',
                      'margherita_1.1.0-beta_all']
    check_package_file_names = []
    for check_package in check_packages:
        check_package_file_names.append(get_path('%s.deb' % check_package))

    api.check(public_repo_name=public_repo_name, package_files=check_package_file_names,
              upload_dir=api.local_user)


def test_deploy():
    api = AptlyApi('http://localhost:9876/api')
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

    api.deploy(repo_name, package_file_names, '', distribution, 'test')
    after = api.pkg_list(repo_name, distribution)
    assert len(after) - len(before) == len(package_file_names)
    api.undeploy(repo_name, packages[0], distribution, False)
    api.undeploy(repo_name, packages[1], distribution, False)
    final = api.pkg_list(repo_name, distribution)
    assert len(packages) - len(final) == 2


def test_test():
    api = AptlyApi('http://localhost:9876/api')
    # Create a unique-ish 8 character repo name
    repo_name = str(uuid.uuid1())[:8]
    # Create the repo
    distribution = 'unstable'
    api.create(repo_name, distribution)
    before = api.pkg_list(repo_name, distribution)
    api.deploy(repo_name, [get_path('margherita_1.0.0_all.deb')], '', distribution, 'test')

    # Create a test candidate
    union, new_packages, snapshot_release_candidate = api.test(public_repo_name=repo_name,
                                                               package_query='margherita_1.0.0_all',
                                                               release_id=repo_name,
                                                               unstable_distribution_name='unstable',
                                                               testing_distribution_name='testing',
                                                               stable_distribution_name='stable',
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
