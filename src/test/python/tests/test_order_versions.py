from raptly.debian_version import order
import string


def test_squiggle():
    assert order('~') == -1


def test_digit():
    assert order('9') == 0


def test_empty():
    assert order('') == 0


def test_letters():
    for a in string.ascii_letters:
        assert order(a) == ord(a)


def test_non_letters():
    assert order('.') == ord('.') + 256
    assert order('+') == ord('+') + 256
    assert order('-') == ord('-') + 256
    assert order(':') == ord(':') + 256
