import argparse
import json
import os
import sys

import toml

import aptly_api
from _version import __version__
from aptly_api import AptlyApi
from debian_version import compare_versions


# TODO - coloured output for new packages etc
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# To remove metavar character from sub-command listing
class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts

    def _format_usage(self, usage, actions, groups, prefix):
        return super(CustomHelpFormatter, self)._format_usage(usage, actions, groups, 'Usage: ')


def add_deploy_cmd(subparsers):
    """ Add the parser for the "deploy" command."""
    cmd_parser = subparsers.add_parser('deploy', help='Deploy a package and publish "unstable" distribution')
    cmd_parser.add_argument('repo_name', help='The name of the APT repo - e.g. pizza/pizza4/trusty')
    cmd_parser.add_argument('package_file', nargs='?',
                            help='Package file to deploy - e.g. ./pizza_1.2.deb.  If omitted, just re-publish')
    cmd_parser.add_argument('-g', '--gpg-key', dest='gpg_key',
                            help='Public GPG key to use for signing on the server')
    cmd_parser.add_argument('-d', '--distribution', default='unstable',
                            help='Distribution name - default "unstable"')
    cmd_parser.set_defaults(func=run_remote_cmd)


def add_undeploy_cmd(subparsers):
    """ Add the parser for the "undeploy" command."""
    cmd_parser = subparsers.add_parser('undeploy', help='Un-deploy a package from "unstable" distribution')
    cmd_parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true', help='Just show what would happen')
    cmd_parser.set_defaults(dry_run=False)
    cmd_parser.add_argument('repo_name', help='The name of the APT repo - e.g. pizza/pizza4/trusty')
    cmd_parser.add_argument('packages', help='Packages to remove from unstable - a non-urlencoded Aptly package query')
    cmd_parser.set_defaults(func=run_remote_cmd)


def add_test_cmd(subparsers):
    """ Create the parser for the "test" command."""
    cmd_parser = subparsers.add_parser('test', help='Put a candidate release into "testing".')
    cmd_parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true', help='Just show what would happen')
    cmd_parser.set_defaults(dry_run=False)
    # package_query
    cmd_parser.add_argument('-p', '--packages',
                            help='Add packages from unstable - a non-urlencoded Aptly package query')
    cmd_parser.add_argument('repo_name', help='The name of the APT repo - e.g. pizza/pizza4/trusty')
    cmd_parser.add_argument('release_id',
                            help='The unique identifier of this candidate release - e.g. Jira ticket')
    cmd_parser.set_defaults(func=run_remote_cmd)


def add_stage_cmd(subparsers):
    """ Create the parser for the "stage" command."""
    cmd_parser = subparsers.add_parser('stage', help='Stage packages in "staging"')
    cmd_parser.add_argument('repo_name', help='The name of the APT repo - e.g. pizza/pizza4/trusty')
    cmd_parser.add_argument('release_id', help='The unique identifier of the release - e.g. Jira ticket')
    cmd_parser.set_defaults(func=run_remote_cmd)


def add_release_cmd(subparsers):
    """ Create the parser for the "release" command."""
    cmd_parser = subparsers.add_parser('release', help='Release packages to "stable"')
    cmd_parser.add_argument('repo_name', help='The name of the APT repo - e.g. pizza/pizza4/trusty')
    cmd_parser.add_argument('release_id', help='The unique identifier of the release - e.g. Jira ticket')
    cmd_parser.set_defaults(func=run_remote_cmd)


def add_aptly_version_cmd(subparsers):
    """ Create the parser for the "aptly API version" command."""
    cmd_parser = subparsers.add_parser('version', help='Show client and Aptly server version')
    cmd_parser.add_argument('-j', '--json', dest='json', action='store_true', help='Print result as json')
    cmd_parser.set_defaults(json=False)
    cmd_parser.set_defaults(func=run_remote_cmd)


def add_show_cmd(subparsers):
    """ Create the parser for the "aptly show" command."""
    cmd_parser = subparsers.add_parser('show', help='Show repository details')
    cmd_parser.add_argument('repo_name', nargs='?', help='The name of the APT repo - e.g. pizza/pizza4/trusty')
    cmd_parser.add_argument('distribution', nargs='?', help='The name of the distribution to show')
    cmd_parser.add_argument('-j', '--json', dest='json', action='store_true', help='Print result as json')
    cmd_parser.set_defaults(json=False)
    cmd_parser.set_defaults(func=run_remote_cmd)


def add_create_cmd(subparsers):
    """ Create the parser for the "aptly create" command"""
    cmd_parser = subparsers.add_parser('create', help='Create a repository')
    cmd_parser.add_argument('repo_name', help='The name of the APT repo - e.g. pizza/pizza4/trusty')
    cmd_parser.set_defaults(func=run_remote_cmd)


def create_cmd_parsers():
    """ Create the command parsers."""

    # Create top level parser
    cmd_parser = argparse.ArgumentParser(prog='raptly', add_help=False,
                                         epilog='Raptly w\033[92mr\033[0maps \033[92maptly\033[0m! \n  https://www.aptly.info/',
                                         formatter_class=CustomHelpFormatter)

    # Create sub-parsers for commands
    subparsers = cmd_parser.add_subparsers(title='Commands', metavar='<command>', dest='command')
    add_create_cmd(subparsers)
    add_deploy_cmd(subparsers)
    add_undeploy_cmd(subparsers)
    add_test_cmd(subparsers)
    add_stage_cmd(subparsers)
    add_release_cmd(subparsers)
    add_aptly_version_cmd(subparsers)
    add_show_cmd(subparsers)

    # Top level Options
    options_group = cmd_parser.add_argument_group('Options')
    options_group.add_argument('--url', dest='url',
                               help='The URL of the Aptly API - override default value set in ~/.raptly/config')
    options_group.add_argument('-h', '--help', action='help', help='Show help message and exit')
    options_group.add_argument('--version', action='version', version='%(prog)s version: ' + __version__,
                               help='Show %(prog)s version')
    options_group.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                               help='Print additional logging')
    options_group.set_defaults(verbose=False)
    options_group.add_argument('-k', '--skip-ssl', dest='skip_ssl', action='store_true',
                               help='Skip server SSL verification')

    # SSL auth group
    auth_group = cmd_parser.add_argument_group('SSL auth',
                                               'Provide client private key and CA signed client cert')
    auth_group.add_argument('--key', help='Client key')
    auth_group.add_argument('--cert', help='Client certificate')

    # Basic auth group
    basic_auth_group = cmd_parser.add_argument_group('Basic auth',
                                                     'Provide HTTP basic auth in the form: <username:password>')
    basic_auth_group.add_argument('-u', '--user', help='Basic Auth credentials', default=':')

    return cmd_parser


def repo_list_cmd(url, args, key, cert):
    """Print repositories to stdout."""

    repos = get_api(args=args, url=url, key=key, cert=cert).list_published_repos()

    if args.json:
        print json.dumps(repos)
    else:
        # Print out one repo name per line
        print("Repositories:")
        for repo in repos:
            print "  %s" % repo


def dist_list_cmd(url, args, key, cert):
    """Print distributions to stdout."""

    dists = get_api(args=args, url=url, key=key, cert=cert).list_distributions(public_repo_name=args.repo_name)

    if args.json:
        print json.dumps(dists)
    else:
        # Print out one distribution name per line
        print("Distributions:")
        for dist in dists:
            sys.stdout.write("  %s -> " % dist['Distribution'])
            for source in dist['Sources']:
                sys.stdout.write("%s " % source['Name'])
            print("")


def deploy_cmd(args, url, key, cert):
    """Deploy package to unstable distribution."""

    api = get_api(args=args, url=url, key=key, cert=cert)

    if args.package_file is not None:
        # Deploy the package and re-publish
        api.deploy(public_repo_name=args.repo_name, package_file=args.package_file,
                   gpg_key=args.gpg_key, unstable_dist_name=args.distribution)
        print('Package deployed:')
    else:
        # No package file, just re-publish
        api.republish_unstable(unstable_dist_name=args.distribution, public_repo_name=args.repo_name,
                               gpg_public_key_id=args.gpg_key)

    show(api, False, args.repo_name, 'unstable')


def undeploy_cmd(args, url, key, cert):
    """Un-deploy a package from unstable distribution."""

    api = get_api(args=args, url=url, key=key, cert=cert)

    unstable_dist_name = 'unstable'

    deleted_packages = api.undeploy(public_repo_name=args.repo_name, package_query=args.packages,
                                    unstable_dist_name=unstable_dist_name, dry_run=args.dry_run)

    if len(deleted_packages) <= 0:
        print("Query matched no packages: nothing to do")
        return

    if args.dry_run:
        print('Matching packages (dry run - no action taken):')
    else:
        print('Deleted packages:')

    aptly_api.print_package_refs(deleted_packages)


def test_cmd(args, url, key, cert):
    """Release package to testing distribution."""

    api = get_api(args=args, url=url, key=key, cert=cert)

    unstable_distribution_name = 'unstable'
    testing_distribution_name = 'testing'
    stable_distribution_name = 'stable'
    public_repo_name = args.repo_name

    union, new_packages, snapshot_release_candidate = api.test(public_repo_name=public_repo_name,
                                                               package_query=args.packages,
                                                               release_id=args.release_id,
                                                               unstable_distribution_name=unstable_distribution_name,
                                                               testing_distribution_name=testing_distribution_name,
                                                               stable_distribution_name=stable_distribution_name,
                                                               dry_run=args.dry_run)
    if len(union) <= 0:
        print("No packages: nothing to do")
        return

    if len(new_packages) <= 0:
        print("No new packages:")

    print('Test candidate %s:' % args.release_id)
    print('Snapshot: %s' % ('(dry run - none created)' if args.dry_run else snapshot_release_candidate))
    print('Repository: %s' % public_repo_name)
    print('Distribution: %s' % testing_distribution_name)
    print('Packages:')
    aptly_api.print_package_refs(union)
    # show(api, False, args.repo_name, 'testing')


def stage_cmd(args, url, key, cert):
    """Release package to staging distribution."""

    api = get_api(args=args, url=url, key=key, cert=cert)
    api.stage(public_repo_name=args.repo_name, testing_distribution_name='testing',
              staging_distribution_name='staging', release_id=args.release_id)
    print('Staged release %s:' % args.release_id)
    show(api, False, args.repo_name, 'staging')


def release_cmd(args, url, key, cert):
    """Release package to stable distribution."""

    api = get_api(args=args, url=url, key=key, cert=cert)
    api.release(public_repo_name=args.repo_name, staging_distribution_name='staging',
                stable_distribution_name='stable', release_id=args.release_id)
    print('Released %s to stable:' % args.release_id)
    show(api, False, args.repo_name, 'stable')


def get_api(args, url, key, cert):
    return AptlyApi(url.rstrip("/"), args.verbose, args.skip_ssl, args.user, key, cert)


def version_cmd(args, url, key, cert):
    """Print version to stdout
    :param args: Command line arguments.
    """

    print('raptly version: %s' % __version__)

    # Try to get the server version
    try:
        version = get_api(args=args, url=url, key=key, cert=cert).version()
        if args.json:
            print json.dumps(version)
        else:
            print 'server version: %s' % version['Version']
    except Exception as e:
        print('server version: (no connection)')


def create_cmd(args, url, key, cert):
    """Create a repository
    :param args: Command line arguments.
    """
    api = get_api(args=args, url=url, key=key, cert=cert)
    api.create(public_repo_name=args.repo_name, unstable_distribution_name='unstable')


def run_remote_cmd(args):
    """Dispatch command based on args.command"""

    # TODO - use values in config file
    config_filename = os.path.expanduser('~/.raptly/config')
    config = None
    if os.path.isfile(config_filename):
        with open(config_filename) as config_file:
            config = toml.loads(config_file.read())

    key = get_key(args, config)
    cert = get_cert(args, config)
    url = get_url(args, config)
    if url is None:
        print('Please set Aptly server URL in the config file ~/.raptly/config or by using --url option')
        return

    if args.command == 'show':
        show_cmd(args=args, url=url, key=key, cert=cert)
    if args.command == 'create':
        create_cmd(args=args, url=url, key=key, cert=cert)
    if args.command == 'deploy':
        deploy_cmd(args=args, url=url, key=key, cert=cert)
    if args.command == 'undeploy':
        undeploy_cmd(args=args, url=url, key=key, cert=cert)
    if args.command == 'test':
        test_cmd(args=args, url=url, key=key, cert=cert)
    if args.command == 'stage':
        stage_cmd(args=args, url=url, key=key, cert=cert)
    if args.command == 'release':
        release_cmd(args=args, url=url, key=key, cert=cert)
    if args.command == 'version':
        version_cmd(args=args, url=url, key=key, cert=cert)


def show_cmd(url, args, key, cert):
    """Print packages to stdout
    :param url: URL of backend Aptly API
    :param args: Command line arguments
    """

    # If no repo name specified list all published repos
    if args.repo_name is None:
        repo_list_cmd(url=url, args=args, key=key, cert=cert)
        return

    # If no distribution name specified list all distributions for the specified repo
    if args.distribution is None:
        dist_list_cmd(url=url, args=args, key=key, cert=cert)
        return

    # If both repo name a distribution specified show the whole works
    api = get_api(args=args, url=url, key=key, cert=cert)
    show(api, args.json, public_repo_name=args.repo_name, distribution=args.distribution)


def show(api, is_json, public_repo_name, distribution):
    matching_publication = api.get_publication(public_repo_name=public_repo_name, distribution=distribution)

    if matching_publication is None:
        raise aptly_api.RaptlyError('Distribution not found: %s %s' % (public_repo_name, distribution))

    print('Prefix:       %s' % matching_publication['Prefix'])
    print('Distribution: %s' % matching_publication['Distribution'])
    print('Source:')
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
    sorted_by_version = sorted(unsorted, key=aptly_api.pkg_ref_version_key(compare_versions))
    sorted_by_name = sorted(sorted_by_version, key=lambda pr: pr[1:].split()[1])
    if is_json:
        print json.dumps(sorted_by_name)
    else:
        # Print out one package name per line
        aptly_api.print_package_refs(sorted_by_name)


def get_param_value(param_name, args, config):
    """Get value of a named command parameter either from args or from config.
    """
    param_val = None
    # If param_name is available in config use it
    if config and config.get('default', None) and config['default'].get(param_name, None):
        param_val = config['default'][param_name]

    # If param_name option is available in args, override the value from config
    if args and vars(args)[param_name]:
        param_val = vars(args)[param_name]

    return param_val


def get_cert(args, config):
    """Get cert file name from args / config.
    """
    return get_param_value('cert', args, config)


def get_key(args, config):
    """Get key file name from args / config.
    """
    return get_param_value('key', args, config)


def get_url(args, config):
    """Get key file from args and config.
    """
    return get_param_value('url', args, config)