# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from traceback import format_exc


REQUESTS_IMP_ERR = None
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = format_exc()
    HAS_REQUESTS = False


def copy_entries(src, dest, entries, copy_empty=True):
    for entry in entries:
        if entry in src or copy_empty:
            dest[entry] = src.get(entry, None)


def set_not_none(dest, key, val):
    if val is not None:
        dest[key] = val


class JsonRestApiClient(object):
    def __init__(self, protocol, host, port, username, password, validate_certs=True, proxy=None):
        if not HAS_REQUESTS:
            raise ImportError(
                self.__class__.__name__ + ": requires Python Requests 1.1.0 or higher: https://github.com/psf/requests."
            )
        self.base_url = "{0}://{1}:{2}".format(
            protocol,
            host,
            port,
        )
        self.username = username
        self.password = password
        self.validate_certs = validate_certs
        if proxy:
            self.proxies = {"http": proxy, "https": proxy}
        else:
            self.proxies = None

    def get_headers(self):
        return {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        }

    def get_auth(self):
        return None

    def get_proxies(self):
        return self.proxies

    def get_request(self, uri_path, timeout=None):
        return self._execute_request(
            "GET",
            uri_path,
            headers=self.get_headers(),
            auth=self.get_auth(),
            proxies=self.get_proxies(),
            verify=self.validate_certs,
            timeout=timeout,
        )

    def post_request(self, uri_path, data, timeout=None):
        return self._execute_request(
            "POST",
            uri_path,
            headers=self.get_headers(),
            auth=self.get_auth(),
            proxies=self.get_proxies(),
            verify=self.validate_certs,
            data=data,
            timeout=timeout,
        )

    def put_request(self, uri_path, data, timeout=None):
        return self._execute_request(
            "PUT",
            uri_path,
            headers=self.get_headers(),
            auth=self.get_auth(),
            proxies=self.get_proxies(),
            verify=self.validate_certs,
            data=data,
            timeout=timeout,
        )

    def delete_request(self, uri_path, data=None, timeout=None):
        return self._execute_request(
            "DELETE",
            uri_path,
            headers=self.get_headers(),
            auth=self.get_auth(),
            proxies=self.get_proxies(),
            verify=self.validate_certs,
            data=data,
            timeout=timeout,
        )

    def head_request(self, uri_path, timeout=None):
        return self._execute_request(
            "HEAD",
            uri_path,
            headers=self.get_headers(),
            auth=self.get_auth(),
            proxies=self.get_proxies(),
            verify=self.validate_certs,
            timeout=timeout,
        )

    def patch_request(self, uri_path, data=None, timeout=None):
        return self._execute_request(
            "PATCH",
            uri_path,
            headers=self.get_headers(),
            auth=self.get_auth(),
            proxies=self.get_proxies(),
            verify=self.validate_certs,
            data=data,
            timeout=timeout,
        )

    def _execute_request(
        self, verb, uri_path, headers=None, auth=None, proxies=None, verify=True, data=None, timeout=None
    ):
        url = "{0}{1}".format(self.base_url, uri_path)
        r = requests.request(
            verb, url=url, headers=headers, auth=auth, verify=verify, json=data, timeout=timeout, proxies=proxies
        )
        if r.ok:
            if r.headers.get("Content-Type") and r.headers.get("Content-Type").startswith("application/json"):
                return r.json()
        else:
            r.raise_for_status()
