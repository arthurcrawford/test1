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
    api.create(repo_name, 'unstable')
    time.sleep(3)
    package_filename = os.path.join(os.path.dirname(__file__), 'margherita_1.0.0_all.deb')
    api.deploy(repo_name, package_filename, '', 'unstable')
    time.sleep(3)
    api.undeploy(repo_name, 'margherita_1.0.0_all', 'unstable', False)
    time.sleep(3)
