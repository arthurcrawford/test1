"""Debian version utility.

This module provides a verion comparison for Debian version strings.

Examples:

    It is designed to have the same semantics as dpkg --compare-versions

        dpkg --compare-versions 1.0.0+23 gt 1.0.0 && echo True

.. see dpkg code:
     dpkg/lib/dpkg/vercmp.c

"""


class Version:
    def __init__(self, value):

        remainder = value

        # Get epoch from split on first occurrence of ':'
        epoch_split = value.split(':', 1)
        if len(epoch_split) > 1:
            self.epoch = epoch_split[0]
            remainder = epoch_split[1]
        else:
            self.epoch = 0

        # Get revision from split on last occurrence of '-'
        revision_split = remainder.rsplit('-', 1)
        if len(revision_split) > 1:
            self.revision = revision_split[1]
            remainder = revision_split[0]
        else:
            self.revision = ''

        self.upstream = remainder


def order(x):
    """
    Determine sort order of char (x)

    :param x: character to test
    :return: order value

    char class   order value
    ----------   -----------
    '~'           -1
    digits        0
    empty         0
    letters       ascii x
    non-letters   ascii x + 256
    """
    return \
        -1 if x == '~' \
            else 0 if x.isdigit() \
            else 0 if not x \
            else ord(x) if x.isalpha() \
            else ord(x) + 256


def compare_versions(val, ref):
    """Compare two Debian versions

    return < 0 if val is less than ref
    return 0 if val and ref equal
    return > 0 if val is greater than ref
    """

    v = Version(val)
    r = Version(ref)

    # If epochs differ
    if v.epoch != r.epoch:
        if r.epoch > v.epoch:
            return -1
        else:
            return 1

    # Epochs are the same or missing

    # If upstream versions differ
    upstream_cmp = verrevcmp(v.upstream, r.upstream)
    if upstream_cmp != 0:
        if upstream_cmp < 0:
            return -1
        else:
            return 1

    # Upstream versions are the same

    # If debian revisions differ
    revision_cmp = verrevcmp(v.revision, r.revision)

    if revision_cmp != 0:
        if revision_cmp < 0:
            return -1
        else:
            return 1

    # Versions are equal
    return 0


def verrevcmp(val, ref):
    """Return result of comparing upstream_version or debian_revision strings val and ref

    return < 0 if val is less than ref
    return 0 if val and ref equal
    return > 0 if val is greater than ref
    """

    if not val:
        val = ''
    if not ref:
        ref = ''

    # Whilst we haven't reached the end of both strings yet
    while val or ref:

        first_diff = 0

        # Whilst one of the strings has some non-digits
        while (val and not val[0].isdigit()) or (ref and not ref[0].isdigit()):

            # Determine the alphanumeric ordering
            vc = order(val[0] if val else '')
            rc = order(ref[0] if ref else '')

            if vc != rc:
                return vc - rc

            val = val[1:] if val else ''
            ref = ref[1:] if ref else ''

        # At least one string has ended a run of non-digits

        # Discard any 0 padding from numerical sequences
        while val and val[0] == '0':
            val = val[1:]
        while ref and ref[0] == '0':
            ref = ref[1:]

        # While we're still seeing digits in both strings
        while (val and val[0].isdigit()) and (ref and ref[0].isdigit()):

            if not first_diff:
                first_diff = ord(val[0]) - ord(ref[0])

            val = val[1:]
            ref = ref[1:]

        # If we're still processing digits in val
        if val and val[0].isdigit():
            # val must be the greater version
            return 1

        # If we're still processing digits in ref
        if ref and ref[0].isdigit():
            # ref must be the greater version
            return -1

        # Same number of digits in this segment - return first numerical diff if there was one
        if first_diff:
            return first_diff

    # Versions equal
    return 0
