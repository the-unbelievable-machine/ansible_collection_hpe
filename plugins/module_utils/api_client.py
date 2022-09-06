# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from traceback import format_exc
from collections import namedtuple

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible_collections.unbelievable.hpe.plugins.module_utils.logger import SilentLogger, ModuleLogger  # type: ignore

REQUESTS_IMP_ERR = None
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = format_exc()
    HAS_REQUESTS = False

JsonRestApiResponse = namedtuple("JsonRestApiResponse", ["headers", "content"])


class JsonRestApiClient(object):
    def __init__(
        self,
        protocol,
        host,
        port,
        api_base="",
        username=None,
        password=None,
        validate_certs=True,
        proxy=None,
        logger=SilentLogger(),
    ):
        if not HAS_REQUESTS:
            raise ImportError(
                self.__class__.__name__ + ": requires Python Requests 1.1.0 or higher: https://github.com/psf/requests."
            )
        self.protocol = protocol
        self.port = port
        self.host = host
        self.api_base = api_base
        if self.api_base and not self.api_base.startswith("/"):
            self.api_base = "/" + self.api_base
        if self.api_base and self.api_base.endswith("/"):
            self.api_base = self.api_base[:-1]
        self.username = username
        self.password = password
        self.validate_certs = validate_certs
        if proxy:
            self.proxies = {"http": proxy, "https": proxy}
        else:
            self.proxies = None
        self.logger = logger

    def get_headers(self):
        return {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        }

    def get_auth(self):
        return (self.username, self.password) if self.username else None

    def get_proxies(self):
        return self.proxies

    def get_request(self, uri_path, timeout=None):
        """Execute GET request

        Args:
            uri_path (str): uri relative to api_base
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            json: api response
        """
        return self._execute_request("GET", uri_path, data=None, timeout=timeout).content

    def post_request(self, uri_path, data, timeout=None):
        """Execute POST request

        Args:
            uri_path (str): uri relative to api_base
            data (json): payload
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            json: api response
        """
        return self._execute_request("POST", uri_path, data=data, timeout=timeout).content

    def put_request(self, uri_path, data, timeout=None):
        """Execute PUT request

        Args:
            uri_path (str): uri relative to api_base
            data (json): payload
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            json: api response
        """
        return self._execute_request("PUT", uri_path, data=data, timeout=timeout).content

    def delete_request(self, uri_path, data=None, timeout=None):
        """Execute DELETE request

        Args:
            uri_path (str): uri relative to api_base
            data (json, optional): payload. Defaults to None.
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            json: api response
        """
        return self._execute_request("DELETE", uri_path, data=data, timeout=timeout).content

    def head_request(self, uri_path, timeout=None):
        """Execute HEAD request

        Args:
            uri_path (str): uri relative to api_base
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            json: api response
        """
        return self._execute_request("HEAD", uri_path, data=None, timeout=timeout).content

    def patch_request(self, uri_path, data, timeout=None):
        """Execute PATCH request

        Args:
            uri_path (str): uri relative to api_base
            data (json): payload.
            timeout (int, optional): request timeout. Defaults to None.

        Returns:
            json: api response
        """
        return self._execute_request("PATCH", uri_path, data=data, timeout=timeout).content

    def get_request_with_headers(self, uri_path, timeout=None):
        """Execute GET request

        Args:
            uri_path (str): uri relative to api_base
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            JsonRestApiResponse: api response
        """
        return self._execute_request("GET", uri_path, data=None, timeout=timeout)

    def post_request_with_headers(self, uri_path, data, timeout=None):
        """Execute POST request

        Args:
            uri_path (str): uri relative to api_base
            data (json): payload
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            JsonRestApiResponse: api response
        """
        return self._execute_request("POST", uri_path, data=data, timeout=timeout)

    def put_request_with_headers(self, uri_path, data, timeout=None):
        """Execute PUT request

        Args:
            uri_path (str): uri relative to api_base
            data (json): payload
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            JsonRestApiResponse: api response
        """
        return self._execute_request("PUT", uri_path, data=data, timeout=timeout)

    def delete_request_with_headers(self, uri_path, data=None, timeout=None):
        """Execute DELETE request

        Args:
            uri_path (str): uri relative to api_base
            data (json, optional): payload. Defaults to None.
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            JsonRestApiResponse: api response
        """
        return self._execute_request("DELETE", uri_path, data=data, timeout=timeout)

    def head_request_with_headers(self, uri_path, timeout=None):
        """Execute HEAD request

        Args:
            uri_path (str): uri relative to api_base
            timeout (int, optional): request timeout in seconds. Defaults to None.

        Returns:
            JsonRestApiResponse: api response
        """
        return self._execute_request("HEAD", uri_path, data=None, timeout=timeout)

    def patch_request_with_headers(self, uri_path, data, timeout=None):
        """Execute PATCH request

        Args:
            uri_path (str): uri relative to api_base
            data (json): payload.
            timeout (int, optional): request timeout. Defaults to None.

        Returns:
            JsonRestApiResponse: api response
        """
        return self._execute_request("PATCH", uri_path, data=data, timeout=timeout)

    def cleanup_uri_path(self, uri_path):
        if uri_path.startswith(self.api_base):
            uri_path = uri_path[len(self.api_base):]  # fmt: skip
        if uri_path.startswith("/"):
            uri_path = uri_path[1:]
        return uri_path

    def _execute_request(self, verb, uri_path, data, timeout):
        uri_path = self.cleanup_uri_path(uri_path)
        url = "{0}://{1}:{2}{3}/{4}".format(self.protocol, self.host, self.port, self.api_base, uri_path)
        self.logger.debug("{0} request to {1}".format(verb, url))
        r = requests.request(
            verb,
            url=url,
            headers=self.get_headers(),
            auth=self.get_auth(),
            verify=self.validate_certs,
            json=data,
            timeout=timeout,
            proxies=self.get_proxies(),
        )
        if r.ok:
            content = None
            if r.headers.get("Content-Type", "").startswith("application/json"):
                content = r.json()
            elif r.content:
                self.logger.warn("no json response '{0}' from {1} request to {2}".format(r.content, verb, url))
            return JsonRestApiResponse(r.headers, content)
        else:
            self.logger.warn("response error {0} from {1} request to {2}".format(r.status_code, verb, url))
            r.raise_for_status()


class ModuleBase(object):
    def __init__(self, param_alias_prefix):
        self.param_alias_prefix = param_alias_prefix

    def main(self):
        # define available arguments/parameters a user can pass to the module

        self.module = AnsibleModule(
            argument_spec=self.argument_spec(),
            supports_check_mode=self.supports_check_mode(),
            **self.module_def_extras()
        )

        if not HAS_REQUESTS:
            self.module.fail_json(msg=missing_required_lib("requests"), exception=REQUESTS_IMP_ERR)

        try:
            self.api_client = self.get_api_client()
            self.result = dict(
                changed=False,
                diff=None,
            )

            self.init()
            self.run()
            self.module.exit_json(**self.result)
        except BaseException as e:
            self.module.fail_json(e)

    def supports_check_mode(self):
        return True

    def module_def_extras(self):
        return dict()

    def init(self):
        """Overwrite this to init your module"""
        pass

    def run(self):
        """Overwrite this to implement the module action"""
        pass

    def get_api_client(self):
        return self.get_module_api_client(
            protocol=self.module.params.get("protocol"),
            host=self.module.params.get("hostname"),
            port=self.module.params.get("port"),
            username=self.module.params.get("username"),
            password=self.module.params.get("password"),
            validate_certs=self.module.params.get("validate_certs"),
            proxy=self.module.params.get("proxy") if "proxy" in self.module.params else None,
            logger=ModuleLogger(self.module),
        )

    def get_module_api_client(self, protocol, host, port, username, password, validate_certs, proxy, logger):
        raise NotImplementedError("Please Implement get_module_api_client")

    def set_changed(self, changed):
        self.result["changed"] = changed

    def set_changes(self, before=None, after=None):
        self.result["diff"] = {"before": before, "after": after}
        self.set_changed(before != after)

    def set_message(self, message):
        self.result["message"] = message

    def argument_spec(self):
        return dict(
            protocol=dict(
                type="str",
                choices=["http", "https"],
                required=False,
                default="https",
                aliases=[self.param_alias_prefix + "_protocol"],
            ),
            hostname=dict(
                type="str",
                required=True,
                aliases=[
                    "name",
                    "host",
                    "server",
                    self.param_alias_prefix + "_server",
                    self.param_alias_prefix + "_host",
                ],
            ),
            port=dict(type="int", default=443, aliases=[self.param_alias_prefix + "_port"]),
            username=dict(type="str", required=True, aliases=["user", self.param_alias_prefix + "_user"]),
            password=dict(
                type="str", required=True, aliases=["passwd", self.param_alias_prefix + "_password"], no_log=True
            ),
            validate_certs=dict(type="bool", required=False, default=True),
            proxy=dict(type="str", required=False),
        )
