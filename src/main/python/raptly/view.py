from aptly_api import pkg_ref_version_key
from aptly_api import compare_versions
from packages import sort_by_name_and_version, prune
import aptly_api
import json
import sys


def print_package_refs(package_refs):
    """Print package refs to stdout - sort first by version then by name
    :param package_refs: List of aptly package references
    """
    sorted_by_version = sorted(package_refs, key=pkg_ref_version_key(compare_versions))
    sorted_by_name = sorted(sorted_by_version, key=lambda pr: pr[1:].split()[1])

    for package_ref in sorted_by_name:
        package_ref_fields = package_ref[1:].split()
        print '  %s %s %s' % (package_ref_fields[1], package_ref_fields[2], package_ref_fields[0])


def show_distribution(api, is_pruned, is_json, public_repo_name, distribution):
    """Show the package contents of a distribution
    :param api: The aptly api wrapper
    :param is_pruned: Whether the user wants package-version lists pruned to latest versions only
    :param is_json: Output raw json instead of pretty formatted output
    :param public_repo_name: The public name of the repo (i.e. with '/' slashes)
    :param distribution: The repo distribution - e.g. unstable, stable etc
    """
    # Get the publication of the specified repo + distribution
    matching_publication = api.get_publication(public_repo_name=public_repo_name, distribution=distribution)
    if matching_publication is None:
        raise aptly_api.RaptlyError('Distribution not found: %s %s' % (public_repo_name, distribution))

    print('Prefix:       %s' % matching_publication['Prefix'])
    print('Distribution: %s' % matching_publication['Distribution'])
    print('Source:')
    # Print out the Source - aka, usually, the source snapshot
    for source in matching_publication['Sources']:
        print('  %s' % source['Name'])
    print('Packages: ')
    # Sort list of package refs first on package name, then on Debian version
    # Each record is of the form:
    #    'Pamd64 zonza-projects 1.24.6+14 3dede259289aa0aa'
    # where:
    #    package_name   = [1]
    #    debian_version = [2]
    # Correct Debian version sorting provided by debian_version.compare_versions
    unsorted = api.get_packages(matching_publication)

    # If caller wants the list pruned:
    if is_pruned:
        final_list = prune(unsorted)
    else:
        final_list = sort_by_name_and_version(unsorted)

    if is_json:
        print json.dumps(final_list)
    else:
        # Print out one package name per line
        print_package_refs(final_list)


def show_repos(repos, is_json=False):
    """Show a list of repositories
    :param repos: The list of repository names
    :param is_json: Show as json string
    """
    if is_json:
        print json.dumps(repos)
    else:
        # Print out one repo name per line
        print("Repositories:")
        for repo in repos:
            print "  %s" % repo


def show_distributions(dists, is_json):
    """Show a list of distributions
    :param dists: The list of distributions
    :param is_json: Show as json string
    """
    if is_json:
        print json.dumps(dists)
    else:
        # Print out one distribution name per line
        print("Distributions:")
        for dist in dists:
            sys.stdout.write("  %s -> " % dist['Distribution'])
            for source in dist['Sources']:
                sys.stdout.write("%s " % source['Name'])
            print("")


def show_test_cmd_output(api, is_dry_run, new_packages, public_repo_name, release_id, snapshot_release_candidate,
                         union):
    """Show results from creating a test candidate
    :param api: The aptly api wrapper
    :param is_dry_run: Is this a dry run
    :param new_packages: New packages that were added
    :param public_repo_name: The public repo name (i.e. with '/' slashes)
    :param release_id: The unique release ID
    :param snapshot_release_candidate: The name of the snapshot for this test candidate
    :param union: The list of packages constituting the test candidate
    """
    if len(union) <= 0:
        print("No packages: nothing to do")
        return

    if len(new_packages) <= 0:
        print("No new packages:")

    print('Test candidate %s:' % release_id)
    print('Snapshot: %s' % ('(dry run - none created)' if is_dry_run else snapshot_release_candidate))
    print('Repository: %s' % public_repo_name)
    print('Distribution: %s' % api.testing_name)
    print('Packages:')
    print_package_refs(union)
