# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
    name: oneview
    short_description: HPE OneView inventory source
    version_added: "1.0.0"
    author:
        - Janne K. Olesen <janne.olesen@unbelievable-machine.com>
    requirements:
        - requests >= 1.1
    description:
        - Get iLO hosts from a HPE OneView.
        - Hosts will be ungrouped.
        - Hostvar "hpe_model" will be set
        - Uses a configuration file as an inventory source, it must end with C(oneview.yml) or C(oneview.yaml)
    options:
        plugin:
            description: The name of this plugin, it should always be set to C(um.hpe.oneview) for this plugin to recognize it as it's own.
            required: yes
            choices: ['um.hpe.oneview']
            type: str
        url:
            description:
                - URL of OneView host.
                - If the value is not specified in the inventory configuration, the value of environment variable C(ONEVIEW_URL) will be used instead.
            default: 'https://localhost'
            type: str
            env:
                - name: ONEVIEW_URL
                  version_added: 1.0.0
        user:
            description:
                - OneView api authentication user.
                - If the value is not specified in the inventory configuration, the value of environment variable C(ONEVIEW_USER) will be used instead.
            required: yes
            type: str
            env:
                - name: ONEVIEW_USER
                  version_added: 1.0.0
        password:
            description:
                - OneView authentication password.
                - If the value is not specified in the inventory configuration, the value of environment variable C(ONEVIEW_PASSWORD) will be used instead.
            required: yes
            type: str
            env:
                - name: ONEVIEW_PASSWORD
                  version_added: 1.0.0
        validate_certs:
            description:
                - Verify SSL certificate if using HTTPS.
                - If the value is not specified in the inventory configuration, the value of environment variable C(ONEVIEW_VALIDATE_CERTS) will be used instead.
            type: boolean
            default: yes
            env:
                - name: ONEVIEW_VALIDATE_CERTS
                  version_added: 1.0.0
        preferred_ip:
            description: Preferred source for ansible_host IP address.
            choices: ['IPv4', 'IPv6']
            type: str
            default: 'IPv4'
        hostname_short:
            description: Ues short hostnames.
            type: boolean
            default: yes
        add_domain:
            description:
                - Add domain to hostname.
                - Requires C(hostname_short) to be C(no).
            type: str
        proxy:
            description:
                - Proxy to use when accessing OneView api.
                - If the value is not specified in the inventory configuration, the value of environment variable C(ONEVIEW_PROXY) will be used instead.
                - example: http://localhost:8080
            required: no
            type: str
            env:
                - name: ONEVIEW_PROXY
                  version_added: 1.0.0

"""

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.module_utils.basic import missing_required_lib
from ansible.errors import AnsibleError
from distutils.version import LooseVersion
import traceback

try:
    import requests
    if LooseVersion(requests.__version__) < LooseVersion("1.1.0"):
        raise ImportError
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class InventoryModule(BaseInventoryPlugin):

    NAME = "um.hpe.oneview"
    MAIN_GROUP = "oneview_members"

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.base_url = None
        self.session = None
        self.validate_certs = True
        self.proxies = None
        self.preferred_ip = "IPv4"

        if not HAS_REQUESTS:
            raise AnsibleError(
                "oneview: This module requires Python Requests 1.1.0 or higher: https://github.com/psf/requests."
            )

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(("oneview.yaml", "oneview.yml")):
                valid = True
            else:
                self.display.vvv(
                    "oneview: Skipping due to inventory source not ending in 'onview.yaml' nor 'onview.yml'"
                )
        return valid

    def parse(self, inventory, loader, path, cache=False):
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path)
        self.base_url = self.get_option("url")
        if self.has_option("validate_certs"):
            self.validate_certs = self.get_option("validate_certs")
        if self.has_option("proxy"):
            self.proxies = {
                "http": self.get_option("proxy"),
                'https': self.get_option("proxy")
            }
        if self.has_option("preferred_ip"):
            self.preferred_ip = self.get_option("preferred_ip")
        try:
            self.session = self._login()
            self._populate()
        finally:
            self._logout()

    def _get_headers(self):
        headers = {"X-API-Version": "800"}
        if self.session:
            headers["Auth"] = self.session
        return headers

    def _get_request(self, uri_path):
        url = f"{self.base_url}{uri_path}"
        r = requests.get(url,
                         headers=self._get_headers(),
                         verify=self.validate_certs,
                         proxies=self.proxies)

        if r.ok:
            return r.json()
        else:
            raise AnsibleError(r.raise_for_status)

    def _login(self):
        username = self.get_option("user")
        password = self.get_option("password")
        data_get = {
            "userName": username,
            "password": password,
            "loginMsgAck": "true"
        }
        r = requests.post(f"{self.base_url}/rest/login-sessions",
                          json=data_get,
                          headers=self._get_headers(),
                          verify=self.validate_certs,
                          proxies=self.proxies)
        if r.ok:
            session = r.json().get("sessionID")
            self.display.vvv("oneview: Login successful")
            return session
        else:
            raise AnsibleError(r.raise_for_status)

    def _logout(self):
        if self.session:
            r = requests.delete(f"{self.base_url}/rest/login-sessions",
                                headers=self._get_headers(),
                                verify=self.validate_certs,
                                proxies=self.proxies)
            if r.ok:
                self.session = None
                self.display.vvv("oneview: Logout successful")
            else:
                self.display.vvv("oneview: Logout failed")

    def _populate(self):
        next_url = "/rest/server-hardware"
        while True:
            self.display.vvv(f"oneview: query {next_url}")
            data = self._list_hardware(next_url)
            self.inventory.add_group(self.MAIN_GROUP)
            self._process_hardware_list(data)
            next_url = data.get("nextPageUri", "")
            if not next_url:
                break

    def _list_hardware(self, uri_path):
        return self._get_request(uri_path)

    def _process_hardware_list(self, data):
        if not data:
            self.display.warning(f"oneview: got no hardware_list")
            return
        for member in data.get("members", []):
            name, host_vars = self._process_hardware_member(member)
            group = host_vars["shortModel"].replace(" ", "_")
            self.inventory.add_group(group)
            self.inventory.add_child(self.MAIN_GROUP, group)
            self._populate_host_vars(hosts=[name],
                                     variables=host_vars,
                                     group=group)

    def _process_hardware_member(self, member):
        name = member["mpHostInfo"]["mpHostName"].lower()
        if self.get_option("hostname_short"):
            name = name.split(".")[0]
        elif self.has_option("add_domain"):
            name = name.split(".")[0] + "." + self.get_option("add_domain")
        host_vars = dict()
        host_vars["shortModel"] = member.get("shortModel")
        host_vars["mpModel"] = member.get("mpModel")
        for mp_ip_address in member["mpHostInfo"]["mpIpAddresses"]:
            if mp_ip_address["type"] == "Static":
                ip = mp_ip_address["address"]
                host_vars["ansible_host"] = ip
                if self.preferred_ip == "IPv4" and "." in ip:
                    break
                if self.preferred_ip == "IPv6" and ":" in ip:
                    break
        return name, host_vars
