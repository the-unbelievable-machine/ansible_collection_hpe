# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
name: oneview
short_description: HPE OneView inventory source
version_added: "1.0.0"
author:
    - Janne K. Olesen (@jakrol)
requirements:
    - requests >= 1.1
description:
    - Get iLO hosts from a HPE OneView.
    - "For each host model ('shortModel' from OneView) a group will be created containing all hosts with
        this host model. Example: 'DL360_Gen10'"
    - "For each iLO major version ('mpModel' from OneView) a group will be created containing all hosts with
        this host model. Example: 'iLO5'"
    - All groups are children of group 'oneview_members'
    - Host vars 'shortModel' and 'mpModel will be set
    - Uses a configuration file as an inventory source, it must end with C(oneview.yml) or C(oneview.yaml)
options:
    plugin:
        description:
            - The name of this plugin, it should always be set to C(um.hpe.oneview) for this plugin to
                recognize it as it's own.
        required: yes
        choices: ['unbelievable.hpe.oneview']
        type: str
        version_added: 1.0.0
    url:
        description:
            - URL of OneView host.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_URL) will be used instead.
        type: str
        required: yes
        env:
            - name: ONEVIEW_URL
        version_added: 1.0.0
    user:
        description:
            - OneView api authentication user.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_USER) will be used instead.
        required: yes
        type: str
        env:
            - name: ONEVIEW_USER
        version_added: 1.0.0
    password:
        description:
            - OneView authentication password.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_PASSWORD) will be used instead.
        required: yes
        type: str
        env:
            - name: ONEVIEW_PASSWORD
        version_added: 1.0.0
    validate_certs:
        description:
            - Verify SSL certificate if using HTTPS.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_VALIDATE_CERTS) will be used instead.
        type: bool
        default: yes
        env:
            - name: ONEVIEW_VALIDATE_CERTS
        version_added: 1.0.0
    preferred_ip:
        description: Preferred source for ansible_host IP address.
        choices: ['IPv4', 'IPv6']
        type: str
        default: 'IPv4'
        version_added: 1.0.0
    hostname_short:
        description: Ues short hostnames.
        type: bool
        default: yes
        version_added: 1.0.0
    add_domain:
        description:
            - Add domain to hostname.
            - Requires C(hostname_short) to be C(no).
        type: str
        version_added: 1.0.0
    proxy:
        description:
            - Proxy to use when accessing OneView API.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_PROXY) will be used instead.
            - if requests where installed like 'pip install requests[socks]', then socks proxies
                are supported.
            - "example: http://localhost:8080"
        required: no
        type: str
        env:
            - name: ONEVIEW_PROXY
        version_added: 1.0.0
"""

from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import (  # type: ignore
    OneViewInventory,
    BaseInventoryPluginLogger,
    Inventory,
)
from ansible.plugins.inventory import BaseInventoryPlugin


class BaseInventoryPluginInventory(Inventory):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def add_group(self, group):
        self.plugin.inventory.add_group(group)

    def add_child_group(self, parent, child):
        self.plugin.inventory.add_child(parent, child)

    def add_host_to_group(self, group, host):
        self.plugin.inventory.add_child(group, host)

    def add_host(self, host, variables=None, group=None):
        self.plugin._populate_host_vars(hosts=[host], variables=variables, group=group)


class InventoryModule(BaseInventoryPlugin):

    NAME = "unbelievable.hpe.oneview"

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.oneview_inventory = OneViewInventory()

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(("oneview.yaml", "oneview.yml")):
                valid = True
            else:
                self.display.vv(
                    "oneview: Skipping due to inventory source not ending in 'onview.yaml' nor 'onview.yml'"
                )
        return valid

    def parse(self, inventory, loader, path, cache=False):
        super(InventoryModule, self).parse(inventory, loader, path, cache=False)
        self._read_config_data(path)

        self.oneview_inventory.init(
            base_url=self.get_option("url"),
            username=self.get_option("user"),
            password=self.get_option("password"),
            inventory=BaseInventoryPluginInventory(self),
            logger=BaseInventoryPluginLogger(self),
        )

        self.oneview_inventory.set_validate_certs(self.get_option("validate_certs"))
        self.oneview_inventory.set_preferred_ip(self.get_option("preferred_ip"))
        self.oneview_inventory.set_hostname_short(self.get_option("hostname_short"))
        if self.has_option("proxy"):
            self.oneview_inventory.set_proxy(self.get_option("proxy"))
        if self.has_option("add_domain"):
            self.oneview_inventory.set_add_domain(self.get_option("add_domain"))

        try:
            self.oneview_inventory.login()
            self.oneview_inventory.populate()
        finally:
            self.oneview_inventory.logout()
