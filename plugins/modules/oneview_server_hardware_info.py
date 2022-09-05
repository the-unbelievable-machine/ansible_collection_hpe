#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oneview_server_hardware_info
author:
    - Janne K. Olesen (@jakrol)

short_description: Content of /rest/server-hardware endpoint of OneView
description:
    - Content of /rest/server-hardware endpoint of OneView

options:
    hwinfo_entry_fields:
        description:
            - List of fields to copy from oneview's /rest/server-hardware api result, section 'members' to copy.
            - "There are some special fieldnames:
              rs_mpHostName=takes mkHostInfo.mpHostName if exists else mpDnsName.
              rs_mpIpAddress4=first IPv4 address from mpHostInfo.mpIpAddresses with type = static.
              rs_mpIpAddress6=first IPv6 address from mpHostInfo.mpIpAddresses with type = static"
        type: list
        elements: str
        default: [
            "formFactor",
            "memoryMb",
            "mpFirmwareVersion",
            "rs_mpHostName",
            "rs_mpIpAddress4",
            "mpModel",
            "name",
            "partNumber",
            "processorCoreCount",
            "processorCount",
            "processorType",
            "romVersion",
            "serialNumber",
            "serverName",
            "shortModel",
            "uuid"]
        version_added: 2.0.0
    rack_info:
        description: Enrich entries with rack_name and position in rack.
        type: bool
        default: yes
        version_added: 3.2.0
    filter:
        description:
            - OneView rest-api filter
            - see https://techlibrary.hpe.com/docs/enterprise/servers/oneview6.0/cicf-api/en/index.html#stdparams
        required: no
        type: str

extends_documentation_fragment:
    - unbelievable.hpe.oneview_api_client
"""

EXAMPLES = r"""
- name: Get server-hardware
  unbelievable.oneview_server_hardware_info:
    hostname: https://oneview.server.domain
    username: user
    password: secret
  register: servers
"""

RETURN = r"""
servers:
    description:
        - List of servers. Always present, but may be empty.
        - Content depends on api_version and configuration.
    returned: success
    type: list
    elements: dict
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import OneviewModuleBase, ApiHelper  # type: ignore # noqa: E501


class OneViewServerHardwareInfo(OneviewModuleBase):
    def argument_spec(self):
        additional_spec = dict(
            hwinfo_entry_fields=dict(
                type="list",
                required=False,
                elements="str",
                default=[
                    "formFactor",
                    "memoryMb",
                    "mpFirmwareVersion",
                    "rs_mpHostName",
                    "rs_mpIpAddress4",
                    "mpModel",
                    "name",
                    "partNumber",
                    "processorCoreCount",
                    "processorCount",
                    "processorType",
                    "romVersion",
                    "serialNumber",
                    "serverName",
                    "shortModel",
                    "uuid",
                ],
            ),
            rack_info=dict(type="bool", required=False, default=True),
            filter=dict(type="str", required=False),
        )
        spec = dict()
        spec.update(super(OneViewServerHardwareInfo, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def init(self):
        self.rack_info = self.module.params.get("rack_info")
        self.hwinfo_entry_fields = self.module.params.get("hwinfo_entry_fields")

    def run(self):
        self.api_client.login()
        servers_raw = self.api_client.list_server_hardware()
        servers = self._process_servers(servers_raw)
        self.result["servers"] = servers if servers else []
        self.api_client.logout()

    def _process_servers(self, servers_raw):
        racksinfo = {}
        if self.rack_info:
            racksinfo.update(self._prepare_rackinfo())
        servers = []
        for s in servers_raw:
            server = {}
            servers.append(server)
            server.update(ApiHelper.copy_entries(s, self.hwinfo_entry_fields))
            id = server.get("uuid", None)
            if id in racksinfo:
                server["rackInfo"] = racksinfo[id]
        return servers

    def _prepare_rackinfo(self):
        racks_raw = self.api_client.list_racks()
        rackinfo = {}
        rack_fields = ["name", "id", "model", "partNumber", "serialNumber"]
        rackmount_fields = ["topUSlot", "uHeight"]
        for r in racks_raw:
            info = ApiHelper.copy_entries(r, rack_fields)
            for m in r.get("rackMounts", []):
                id = m["mountUri"].split("/")[-1]
                rackinfo[id] = ApiHelper.copy_entries(m, rackmount_fields)
                rackinfo[id].update(info)
        return rackinfo


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    OneViewServerHardwareInfo().main()


if __name__ == "__main__":
    main()
