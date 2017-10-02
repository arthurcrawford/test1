import uuid
import os
import time
import getpass

from raptly.aptly_api import AptlyApi


def test_create():
    api = AptlyApi('http://localhost:9876/api')
    # Record how many repos there are before
    before = api.list_published_repos()
    # Create a unique-ish 8 character repo name
    repo_name = str(uuid.uuid1())[:8]
    # Create the repo
    api.create(repo_name, 'unstable')
    after = api.list_published_repos()
    assert len(after) - len(before) == 1


def test_upload():
    api = AptlyApi('http://localhost:9876/api', verbose=True)
    upload_dir = "%s" % getpass.getuser()
    package_filenames = [get_path('margherita_1.0.0_all.deb'),
                         get_path('margherita_1.1.0_all.deb'),
                         get_path('fiorentina_1.0.2_all.deb')]
    paths = api.upload(package_filenames=package_filenames,
                       upload_dir=upload_dir)
    assert len(paths) == len(package_filenames)
    for i in range(0, len(paths)):
        assert '%s/%s' % (upload_dir, os.path.basename(package_filenames[i])) in paths


def test_deploy():
    api = AptlyApi('http://localhost:9876/api')
    # Create a unique-ish 8 character repo name
    repo_name = str(uuid.uuid1())[:8]
    # Create the repo
    distribution = 'unstable'
    api.create(repo_name, distribution)
    time.sleep(2)
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
    time.sleep(2)
    after = api.pkg_list(repo_name, distribution)
    assert len(after) - len(before) == len(package_file_names)
    api.undeploy(repo_name, packages[0], distribution, False)
    time.sleep(2)
    api.undeploy(repo_name, packages[1], distribution, False)
    time.sleep(2)
    final = api.pkg_list(repo_name, distribution)
    assert len(packages) - len(final) == 2


def test_test():
    api = AptlyApi('http://localhost:9876/api')
    # Create a unique-ish 8 character repo name
    repo_name = str(uuid.uuid1())[:8]
    # Create the repo
    distribution = 'unstable'
    api.create(repo_name, distribution)
    time.sleep(2)
    before = api.pkg_list(repo_name, distribution)
    api.deploy(repo_name, [get_path('margherita_1.0.0_all.deb')], '', distribution, 'test')
    time.sleep(2)

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
