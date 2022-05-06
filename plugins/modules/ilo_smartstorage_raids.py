#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ilo_smartstorage_raids
author:
    - Janne K. Olesen (@jakrol)

short_description: Create/configure/delete smartstorage raids
description:
    - Create / configure / delete a smartstorage raids.
    - Currently only Raid1 is supported.
    - For each declared raid, this module will filter the disks using min_size, max_size and disk_type to
      find suitable disks.
    - Module DOES NOT CARE IF DISK IS ALREADY USED!
    - Disks are processed in Location order, The first disks matching the filters are used.

options:
    raids:
        description:
            - SmartStorage raid configuration.
            - Raids not defined here are DELETED!
        type: list
        required: yes
        elements: dict
        suboptions:
            name:
                description:
                    - Name of the logical device. Changing the name will result in RECREATION of the raid,
                      unless ignore_raid_names is set.
                    - Name is ignored if ignore_raid_names is set.
                type: str
                required: no
            raid_level:
                description:
                    - Raid level
                type: int
                required: yes
                choices: [0, 1, 5]
            disks:
                description:
                    - Number of disks to use for raid.
                type: int
                required: no
            disk_type:
                description:
                    - Filter disks to use by type.
                type: str
                required: no
                choices: ['SSD', 'HDD']
            min_size:
                description:
                    - Filter disks to use by size (in GB)
                type: int
                required: no
                default: 0
            max_size:
                description:
                    - Filter disks to use by size (in GB)
                type: int
                required: no
                default: 10000000
            accelerator:
                description:
                    - Raid accelerator to use
                type: str
                required: no
                choices: ['IOBypass', 'ControllerCache', 'None', 'SmartCache']
                default: None
            legacybootpriority:
                description: LegacyBootPriority.
                type: str
                required: no
                choices: ['Primary', 'Secondary', 'None']
                default: None
    ignore_raid_names:
        description:
            - Ignore raid.name
        type: bool
        required: no
        default: False
    controller:
        description:
            - Raid controller to look for available disks
        type: int
        required: no
        default: 0

extends_documentation_fragment:
    - unbelievable.hpe.redfish_api_client
"""

EXAMPLES = r"""
- name: Configure raids
  unbelievable.hpe.ilo_smartstorage_raids:
      hostname: '{{ inventory_hostname }}'
      user: user
      password: secret
      delegate_to: localhost
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.redfish import RedfishModuleBase  # type: ignore


class IloSmartStorageRaids(RedfishModuleBase):
    def argument_spec(self):
        additional_spec = dict(
            raids=dict(
                type="list",
                required=True,
                elements="dict",
                options=dict(
                    name=dict(type="str", required=False),
                    raid_level=dict(type="int", required=True, choices=[0, 1, 5]),
                    disks=dict(type="int", required=False),
                    disk_type=dict(type="str", required=False, choices=["SSD", "HDD"]),
                    min_size=dict(type="int", required=False, default=0),
                    max_size=dict(type="int", required=False, default=10000000),
                    accelerator=dict(
                        type="str",
                        required=False,
                        choices=["IOBypass", "ControllerCache", "None", "SmartCache"],
                        default="None",
                    ),
                    legacybootpriority=dict(
                        type="str", required=False, choices=["Primary", "Secondary", "None"], default="None"
                    ),
                ),
            ),
            ignore_raid_names=dict(type="bool", required=False, default=False),
            controller=dict(type="int", required=False, default=0),
        )
        spec = dict()
        spec.update(super(IloSmartStorageRaids, self).argument_spec())

        spec.update(additional_spec)
        return spec

    def run(self):

        before = dict()
        after = dict()

        config_api_endpoint = self.get_config_endpoint(self.module.params.get("controller"))
        before["raids"] = self.get_current_raids(config_api_endpoint)
        self.result["disks"] = self.get_disks(self.module.params.get("controller"))

        build_raids = self.create_logical_drives_definitions(self.module.params.get("raids"), self.result["disks"])
        after["raids"] = build_raids

        if not self.module.check_mode:
            if before != after:
                request_data = {"DataGuard": "Disabled", "LogicalDrives": build_raids}
                self.result["response"] = self.api_client.put_request(
                    config_api_endpoint + "settings/", data=request_data
                )

        self.set_changes(before, after)

    def get_disks(self, controller):
        disks = []
        drives = self.api_client.get_request(
            "Systems/1/SmartStorage/ArrayControllers/{0}/DiskDrives".format(controller)
        )
        for member in drives.get("Members", []):
            disks.append(self.get_disk_info(member["@odata.id"]))
        return disks

    def get_disk_info(self, disk_url):
        disk_info = self.api_client.get_request(disk_url)
        disk = {}
        for key in ["CapacityGB", "Location", "MediaType"]:
            disk[key] = disk_info[key]
        return disk

    def get_config_endpoint(self, controller):
        sysinfo = self.api_client.get_request("Systems/1/")
        slot = "Slot {0}".format(controller)
        endpoint = None
        for s_config_endpoint in [x["@odata.id"] for x in sysinfo["Oem"]["Hpe"]["SmartStorageConfig"]]:
            s_config = self.api_client.get_request(s_config_endpoint)
            if s_config["Location"] == slot:
                endpoint = s_config_endpoint
                break
        return endpoint

    def get_current_raids(self, endpoint):
        current_raids = []
        config = self.api_client.get_request(endpoint)
        for ldrive in config.get("LogicalDrives", []):
            raid = {}
            if not self.module.params.get("ignore_raid_names"):
                raid["LogicalDriveName"] = ldrive["LogicalDriveName"]
            for k in ["Raid", "Accelerator", "DataDrives", "SpareDrives", "LegacyBootPriority"]:
                raid[k] = ldrive[k]
            current_raids.append(raid)
        return current_raids

    def create_logical_drives_definitions(self, raids, disks):
        build_raids = []
        remaining_disks = disks

        for raid in raids:
            required_disks = self.get_required_disks_number(raid)
            raid_disks, remaining_disks = self.find_disks_for_raid(
                disks=remaining_disks,
                required_disks=required_disks,
                min_size=raid.get("min_size"),
                max_size=raid.get("max_size"),
                media_type=raid.get("disk_type", None),
            )
            if len(raid_disks) < required_disks:
                self.module.fail_json(
                    msg="Cound not find necessary disks for raid",
                    raid=raid,
                    all_disks=disks,
                    remaining_disks=remaining_disks,
                )
            build_raids.append(self.create_logical_drive_definition(raid, raid_disks))

        return build_raids

    def create_logical_drive_definition(self, raid, raid_disks):
        logical_drive = {}
        if not self.module.params.get("ignore_raid_names") and raid.get("name", None):
            logical_drive["LogicalDriveName"] = raid.get("name")
        logical_drive["Raid"] = "Raid{0}".format(raid.get("raid_level"))
        logical_drive["Accelerator"] = raid.get("accelerator")
        logical_drive["DataDrives"] = [d["Location"] for d in raid_disks]
        logical_drive["SpareDrives"] = []
        logical_drive["LegacyBootPriority"] = raid.get("legacybootpriority")
        return logical_drive

    def get_required_disks_number(self, raid):
        raid_level = raid.get("raid_level")
        min_disks = 1
        if raid_level == 1:
            min_disks = 2
        elif raid_level == 5:
            min_disks = 3

        specified_disks = raid.get("disks") if raid.get("disks") is not None else min_disks

        if specified_disks < min_disks:
            self.module.fail_json(
                msg="RAID{0} requires minimal {1} disks, but {2} disks specified".format(
                    raid_level, min_disks, specified_disks
                )
            )
        return specified_disks

    def find_disks_for_raid(self, disks, required_disks, min_size, max_size, media_type):
        remaining_disks = []
        raid_disks = []

        for disk in sorted(disks, key=lambda d: d["Location"]):
            if (
                len(raid_disks) >= required_disks
                or disk["CapacityGB"] < min_size  # noqa: W503
                or disk["CapacityGB"] > max_size  # noqa: W503
                or (media_type and disk["MediaType"] != media_type)  # noqa: W503
            ):
                remaining_disks.append(disk)
            else:
                raid_disks.append(disk)

        return raid_disks, remaining_disks


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    IloSmartStorageRaids().main()


if __name__ == "__main__":
    main()
