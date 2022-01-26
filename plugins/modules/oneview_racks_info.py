#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oneview_racks_info
author:
    - Janne K. Olesen (@jakrol)

short_description: Content of /rest/racks endpoint of OneView
description:
    - Content of /rest/racks endpoint of OneView

options:
    rack_entry_fields:
        description:
            - List of fields to copy from oneview's /rest/racks api result to copy.
        type: list
        elements: str
        default: [
            "name",
            "id",
            "depth",
            "height",
            "width",
            "model",
            "partNumber",
            "serialNumber",
            "thermalLimit",
            "uHeight"]
        version_added: 2.0.0
    rackmount_entry_fields:
        description:
            - List of fields to copy from oneview's /rest/racks api result, section 'rackMounts' to copy.
        type: list
        elements: str
        default: [
            "location",
            "topUSlot",
            "uHeight"]
        version_added: 2.0.0
    hwinfo_entry_fields:
        description:
            - List of fields to copy from oneview's api result, when looking up 'mountUri' field.
            - "There are some special fieldnames:
              rs_mpHostName=takes mkHostInfo.mpHostName if exists else mpDnsName.
              rs_mpIpAddress4=first IPv4 address from mpHostInfo.mpIpAddresses with type = static.
              rs_mpIpAddress6=first IPv6 address from mpHostInfo.mpIpAddresses with type = static"
        type: list
        elements: str
        default: [
            "name",
            "serverName",
            "category",
            "shortModel",
            "formFactor",
            "uuid",
            "rs_mpHostName",
            "rs_mpIpAddress4"]
        version_added: 2.0.0

extends_documentation_fragment:
    - unbelievable.hpe.oneview_api_client
"""

EXAMPLES = r"""
- name: Get rack_info
  unbelievable.oneview_racks_info:
    hostname: https://oneview.server.domain
    username: user
    password: secret
  register: racks
"""

RETURN = r"""
racks:
    description:
        - List of racks. Always present, but may be empty.
        - Content depends on api_version and configuration.
    returned: success
    type: list
    elements: dict
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import OneviewModuleBase, ApiHelper  # type: ignore # noqa: E501


class OneViewRacksInfo(OneviewModuleBase):
    def additional_argument_spec(self):
        return dict(
            rack_entry_fields=dict(
                type="list",
                required=False,
                elements="str",
                default=[
                    "name",
                    "id",
                    "depth",
                    "height",
                    "width",
                    "model",
                    "partNumber",
                    "serialNumber",
                    "thermalLimit",
                    "uHeight",
                ],
            ),
            rackmount_entry_fields=dict(
                type="list", required=False, elements="str", default=["location", "topUSlot", "uHeight"]
            ),
            hwinfo_entry_fields=dict(
                type="list",
                required=False,
                elements="str",
                default=[
                    "name",
                    "serverName",
                    "category",
                    "shortModel",
                    "formFactor",
                    "uuid",
                    "rs_mpHostName",
                    "rs_mpIpAddress4",
                ],
            ),
        )

    def init(self):
        self.rack_entry_fields = self.module.params.get("rack_entry_fields")
        self.rackmount_entry_fields = self.module.params.get("rackmount_entry_fields")
        self.hwinfo_entry_fields = self.module.params.get("hwinfo_entry_fields")

    def run(self):
        self.api_client.login()
        racks_raw = self.api_client.list_racks()
        racks = self._process_racks(racks_raw)
        self.result["racks"] = racks if racks else []
        self.api_client.logout()

    def _process_racks(self, racks_raw):
        # to satisfy ansible tests
        import requests

        racks = []
        for r in racks_raw:
            rack = {"rackMounts": []}
            racks.append(rack)
            rack.update(ApiHelper.copy_entries(r, self.rack_entry_fields))
            for m in r.get("rackMounts", []):
                mount = {}
                rack["rackMounts"].append(mount)
                mount.update(ApiHelper.copy_entries(m, self.rackmount_entry_fields))
                if m["mountUri"] and self.hwinfo_entry_fields:
                    try:
                        hwinfo = self.api_client.get_request(m["mountUri"])
                        mount.update(ApiHelper.copy_entries(hwinfo, self.hwinfo_entry_fields))
                    except requests.HTTPError as e:
                        if e.response.status_code != 404:
                            raise e
        return racks


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    OneViewRacksInfo().main()


if __name__ == "__main__":
    main()
