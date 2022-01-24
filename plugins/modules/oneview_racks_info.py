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
    returned: success
    type: complex
    elements: dict
    contains:
        name:
            type: str
            description: Rack name
        id:
            type: str
            description: OneView uuid for entry
        depth:
            type: int
            description: rack depth
        height:
            type: int
            description: rack depth
        model:
            type: str
            description: rack model
        partNumber:
            type: str
            description: partNumber
        serialNumber:
            type: str
            description: serialNumber
        thermalLimit:
            type: str
            description: thermalLimit
        uHeight:
            type: int
            description: uHeight
        rackMounts:
            description: Units mounted in rack
            type: complex
            elements: dict
            contains:
                category:
                    type: str
                    description: OneView category
                formFactor:
                    type: str
                    description: formFactor
                location:
                    type: str
                    description: location
                mpHostName:
                    type: str
                    description: iLO hostname
                mpIpAddress:
                    type: str
                    description: iLO ip address
                name:
                    type: str
                    description: name
                partNumber:
                    type: str
                    description: partNumber
                serialNumber:
                    type: str
                    description: serialNumber
                serverName:
                    type: str
                    description: serverName
                shortModel:
                    type: str
                    description: shortModel
                topUSlot:
                    type: str
                    description: topUSlot
                uHeight:
                    type: int
                    description: uHeight
                uuid:
                    type: str
                    description: OneView uuid for device
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import OneviewModuleBase, ApiHelper  # type: ignore # noqa: E501
from ansible_collections.unbelievable.hpe.plugins.module_utils.api_client import copy_entries, set_not_none  # type: ignore # noqa: E501


class OneViewRacksInfo(OneviewModuleBase):

    rack_entries = [
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
    ]

    rack_mount_entries = ["location", "topUSlot", "uHeight", "relativeOrder"]

    hw_info_entries = [
        "name",
        "serverName",
        "category",
        "shortModel",
        "formFactor",
        "serialNumber",
        "uuid",
        "partNumber",
    ]

    def run(self):
        self.api_client.login()
        racks_raw = self.api_client.list_racks()
        racks = self._process_racks(racks_raw)
        self.result["racks"] = racks if racks else []
        self.api_client.logout()

    def _process_racks(self, racks_raw):
        import requests

        racks = []
        for r in racks_raw:
            rack = {"rackMounts": []}
            racks.append(rack)
            copy_entries(r, rack, OneViewRacksInfo.rack_entries, copy_empty=False)
            for m in r.get("rackMounts", []):
                mount = {}
                rack["rackMounts"].append(mount)
                copy_entries(m, mount, OneViewRacksInfo.rack_mount_entries, copy_empty=False)
                if m["mountUri"]:
                    try:
                        mount_info = self.api_client.get_request(m["mountUri"])
                        copy_entries(mount_info, mount, OneViewRacksInfo.hw_info_entries, copy_empty=False)
                        set_not_none(mount, "mpHostName", ApiHelper.Host.mpHostName(mount_info))
                        set_not_none(mount, "mpIpAddress", ApiHelper.Host.mpHostIpv4(mount_info))

                    except requests.HTTPError as e:
                        if e.response.status_code != 404:
                            raise e
        return racks


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    OneViewRacksInfo().main()


if __name__ == "__main__":
    main()
