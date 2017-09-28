"""
Methods for manipulating lists of packages returned by aptly
"""
import aptly_api
from aptly_api import compare_versions


def sort_by_version(packages):
    return sorted(packages, key=aptly_api.pkg_ref_version_key(compare_versions))


def sort_by_name(packages):
    return sorted(packages, key=lambda pr: pr[1:].split()[1])


def sort_by_name_and_version(packages):
    return sort_by_name(sort_by_version(packages))


def prune(packages):
    """Prune package list to include only the latest version of each package in the list.
    It sorts the package list first by name and version in order to do this.
    :return: Pruned package list
    """
    sorted_by_name_and_version = sort_by_name_and_version(packages)
    visited = set()
    pruned = []
    for pkg in reversed(sorted_by_name_and_version):
        package_name = pkg[1:].split()[1]
        if package_name not in visited:
            pruned.append(pkg)
            visited.add(package_name)
    return list(reversed(pruned))

