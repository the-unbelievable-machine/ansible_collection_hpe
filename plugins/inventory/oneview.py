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
    protocol:
        description:
            - Protocol to use when connecting to OneView.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_PROTOCOL) will be used instead.
        choices: ['http', 'https']
        type: str
        default: 'https'
        env:
            - name: ONEVIEW_PROTOCOL
        version_added: 2.0.0
    host:
        description:
            - Hostname to use when connecting to OneView.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_HOST) will be used instead.
        type: str
        required: yes
        env:
            - name: ONEVIEW_HOST
        version_added: 2.0.0
    port:
        description:
            - Port to use when connecting to OneView.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_PORT) will be used instead.
        type: int
        default: 443
        env:
            - name: ONEVIEW_PORT
        version_added: 2.0.0
    api_version:
        description:
            - OneView REST api version.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_API_VERSION) will be used instead.
        type: int
        default: 2400
        env:
            - name: ONEVIEW_API_VERSION
        version_added: 2.0.0
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
        default: no
        version_added: 1.0.0
    add_domain:
        description:
            - Add domain to hostname.
            - Requires C(hostname_short) to be C(no).
        type: str
        version_added: 1.0.0
    proxy:
        description:
            - Proxy (hostname+port) to use when connecting to OneView.
            - If the value is not specified in the inventory configuration, the value of environment variable
                C(ONEVIEW_PROXY) will be used instead.
        type: str
        required: no
        env:
            - name: ONEVIEW_PROXY
        version_added: 2.0.0
"""

from ansible_collections.unbelievable.hpe.plugins.module_utils.logger import InventoryPluginLogger  # type: ignore
from ansible_collections.unbelievable.hpe.plugins.module_utils.inventory import InventoryPluginInventory  # type: ignore
from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import (  # type: ignore
    OneViewApiClient,
    OneViewInventoryBuilder,
)
from ansible.plugins.inventory import BaseInventoryPlugin


class InventoryModule(BaseInventoryPlugin):

    NAME = "unbelievable.hpe.oneview"

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(("oneview.yaml", "oneview.yml")):
                valid = True
            else:
                self.display.vv(
                    "oneview: Skipping due to inventory source not ending in 'oneview.yaml' nor 'oneview.yml'"
                )
        return valid

    def parse(self, inventory, loader, path, cache=False):
        super(InventoryModule, self).parse(inventory, loader, path, cache=False)
        self._read_config_data(path)

        api_client = OneViewApiClient(
            protocol=self.get_option("protocol"),
            host=self.get_option("host"),
            port=self.get_option("port"),
            username=self.get_option("user"),
            password=self.get_option("password"),
            validate_certs=self.get_option("validate_certs"),
            proxy=self.get_option("proxy"),
            api_version=self.get_option("api_version"),
            logger=InventoryPluginLogger(self),
        )
        oneview_inventory_builder = OneViewInventoryBuilder(api_client, InventoryPluginInventory(self))
        oneview_inventory_builder.set_preferred_ip(self.get_option("preferred_ip"))
        oneview_inventory_builder.set_hostname_short(self.get_option("hostname_short"))
        if self.has_option("add_domain"):
            oneview_inventory_builder.set_add_domain(self.get_option("add_domain"))

        oneview_inventory_builder.populate()
