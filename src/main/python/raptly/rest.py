import requests


class Rest:
    """
    Rest calls
    """

    def __init__(self, cert, auth, verify):
        self.cert = cert
        self.auth = auth
        self.verify = verify

    def do_get(self, url):
        """Execute GET request on specified URL.
        :param url: The URL to make the GET request on.
        """
        return requests.get(url, cert=self.cert, auth=self.auth, verify=self.verify)

    def do_delete(self, url, data=None, headers=None):
        """Execute DELETE request on specified URL.
        :param data:
        :param headers:
        :param url: The URL to make the DELETE request on.
        """
        return requests.delete(url, cert=self.cert, auth=self.auth, verify=self.verify, data=data, headers=headers)

    def do_post(self, url, files=None, data=None, headers=None):
        """Execute POST request on specified URL.
        :param url: The URL to make the GET request on.
        :param files: List of files to upload in the POST.
        :param data: Post data.
        :param headers: Request headers.
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
