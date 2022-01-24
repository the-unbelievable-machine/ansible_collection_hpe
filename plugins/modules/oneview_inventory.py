#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oneview_inventory
author:
    - Janne K. Olesen (@jakrol)

short_description: Generates the same information as the oneview_inventory plugin.
description:
    - This list could be used to dynamically add hosts using C(ansible.builtin.add_host).
    - See also inventory plugin C(unbelievable.hpe.oneview)

options:
    preferred_ip:
        description: Preferred source for ansible_host IP address.
        choices: [ IPv4, IPv6 ]
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
    add_vars:
        description:
            - Add aditional variables to host
        required: no
        type: dict
        version_added: 1.0.0

extends_documentation_fragment:
    - unbelievable.hpe.oneview_api_client
"""

EXAMPLES = r"""
- name: Get server from Oneview
  unbelievable.oneview_inventory:
      url: https://oneview.server.domain
      username: Admin
      password: secret
  register: inv
"""

RETURN = r"""
inventory:
    description:
        - List of hardware servers with IP and some information
    returned: success
    type: dict
    contains:
        groups:
            description:
                - Dictionary with group name as key.
                - All groups are children of group "oneview_member".
                - For each "shortModel" (i.e. DL360_Gen10) a group will be created.
                - For each "mpModel (i.e. iLO5) a group will be created.
            type: dict
            contains:
                name:
                    description: group name
                    type: str
                children:
                    description: List of child groups
                    type: list
        hosts:
            description:
                - Dictionary with hostname as key.
            type: dict
            contains:
                groups:
                    description: List of groups the host belongs to.
                    type: list
                vars:
                    description:
                        - Dictionary with host_vars.
                    type: dict
                    contains:
                        ansible_host:
                            description: host IP address
                            type: str
                        mpModel:
                            description: iLO version, i.e "iLO5"
                            type: str
                        shortModel:
                            description: HPE model name, i.e. "DL360 Gen10"
                            type: str

"""

from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import OneviewModuleBase, OneViewInventoryBuilder  # type: ignore # noqa: E501
from ansible_collections.unbelievable.hpe.plugins.module_utils.inventory import DictInventory  # type: ignore


class OneViewInventory(OneviewModuleBase):
    def init(self):
        self.inventory = DictInventory()
        self.oneview_inventory_builder = OneViewInventoryBuilder(self.api_client, self.inventory)
        self.oneview_inventory_builder.set_preferred_ip(self.module.params.get("preferred_ip"))
        self.oneview_inventory_builder.set_hostname_short(self.module.params.get("hostname_short"))
        if self.module.params.get("add_domain"):
            self.oneview_inventory_builder.set_add_domain(self.module.params.get("add_domain"))

    def run(self):
        self.oneview_inventory_builder.populate()
        self.result["inventory"] = self.inventory.get_inventory()

        add_vars = self.module.params.get("add_vars")
        if add_vars:
            for host in self.result["inventory"]["hosts"].values():
                host.setdefault("vars", dict()).update(add_vars)

    def additional_argument_spec(self):
        return dict(
            preferred_ip=dict(type="str", choices=["IPv4", "IPv6"], required=False, default="IPv4"),
            hostname_short=dict(type="bool", required=False, default=True),
            add_domain=dict(type="str", required=False),
            add_vars=dict(type="dict", required=False),
        )


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    OneViewInventory().main()


if __name__ == "__main__":
    main()
