import uuid

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

