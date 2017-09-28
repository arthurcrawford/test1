import uuid
import os
import time

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


def test_deploy():
    api = AptlyApi('http://localhost:9876/api')
    # Create a unique-ish 8 character repo name
    repo_name = str(uuid.uuid1())[:8]
    # Create the repo
    distribution = 'unstable'
    api.create(repo_name, distribution)
    time.sleep(2)
    before = api.pkg_list(repo_name, distribution)
    api.deploy(repo_name, get_path('margherita_1.0.0_all.deb'), '', distribution)
    # time.sleep(2)
    api.deploy(repo_name, get_path('margherita_1.1.0-2_all.deb'), '', distribution)
    time.sleep(2)
    after = api.pkg_list(repo_name, distribution)
    assert len(after) - len(before) == 2
    api.undeploy(repo_name, 'margherita_1.0.0_all', distribution, False)
    time.sleep(2)
    api.undeploy(repo_name, 'margherita_1.1.0-2_all', distribution, False)
    time.sleep(2)
    final = api.pkg_list(repo_name, distribution)
    assert len(before) == len(final)


def get_path(deb):
    return os.path.join(os.path.dirname(__file__), deb)
