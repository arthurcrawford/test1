from raptly.debian_version import compare_versions


def test_less_than():
    assert compare_versions('1:4.3.3-1', '2:4.3.3-1') < 0
    assert compare_versions('1:4.3.3-1', '1:4.3.3-2') < 0
    assert compare_versions('1:4.3:3-1', '1:4.3:4-1') < 0
    assert compare_versions('1:4.3-a-1', '1:4.3-a-2') < 0


def test_equal():
    assert compare_versions('1:4.3.3-1', '1:4.3.3-1') == 0
