import time
import re

import json
import os
import urllib

import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from debian_version import compare_versions


class RaptlyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AptlyApiError(Exception):
    def __init__(self, value, msg):
        self.value = value
        self.msg = msg

    def __str__(self):
        return repr(self.value)


def pkg_ref_version_key(mycmp):
    """Convert a cmp= function into a key= function, to prepare for Python 3's removal of cmp= style comparator"""

    class K:
        def __init__(self, obj, *args):
            self.obj = obj.split()[2]

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return K


def get_timestamp():
    return int(time.time())


def local(public_repo_name):
    """Return local form of public repo name.
    Aptly REST API interprets '_' as '/' in repo names.
    :param public_repo_name: The name of the repo (e.g. zonza/zonza4/trusty)
    """
    return public_repo_name.replace('/', '_')


class AptlyApi:
    """Class that wraps calls to Aptly's REST API """

    def __init__(self, repo_url, verbose=False, skip_ssl=False, user=':', key=None, cert=None):
        self.repo_url = repo_url
        self.aptly_api_base_url = repo_url
        self.verbose = verbose
        self.verify = not skip_ssl
        self.user = user
        self.headers = {}
        (self.username, self.password) = user.split(':')
        self.auth = HTTPBasicAuth(self.username, self.password)
        if cert:
            cert = os.path.expanduser(cert)
            if not os.path.exists(cert):
                raise RaptlyError('Cert file %s does not exist' % cert)
        if key:
            key = os.path.expanduser(key)
            if not os.path.exists(key):
                raise RaptlyError('Key file %s does not exist' % key)
        self.cert = (cert, key)
        # Suppress SSL warnings for self-signed certificates
        requests.packages.urllib3.disable_warnings()

    def drop_published_distribution(self, base_url, local_repo_name, distribution):
        """Drop a published distribution.
        :param base_url: The base API url (e.g. https://repo.hogarthww.com/aptly/api)
        :param local_repo_name: The local name of the repo (e.g. zonza_zonza4_trusty)
        :param distribution: The distribution name (e.g. unstable | testing | stable)
        """
        r = self.do_delete('%s/publish/%s/%s' % (base_url, local_repo_name, distribution))
        if r.status_code != requests.codes.ok:
            raise AptlyApiError(r.status_code, '[HTTP %s] - Failed to drop published distribution: %s from: %s'
                                % (r.status_code, distribution, local_repo_name))

    def publish_snapshot(self, base_url, distribution, gpg_public_key_id, snapshot_name, repo_name):
        """Publish a snapshot.
        :param base_url: The base API url (e.g. https://repo.hogarthww.com/aptly/api)
        :param snapshot_name: The name of the snapshot to publish
        :param distribution: The distribution name (e.g. unstable | testing | stable)
        :param gpg_public_key_id: The GPG key the server will use to sign packages with
        :param repo_name: The name of the repo (e.g. zonza/zonza4/trusty)
        """
        payload = {'Signing': {'GpgKey': gpg_public_key_id},
                   'SourceKind': 'snapshot',
                   'Sources': [{'Name': snapshot_name}],
                   'Architectures': ['amd64', 'all'],
                   'Distribution': distribution}
        headers = {'content-type': 'application/json'}
        r = self.do_post('%s/publish//%s' % (base_url, repo_name), data=json.dumps(payload), headers=headers)
        if r.status_code != 201:
            raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                % ('Failed to publish unstable snapshot', r.status_code))

    def drop_snapshot(self, snapshot_name):
        """Drop a snapshot.
         The quivalent cURL command: curl -v -X DELETE 'http://repo:8080/api/snapshots/snapshot-name?force=1'
        :param snapshot_name: Name of the snapshot to drop
        """
        delete_snapshot_url = ('%s/snapshots/' + snapshot_name + '?force=1') % self.aptly_api_base_url
        if self.verbose:
            print('Deleting snapshot: %s' % delete_snapshot_url)

        r = self.do_delete(delete_snapshot_url)

        if (r.status_code != requests.codes.ok) and (r.status_code != requests.codes.not_found):
            raise AptlyApiError(r.status_code, '[HTTP %s] - Failed to delete snapshot: %s'
                                % (r.status_code, delete_snapshot_url))

    def filter_packages(self, package_query, snapshot_name):

        urlencoded_query = urllib.urlencode({'q': package_query})

        filter_snapshot_url = '%s/snapshots/%s/packages?%s' % (self.aptly_api_base_url, snapshot_name, urlencoded_query)

        r = self.do_get(filter_snapshot_url)
        if self.verbose:
            print('Filtering snapshot of unstable: %s' % filter_snapshot_url)

        if r.status_code != requests.codes.ok:
            raise AptlyApiError(r.status_code, '[HTTP %s] - Failed to filter package: %s in snapshot: %s'
                                % (r.status_code, package_query, snapshot_name))

        new_packages = r.json()
        return new_packages

    def create_empty_snapshot_for_repo(self, public_repo_name):
        """Create an empty snapshot with the name <public_repo_name>.timestamp
        :param public_repo_name: The public repo name
        """
        snapshot_name = "%s.%s" % (local(public_repo_name), get_timestamp())
        payload = {'Name': snapshot_name}
        headers = {'content-type': 'application/json'}
        r = self.do_post('%s/snapshots' % self.aptly_api_base_url, data=json.dumps(payload), headers=headers)
        if self.verbose:
            print('Creating snapshot %s' % snapshot_name)

        if r.status_code != 201:
            raise AptlyApiError(r.status_code, '[HTTP %s] - Failed to create snapshot: %s'
                                % (r.status_code, snapshot_name))
        return snapshot_name

    def create_snapshot_from_package_refs(self, package_refs, source_snapshots, target_snapshot_name):
        """Create a snapshot from the source snapshots, filtering for the specified package refs.
        :param package_refs: The refs of the required packages
        :param source_snapshots: The source snapshots to filter packages from
        :param target_snapshot_name: The name of the snapshot that will be created
        """
        payload = {'Name': target_snapshot_name,
                   'SourceSnapshots': source_snapshots,
                   'Description': target_snapshot_name,
                   'PackageRefs': package_refs}
        headers = {'content-type': 'application/json'}
        r = self.do_post('%s/snapshots' % self.aptly_api_base_url, data=json.dumps(payload), headers=headers)
        if self.verbose:
            print('Creating snapshot %s' % target_snapshot_name)

        if r.status_code != 201:
            raise AptlyApiError(r.status_code, '[HTTP %s] - Failed to create snapshot: %s'
                                % (r.status_code, target_snapshot_name))

    def do_delete(self, url, data=None, headers=None):
        """Execute DELETE request on specified URL.
        :param data:
        :param headers:
        :param url: The URL to make the DELETE request on.
        """
        return requests.delete(url, cert=self.cert, auth=self.auth, verify=self.verify, data=data, headers=headers)

    def do_get(self, url):
        """Execute GET request on specified URL.
        :param url: The URL to make the GET request on.
        """
        return requests.get(url, cert=self.cert, auth=self.auth, verify=self.verify)

    def do_post(self, url, files=None, data=None, headers=None):
        """Execute POST request on specified URL.
        :param files: List of files to upload in the POST.
        :param url: The URL to make the GET request on.
        """
        return requests.post(url, cert=self.cert, auth=self.auth, verify=self.verify, data=data, headers=headers,
                             files=files)

    def do_put(self, url, data, headers):
        """Execute PUT request on specified URL.
        :param url: The URL to make the GET request on.
        :param data: Data payload of the PUT request.
        :param headers: Headers for the HTTP request.
        """
        return requests.put(url, data=data, headers=headers, cert=self.cert, auth=self.auth, verify=self.verify)

    def pkg_list(self, public_repo_name, distribution):
        """Return the list of packages in the specified repo and distribution."""

        if self.verbose:
            print('Listing packages from repo: %s in distribution: %s' % (public_repo_name, distribution))

        matching_publication = self.get_publication(distribution, public_repo_name)

        return self.get_packages(matching_publication)

    def query_packages(self, public_repo_name, distribution_name, package_query):
        """Return list of matching packages in the specified repo/distribution or empty list if no match
        :param public_repo_name: The name of the APT repo
        :param distribution_name: The distribution within the repo
        :param package_query: Aptly package query
        """

        if self.verbose:
            print('Listing packages from repo: %s in distribution: %s, q="%s"' % (public_repo_name, distribution_name,
                                                                                  package_query))

        # Get the snapshot source of the unstable distribution
        snapshot_name = self.get_snapshot_for_publication(distribution=distribution_name,
                                                          public_repo_name=public_repo_name)

        return self.filter_packages(package_query, snapshot_name)

    def get_packages(self, publication):
        """Return the list of packages for the specified publication."""
        sources = publication['Sources']
        packages = []
        if publication['SourceKind'] == 'snapshot':
            for source in sources:
                source_name = source['Name']
                packages += self.get_packages_from_snapshot(source_name)
        elif publication['SourceKind'] == 'local':
            for source in sources:
                source_name = source['Name']
                packages += self.get_packages_from_local_repo(source_name)
        else:
            pass

        return packages

    def get_snapshots(self):
        """Get all snapshots, sorted in order of creation"""

        # Get all snapshots on the system
        snapshots_rest_url = '%s/snapshots?sort=time' % self.aptly_api_base_url
        r = self.do_get(snapshots_rest_url)
        if r.status_code != requests.codes.ok:
            raise AptlyApiError(r.status_code,
                                'Aptly API Error - %s - HTTP Error: %s' % (snapshots_rest_url, r.status_code))
        return r.json()

    def find_release_candidate_snapshots(self, local_repo_name, release_id):
        """Find snapshot release candidates matching the form local_repo_name.release_id.*"""
        snapshots = self.get_snapshots()
        pattern = re.compile('%s\.%s\..*' % (local_repo_name, release_id))
        matching_snapshots = [x for x in snapshots if pattern.match(x['Name'])]
        return matching_snapshots

    def get_snapshot_for_publication(self, distribution, public_repo_name):
        """Get the single snapshot published by the specified distribution public repo name.
        Throw RaptlyError if there is *not* a single snapshot source for the published repo and distribution.
        :param public_repo_name: The published repo name
        :param distribution: The distribution
        """

        publication = self.get_publication(distribution, public_repo_name)

        if publication['SourceKind'] != 'snapshot':
            raise RaptlyError('%s %s not published from snapshot' % (public_repo_name, distribution))

        if len(publication['Sources']) < 1:
            raise RaptlyError('No source found for publication %s %s' % (public_repo_name, distribution))

        if len(publication['Sources']) > 1:
            raise RaptlyError('More than one source found for publication %s %s' % (public_repo_name, distribution))

        return publication['Sources'][0]['Name']

    def get_publication(self, distribution, public_repo_name):
        """Get the publication for the specified distribution and public repo name.
        :param public_repo_name: The published repo name
        :param distribution: The distribution
        """

        publications = self.get_publications()
        matching_publications = [x for x in publications if x['Prefix'] == public_repo_name
                                 if x['Distribution'] == distribution]
        if len(matching_publications) > 0:
            return matching_publications[0]
        else:
            return None

    def get_publications(self):
        """Get the published repos and snapshots. """

        # Get all publications - i.e. published repos/snapshots
        publications_rest_url = '%s/publish' % self.aptly_api_base_url
        r = self.do_get(publications_rest_url)
        if r.status_code != requests.codes.ok:
            raise AptlyApiError(r.status_code,
                                'Aptly API Error - %s - HTTP Error: %s' % (publications_rest_url, r.status_code))
        return r.json()

    def get_packages_from_local_repo(self, local_repo_name):
        packages_rest_url = '%s/repos/%s/packages' % (self.aptly_api_base_url, local_repo_name)
        r = self.do_get(packages_rest_url)
        if r.status_code != requests.codes.ok:
            raise AptlyApiError(r.status_code,
                                'Aptly API Error - %s - HTTP Error: %s' % (packages_rest_url, r.status_code))
        return r.json()

    def get_packages_from_snapshot(self, snapshot_name):
        packages_rest_url = '%s/snapshots/%s/packages' % (self.aptly_api_base_url, snapshot_name)
        r = self.do_get(packages_rest_url)
        if r.status_code != requests.codes.ok:
            raise AptlyApiError(r.status_code,
                                'Aptly API Error - %s - HTTP Error: %s' % (packages_rest_url, r.status_code))
        return r.json()

    def list_distributions(self, public_repo_name):
        """Return the list of published distributions on the Aptly server."""
        publications = self.get_publications()
        publications_for_repo = [x for x in publications if x['Prefix'] == public_repo_name]
        return sorted(publications_for_repo)

    def list_published_repos(self):
        """Return the list of published repositories on the Aptly server."""

        repos_url = '%s/publish' % self.aptly_api_base_url

        if self.verbose:
            print('Listing repos at: %s' % repos_url)

        r = self.do_get(repos_url)

        # Create a distinct list of publications
        if r.status_code == requests.codes.ok:
            publications = r.json()
            return sorted(set([x['Prefix'] for x in publications]))
        else:
            raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s' % (repos_url, r.status_code))

    def version(self):
        """Report the Aptly API version. """

        version_url = '%s/version' % self.aptly_api_base_url

        if self.verbose:
            print('Getting API version from: %s' % version_url)

        r = self.do_get(version_url)

        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s' % (version_url, r.status_code))

    def repo_create(self):
        pass

    def undeploy(self, public_repo_name, package_query, unstable_dist_name, dry_run):
        """Un-deploy a package from the unstable distribution.
        :param public_repo_name: The name of the repository to un-deploy from
        :param package_query: Aptly query defining the package(s) to un-deploy
        :param unstable_dist_name: The name of the `unstable` distribution
        """
        package_refs = self.query_packages(public_repo_name=public_repo_name, distribution_name=unstable_dist_name,
                                           package_query=package_query)

        if dry_run is False:
            retval = self.delete_packages(public_repo_name=public_repo_name, package_refs=package_refs)
            self.republish_unstable(unstable_dist_name, None, public_repo_name)

        return package_refs

    def deploy(self, public_repo_name, package_file, gpg_key, unstable_dist_name):
        """Deploy a Debian package to the specified distribution.
        :param public_repo_name: The name of the repository to deploy to
        :param package_file: The Debian package file to deploy
        :param gpg_key: The fingerprint of the GPG key used by the server to sign packages
        :param unstable_dist_name: The name of the `unstable` distribution
        """

        gpg_public_key_id = gpg_key
        upload_url_component = '/files'
        repos_url_component = '/repos'
        upload_dir = '/myfiles'
        upload_file_url = '%s%s%s' % (self.aptly_api_base_url, upload_url_component, upload_dir)
        deb_file_basename = os.path.basename(package_file)

        if self.verbose:
            print('Deploying package: %s to %s %s %s' % (deb_file_basename, self.aptly_api_base_url,
                                                         local(public_repo_name), unstable_dist_name))

        # Upload the package to the server's file system
        files = {'file': open(package_file, 'rb')}

        if self.verbose:
            print('Uploading file to Aptly server at: %s' % upload_file_url)

        r = self.do_post(upload_file_url, files=files)

        if r.status_code != requests.codes.ok:
            raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s' % ('Failed to upload file',
                                                                                          r.status_code))

        # Add the uploaded package file to the repo
        add_package_to_repo_url = '%s%s/%s/file%s/%s' \
                                  % (self.aptly_api_base_url, repos_url_component,
                                     local(public_repo_name), upload_dir, deb_file_basename)
        if self.verbose:
            print('Adding file: %s to repo %s' % (add_package_to_repo_url, local(public_repo_name)))

        r = self.do_post(add_package_to_repo_url)
        if r.status_code != requests.codes.ok:
            raise AptlyApiError(r.status_code, '[HTTP %s] - Failed to add uploaded file to repo: %s'
                                % (r.status_code, local(public_repo_name)))

        # Snapshot the repo unstable distribution and re-publish
        self.republish_unstable(unstable_dist_name, gpg_public_key_id, public_repo_name)

    def republish_unstable(self, unstable_dist_name, gpg_public_key_id, public_repo_name):
        # Drop any pre-existing publication of the unstable distribution
        if self.get_publication(distribution=unstable_dist_name, public_repo_name=public_repo_name):
            self.drop_published_distribution(self.aptly_api_base_url,
                                             local_repo_name=local(public_repo_name),
                                             distribution=unstable_dist_name)

        # Drop and re-create a dedicated snapshot from the local repo and publish
        # The format of the snapshot name is: <local_repo_name>.<timestamp>
        local_repo_snapshot_name = '%s.%s' % (local(public_repo_name), get_timestamp())

        # Re-create the snapshot of the local repo
        # curl -X POST -H 'Content-Type: application/json' --data '{"Name":"<local-repo-name>-snap-<distribution>"}'
        #     http://repo:8080/api/repos/a4pizza/snapshots
        #
        create_snapshot_url = '%s/repos/%s/snapshots' % (self.aptly_api_base_url, local(public_repo_name))
        if self.verbose:
            print('Creating snapshot: %s' % create_snapshot_url)
        payload = {'Name': local_repo_snapshot_name}
        headers = {'content-type': 'application/json'}
        r = self.do_post(create_snapshot_url, data=json.dumps(payload), headers=headers)
        if r.status_code != 201:
            raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                % ('Failed to publish unstable distribution of repo: %s' % public_repo_name,
                                   r.status_code))

        #
        # Re-publish <local-repo-name>-snap-<distribution> as distribution 'unstable'
        #
        self.publish_snapshot(self.aptly_api_base_url, unstable_dist_name, gpg_public_key_id, local_repo_snapshot_name,
                              local(public_repo_name))

    def test(self, public_repo_name, package_query, release_id, unstable_distribution_name, testing_distribution_name,
             stable_distribution_name, dry_run):
        """Create a test candidate, promoting the specified package to the testing distribution.
        :param public_repo_name: The name of the repository to deploy to (e.g. zonza/zonza4/trusty)
        :param package_query: New packages to add.  A non-urlencoded Aptly package query.
        :param release_id: A unique ID for the test candidate (e.g. JIRA ticket number)
        :param unstable_distribution_name: The name used for the unstable distribution (e.g. 'unstable')
        :param testing_distribution_name: The name used for the testing distribution (e.g. 'testing')
        :param stable_distribution_name: The name used for the stable distribution (e.g. 'stable')
        :param dry_run: If True, just show what would happen.
        """

        # Get list of packages from stable distribution if it exists
        stable_packages = []
        stable_publication = self.get_publication(stable_distribution_name, public_repo_name)
        if stable_publication is not None:
            stable_packages = self.get_packages(stable_publication)

        # Check for pre-existing release candidate with matching release_id sort by latest in case of > 1
        matching_releases = sorted(self.find_release_candidate_snapshots(local(public_repo_name), release_id),
                                   reverse=True)
        # If there is a matching release candidate
        if len(matching_releases) > 0:
            # Prohibit any attempt to modify this release
            if package_query is not None:
                raise RaptlyError('Cannot modify existing release "%s"' % release_id)

            # Publish existing release as testing.  Use most recent if > 1
            existing_release = matching_releases[0]['Name']
            self.publish(testing_distribution_name, public_repo_name, existing_release)
            return stable_packages, [], existing_release

        # TODO - Exit if about to replace un-promoted testing - --force to override

        if self.verbose:
            print('Creating release candidate from packages: %s to %s' % (package_query, self.aptly_api_base_url))

        # Get the snapshot source of the unstable distribution
        unstable_snapshot_name = self.get_snapshot_for_publication(distribution=unstable_distribution_name,
                                                                   public_repo_name=public_repo_name)

        # Create list of new packages to add to what's already in stable
        new_packages = []
        if package_query is not None:
            # Use the query to get list of matching packages from unstable
            matching_packages = self.filter_packages(package_query, unstable_snapshot_name)

            # Filter out any packages that are already released in stable
            new_packages = [x for x in matching_packages if x not in stable_packages]

        # Create the union of new + stable
        union = stable_packages + new_packages

        snapshot_release_candidate = None
        # Nothing to do if there are no packages or dry-run requested
        if not dry_run and len(union) > 0:

            # Drop and re-create a temporary snapshot from the list of new packages
            temp_new_pkgs_snapshot_name = '%s-snap-temp-new-pkgs' % local(public_repo_name)
            self.drop_snapshot(temp_new_pkgs_snapshot_name)
            self.create_snapshot_from_package_refs(new_packages, [unstable_snapshot_name], temp_new_pkgs_snapshot_name)

            # Drop and re-create a testing snapshot containing the union
            snapshot_release_candidate = '%s.%s.%s' % (local(public_repo_name), release_id, get_timestamp())
            self.create_snapshot_from_package_refs(union, [temp_new_pkgs_snapshot_name], snapshot_release_candidate)

            # Publish / Re-publish the testing distribution

            # Check if testing exists
            testing_publication = self.get_publication(testing_distribution_name, public_repo_name)
            if testing_publication is None:
                # Publish the release candidate snapshot
                payload = {'SourceKind': 'snapshot',
                           'Sources': [{'Name': snapshot_release_candidate}],
                           'Architectures': ['amd64', 'all'],
                           'Distribution': testing_distribution_name}
                headers = {'content-type': 'application/json'}
                r = self.do_post('%s/publish//%s' % (self.aptly_api_base_url, local(public_repo_name)),
                                 data=json.dumps(payload),
                                 headers=headers)
                if r.status_code != 201:
                    raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                        % ('Failed to publish testing snapshot', r.status_code))
            else:
                # Re-publish the release candidate snapshot
                payload = {'Snapshots': [{'Component': 'main', 'Name': snapshot_release_candidate}]}
                headers = {'content-type': 'application/json'}
                r = self.do_put('%s/publish//%s/%s' % (
                    self.aptly_api_base_url, local(public_repo_name), testing_distribution_name),
                                data=json.dumps(payload), headers=headers)

                if r.status_code != requests.codes.ok:
                    raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                        % ('Failed to promote to testing', r.status_code))

            # Publish / re-publish the destination distribution
            self.publish(dest_distribution_name=testing_distribution_name, public_repo_name=public_repo_name,
                         source_snapshot=snapshot_release_candidate)

        return union, new_packages, snapshot_release_candidate

    def stage(self, public_repo_name, testing_distribution_name, staging_distribution_name, release_id):
        """Promote a release from the testing to the staging distribution.
        :param public_repo_name: The published name of the repository.
        :param release_id: The unique identifier of the release (e.g. JIRA ticket number)
        :param testing_distribution_name: The name of the testing distribution (e.g. 'testing')
        :param staging_distribution_name: The name of the staging distribution (e.g. 'staging')
        """

        self.__promote(public_repo_name=public_repo_name, source_distribution_name=testing_distribution_name,
                       dest_distribution_name=staging_distribution_name, release_id=release_id)

    def release(self, public_repo_name, staging_distribution_name, stable_distribution_name, release_id):
        """Promote a release from the staging to the stable distribution.
        :param public_repo_name: The published name of the repository.
        :param release_id: The unique identifier of the release (e.g. JIRA ticket number)
        :param staging_distribution_name: The name of the staging distribution (e.g. 'staging')
        :param stable_distribution_name: The name of the stable distribution (e.g. 'stable')
        """

        self.__promote(public_repo_name=public_repo_name, source_distribution_name=staging_distribution_name,
                       dest_distribution_name=stable_distribution_name, release_id=release_id)

    def __promote(self, public_repo_name, source_distribution_name, dest_distribution_name, release_id):
        """Promote a release from the source to the destination distribution.
        :param public_repo_name: The published name of the repository.
        :param release_id: The unique identifier of the release (e.g. JIRA ticket number)
        :param source_distribution_name: The distribution to promote from (e.g. 'staging')
        :param dest_distribution_name: The distribution to promote to (e.g. 'stable')
        """

        if self.verbose:
            print('Promoting release %s from %s to %s' % (release_id, source_distribution_name, dest_distribution_name))

        # Get the currently published source
        staging_publication = self.get_publication(distribution=source_distribution_name,
                                                   public_repo_name=public_repo_name)
        # Check the source distribution exists
        if staging_publication is None:
            raise RaptlyError('Cannot promote to %s.  Source distribution %s does not exist.' % (
                dest_distribution_name, source_distribution_name))

        published_source_snapshot = self.get_snapshot_for_publication(distribution=source_distribution_name,
                                                                      public_repo_name=public_repo_name)

        # If the release ID of the source publication doesn't match the specified ID
        pattern = re.compile('.*\.%s\..*' % release_id)
        if not pattern.match(published_source_snapshot):
            raise RaptlyError(
                'Cannot promote release %s.  It is not published as %s.  Please promote to %s first.'
                % (release_id, source_distribution_name, source_distribution_name))

        # Publish / re-publish the destination distribution
        self.publish(dest_distribution_name=dest_distribution_name, public_repo_name=public_repo_name,
                     source_snapshot=published_source_snapshot)

    def publish(self, dest_distribution_name, public_repo_name, source_snapshot):
        """Publish or re-publish the distribution from the source snapshot.
        :param dest_distribution_name: The destination publication.
        :param public_repo_name: The published name of the repository.
        :param source_snapshot: The snapshot to publish.
        """
        # Check if dest distribution already exists
        dest_publication = self.get_publication(dest_distribution_name, public_repo_name)
        if dest_publication is None:
            # Publish the release candidate snapshot
            payload = {'SourceKind': 'snapshot',
                       'Sources': [{'Name': source_snapshot}],
                       'Architectures': ['amd64', 'all'],
                       'Distribution': dest_distribution_name}
            headers = {'content-type': 'application/json'}
            r = self.do_post('%s/publish//%s' % (self.aptly_api_base_url, local(public_repo_name)),
                             data=json.dumps(payload),
                             headers=headers)
            if r.status_code != 201:
                raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                    % ('Failed to promote to %s' % dest_distribution_name, r.status_code))
        else:
            # Re-publish the release candidate snapshot as stable
            payload = {'Snapshots': [{'Component': 'main', 'Name': source_snapshot}]}
            headers = {'content-type': 'application/json'}
            r = self.do_put('%s/publish//%s/%s' % (
                self.aptly_api_base_url, local(public_repo_name), dest_distribution_name),
                            data=json.dumps(payload), headers=headers)

            if r.status_code != requests.codes.ok:
                raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                    % ('Failed to promote to %s' % dest_distribution_name, r.status_code))

    def create(self, public_repo_name, unstable_distribution_name):
        """Create an Aptly local repository
        :param public_repo_name: The published name of the repository
        """
        payload = {'Name': local(public_repo_name),
                   'Comment': '',
                   'DefaultDistribution': '',
                   'DefaultComponent': ''}
        headers = {'content-type': 'application/json'}
        r = self.do_post('%s/repos' % self.aptly_api_base_url,
                         data=json.dumps(payload),
                         headers=headers)
        if r.status_code != 201:
            raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                % ('Failed to create repo %s' % public_repo_name, r.status_code))

        # Create an empty snapshot for this repo
        snapshot_name = self.create_empty_snapshot_for_repo(public_repo_name)

        # Publish the release candidate snapshot
        payload = {'SourceKind': 'snapshot',
                   'Sources': [{'Name': snapshot_name}],
                   'Architectures': ['amd64', 'all'],
                   'Distribution': unstable_distribution_name}
        headers = {'content-type': 'application/json'}
        r = self.do_post('%s/publish//%s' % (self.aptly_api_base_url, local(public_repo_name)),
                         data=json.dumps(payload),
                         headers=headers)
        if r.status_code != 201:
            raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                % ('Failed to publish distribution %s for repo %s' % (
                unstable_distribution_name, public_repo_name), r.status_code))

    def delete_packages(self, public_repo_name, package_refs):
        """Delete packages from an Aptly local repo
        :param public_repo_name: The published name of the repository
        :param package_refs: The packages to delete
        """

        payload = {'PackageRefs': package_refs}
        headers = {'content-type': 'application/json'}
        r = self.do_delete('%s/repos/%s/packages' % (self.aptly_api_base_url, local(public_repo_name)),
                           data=json.dumps(payload),
                           headers=headers)

        if r.status_code != 200:
            raise AptlyApiError(r.status_code, 'Aptly API Error - %s - HTTP Error: %s'
                                % ('Failed to remove packages %s' % package_refs, r.status_code))
