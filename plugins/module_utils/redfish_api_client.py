# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from traceback import format_exc
import time

REQUESTS_IMP_ERR = None
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = format_exc()
    HAS_REQUESTS = False


class RedfishModuleBase(object):
    def main(self):
        # define available arguments/parameters a user can pass to the module
        argument_spec = RedfishModuleBase.argument_spec()
        argument_spec.update(self.additional_argument_spec())

        self.module = AnsibleModule(
            argument_spec=argument_spec, supports_check_mode=self.supports_check_mode(), **self.module_def_extras()
        )

        self.api_client = RedfishApiClient(self.module)
        self.result = dict(
            changed=False,
            diff=None,
        )

        self.init()
        try:
            self.run()
            self.module.exit_json(**self.result)
        except BaseException as e:
            self.module.fail_json(e)

    @staticmethod
    def setdefault_recursive(path, d):
        """Split 'path' on '.' and recursively calls setdefault on nested dict d"""
        value = d if d is not None else dict()
        for key in path.split("."):
            value = value.setdefault(key, dict())
        return value

    @staticmethod
    def get_recursive(path, d):
        """Split 'path' on '.' and recursively get value from nested dict d"""
        if d is None:
            return None
        value = d
        for key in path.split("."):
            if key in value:
                value = value[key]
            else:
                return None
        return value

    def supports_check_mode(self):
        return True

    def additional_argument_spec(self):
        """Overwrite this to provide additional module argument specs"""
        return dict()

    def module_def_extras(self):
        return dict()

    def init(self):
        """Overwrite this to init your module"""
        pass

    def run(self):
        """Overwrite this to implement the module action"""
        pass

    def set_changed(self, changed):
        self.result["changed"] = changed

    def set_changes(self, before=None, after=None):
        self.result["diff"] = {"before": before, "after": after}
        self.set_changed(before != after)

    def set_message(self, message):
        self.result["message"] = message

    def wait_for_ilo_reset(self, seconds_to_wait, param_name="wait_for_reset"):
        time.sleep(5)  # wait 5 seconds for iLO reset to start
        end = time.time() + seconds_to_wait
        data = None
        while time.time() <= end:
            try:
                data = self.api_client.get_request("", timeout=5, fail_on_error=False)
                break
            except BaseException:
                pass
        if not data:
            self.module.fail_json(
                msg=(
                    "Waiting for iLO reset timed out. Changes should be applied successfully, "
                    "but iLO reset still seems to be in progress. Increasing {0}={1} "
                    "should fix this problem."
                ).format(param_name, seconds_to_wait)
            )

    @staticmethod
    def argument_spec():
        return dict(
            hostname=dict(type="str", required=True, aliases=["name", "ilo_server"]),
            username=dict(type="str", required=True, aliases=["user", "ilo_user"]),
            password=dict(type="str", required=True, aliases=["passwd", "ilo_password"], no_log=True),
            validate_certs=dict(type="bool", required=False, default=True),
            protocol=dict(
                type="str", choices=["http", "https"], required=False, default="https", aliases=["ilo_protocol"]
            ),
            port=dict(type="int", default=443, aliases=["ilo_port"]),
            proxy=dict(type="str", required=False),
        )


class RedfishApiClient(object):

    API_BASE = "/redfish/v1/"

    def __init__(self, module):
        self.module = module
        self._check_required_library()

        self.base_url = "{0}://{1}:{2}{3}".format(
            self.module.params.get("protocol"),
            self.module.params.get("hostname"),
            self.module.params.get("port"),
            RedfishApiClient.API_BASE,
        )

        self.validate_certs = self.module.params.get("validate_certs")
        self.headers = self._get_headers()
        self.auth = self._get_auth()
        self.proxies = self._get_proxies()

    def _cleanup_uri_path(self, uri_path):
        if uri_path.startswith(RedfishApiClient.API_BASE):
            return uri_path[len(RedfishApiClient.API_BASE):]  # fmt: skip
        elif uri_path.startswith("/"):
            return uri_path[1:]
        return uri_path

    def _get_auth(self):
        return (self.module.params.get("username"), self.module.params.get("password"))

    def _get_headers(self):
        return {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
        }

    def _get_proxies(self):
        proxies = None
        if "proxy" in self.module.params:
            proxies = {"http": self.module.params.get("proxy"), "https": self.module.params.get("proxy")}
        return proxies

    def _check_required_library(self):
        if not HAS_REQUESTS:
            self.module.fail_json(msg=missing_required_lib("requests"), exception=REQUESTS_IMP_ERR)

    def get_request(self, uri_path, timeout=None, fail_on_error=True):
        return self._execute_request(
            "GET",
            uri_path,
            headers=self.headers,
            auth=self.auth,
            proxies=self.proxies,
            verify=self.validate_certs,
            timeout=timeout,
            fail_on_error=fail_on_error,
        )

    def post_request(self, uri_path, data, timeout=None, fail_on_error=True):
        return self._execute_request(
            "POST",
            uri_path,
            headers=self.headers,
            auth=self.auth,
            proxies=self.proxies,
            verify=self.validate_certs,
            data=data,
            timeout=timeout,
            fail_on_error=fail_on_error,
        )

    def put_request(self, uri_path, data, timeout=None, fail_on_error=True):
        return self._execute_request(
            "PUT",
            uri_path,
            headers=self.headers,
            auth=self.auth,
            proxies=self.proxies,
            verify=self.validate_certs,
            data=data,
            timeout=timeout,
            fail_on_error=fail_on_error,
        )

    def delete_request(self, uri_path, data=None, timeout=None, fail_on_error=True):
        return self._execute_request(
            "DELETE",
            uri_path,
            headers=self.headers,
            auth=self.auth,
            proxies=self.proxies,
            verify=self.validate_certs,
            data=data,
            timeout=timeout,
            fail_on_error=fail_on_error,
        )

    def head_request(self, uri_path, timeout=None, fail_on_error=True):
        return self._execute_request(
            "HEAD",
            uri_path,
            headers=self.headers,
            auth=self.auth,
            proxies=self.proxies,
            verify=self.validate_certs,
            timeout=timeout,
            fail_on_error=fail_on_error,
        )

    def patch_request(self, uri_path, data=None, timeout=None, fail_on_error=True):
        return self._execute_request(
            "PATCH",
            uri_path,
            headers=self.headers,
            auth=self.auth,
            proxies=self.proxies,
            verify=self.validate_certs,
            data=data,
            timeout=timeout,
            fail_on_error=fail_on_error,
        )

    def _execute_request(
        self,
        verb,
        uri_path,
        headers=None,
        auth=None,
        proxies=None,
        verify=True,
        data=None,
        timeout=None,
        fail_on_error=True,
    ):
        uri_path = self._cleanup_uri_path(uri_path)
        url = "{0}{1}".format(self.base_url, uri_path)
        try:
            r = requests.request(
                verb, url=url, headers=headers, auth=auth, verify=verify, json=data, timeout=timeout, proxies=proxies
            )
            if r.ok:
                if r.headers.get("Content-Type").startswith("application/json"):
                    return r.json()
            else:
                r.raise_for_status()
        except BaseException as e:
            if fail_on_error:
                self.module.fail_json(msg="{0} request to '{1}' failed:  {2}".format(verb, url, e))
            else:
                raise e
