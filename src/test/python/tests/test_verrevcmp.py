from raptly.debian_version import verrevcmp


def test_less_than():
    assert verrevcmp('1', '2') < 0
    assert verrevcmp('1.9', '1.10') < 0
    assert verrevcmp('4.5', '4.5.1') < 0
    assert verrevcmp('4.5.0', '4.5.1') < 0
    assert verrevcmp('4.5-alpha', '4.5.1') < 0
    assert verrevcmp('4.5-alpha', '4.5-beta') < 0
    assert verrevcmp('0.1.0-1', '0.1.0-2') < 0
    assert verrevcmp('0.1.0-1', '0.2.0') < 0
    assert verrevcmp('0.1.0-1', '1.0.0') < 0


def test_greater_than():
    assert verrevcmp('2', '1') > 0
    assert verrevcmp('2.0.0', '1.234.567+456') > 0
    assert verrevcmp('4.3.4-2', '4.3.4-1') > 0
    assert verrevcmp('4.3.4+86', '4.3.4+85') > 0
    assert verrevcmp('4.5-gamma', '4.5-beta') > 0


def test_equal_than():
    assert verrevcmp('1', '1') == 0
    assert verrevcmp('1.20.3', '1.20.3') == 0
    assert verrevcmp('4.3.4+85', '4.3.4+85') == 0
