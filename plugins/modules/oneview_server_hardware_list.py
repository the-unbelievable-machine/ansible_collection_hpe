#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oneview_server_hardware_list
author:
    - Janne K. Olesen (@jakrol)

short_description: Generate a list of server hardware present in OneView
description:
    - Generate a list of server hardware present in OneView
    - This list could be used to dynamically add hosts using C(ansible.builtin.add_host).
    - See also inventory plugin C(unbelievable.hpe.oneview)

options:
    url:
        description:
            - URL of OneView host.
        type: str
        required: yes
        aliases: [ oneview_url ]
        version_added: 1.0.0
    username:
        description:
            - OneView api authentication user.
        required: yes
        type: str
        aliases: [ oneview_user, user ]
        version_added: 1.0.0
    password:
        description:
            - OneView authentication password.
        required: yes
        type: str
        aliases: [ oneview_password, passwd ]
        version_added: 1.0.0
    validate_certs:
        description:
            - Verify SSL certificate if using HTTPS.
        type: bool
        default: yes
        version_added: 1.0.0
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
    proxy:
        description:
            - Proxy to use when accessing OneView API.
            - "example: http://localhost:8080"
        required: no
        type: str
        version_added: 1.0.0
    add_vars:
        description:
            - Add aditional variables to host
        required: no
        type: dict
        version_added: 1.0.0
"""

EXAMPLES = r"""
- name: Get server from Oneview
  unbelievable.oneview_server_hardware_list:
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


from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import OneViewInventory, ModuleLogger, Inventory  # type: ignore # noqa: E501
from ansible.module_utils.basic import AnsibleModule


class DictInventory(Inventory):
    def __init__(self):
        super().__init__()
        self.d = dict(hosts={}, groups={})

    def add_group(self, group):
        self.d["groups"].setdefault(group, dict(name=group, children=list()))

    def add_child_group(self, parent, child):
        if parent in self.d["groups"]:
            if child not in self.d["groups"][parent]["children"]:
                self.d["groups"][parent]["children"].append(child)
        else:
            raise ValueError("group '{0}' not found".format(parent))

    def add_host_to_group(self, group, host):
        if group not in self.d["groups"]:
            raise ValueError("group '{0}' not found".format(group))
        if host in self.d["hosts"]:
            if group not in self.d["hosts"][host]["groups"]:
                self.d["hosts"][host]["groups"].append(group)
        else:
            raise ValueError("host '{0}' not found".format(host))

    def add_host(self, host, variables=None, group=None):
        self.d["hosts"].setdefault(host, dict(name=host, vars=variables, groups=list([group])))

    def get_inventory(self):
        return self.d


class OneViewServerHardwareModule(object):
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.inventory = DictInventory()
        self.oneview_inventory = self._get_oneview_inventory(
            params=self.module.params, inventory=self.inventory, logger=ModuleLogger(self.module)
        )

    def _get_oneview_inventory(self, params, inventory, logger):
        oneview_inventory = OneViewInventory()
        oneview_inventory.init(
            base_url=params.get("url"),
            username=params.get("username"),
            password=params.get("password"),
            inventory=inventory,
            logger=logger,
        )
        oneview_inventory.set_validate_certs(params.get("validate_certs"))
        oneview_inventory.set_preferred_ip(params.get("preferred_ip"))
        oneview_inventory.set_hostname_short(params.get("hostname_short"))
        if params.get("proxy"):
            oneview_inventory.set_proxy(params.get("proxy"))
        if params.get("add_domain"):
            oneview_inventory.set_add_domain(params.get("add_domain"))
        return oneview_inventory

    def run(self):
        try:
            self.oneview_inventory.login()
            self.oneview_inventory.populate()
            result = dict(
                changed=False,
                diff=None,
            )
            result["inventory"] = self.inventory.get_inventory()
            add_vars = self.module.params.get("add_vars")
            if add_vars:
                for host in result["inventory"]["hosts"].values():
                    host.setdefault("vars", dict()).update(add_vars)
            self.module.exit_json(**result)
        except BaseException as e:
            self.module.fail_json(e)
        finally:
            self.oneview_inventory.logout()

    @staticmethod
    def argument_spec():
        return dict(
            url=dict(type="str", required=True, aliases=["oneview_url"]),
            username=dict(type="str", required=True, aliases=["user", "oneview_user"]),
            password=dict(type="str", required=True, aliases=["passwd", "oneview_password"], no_log=True),
            validate_certs=dict(type="bool", required=False, default=True),
            proxy=dict(type="str", required=False),
            preferred_ip=dict(type="str", choices=["IPv4", "IPv6"], required=False, default="IPv4"),
            hostname_short=dict(type="bool", required=False, default=True),
            add_domain=dict(type="str", required=False),
            add_vars=dict(type="dict", required=False),
        )

    @staticmethod
    def main():
        module = AnsibleModule(argument_spec=OneViewServerHardwareModule.argument_spec(), supports_check_mode=True)
        OneViewServerHardwareModule(module).run()


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    OneViewServerHardwareModule.main()


if __name__ == "__main__":
    main()
