#!/usr/bin/env python

from debian_version import compare_versions

def main():

    print("Hello from test1")

    print("Importing module raptly.debian_version, testing version comparisons..")

    assert compare_versions('1:4.3.3-1', '2:4.3.3-1') < 0
    assert compare_versions('1:4.3.3-1', '1:4.3.3-2') < 0
    assert compare_versions('1:4.3:3-1', '1:4.3:4-1') < 0
    assert compare_versions('1:4.3-a-1', '1:4.3-a-2') < 0

    print("done")

if __name__ == "__main__":
    main()
