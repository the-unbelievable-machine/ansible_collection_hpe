#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ilo_boot_order
author:
    - Janne K. Olesen (@jakrol)

short_description: Manage boot order
description:
    - Manage boot order.

options:
    patterns:
        description:
            - List of regex patterns.
            - Pattern will be applied to list of available boot sources (BootString)
        type: list
        elements: str
        required: yes

extends_documentation_fragment:
    - unbelievable.hpe.redfish_api_client
"""

EXAMPLES = r"""
- name: Set iLO boot order
  unbelievable.hpe.ilo_boot_order:
      patterns:
        - RAID1 Logical Drive 1
      hostname: '{{ inventory_hostname }}'
      user: user
      password: secret
      delegate_to: localhost
"""

RETURN = r"""
pending:
    description:
        - Boolean indicated that new boot order is applied, but system restart is required.
    returned: success
    type: bool
BootSources:
    description:
        - List of available BootSources
    returned: success
    type: list
    elements: dict
"""

from ansible_collections.unbelievable.hpe.plugins.module_utils.redfish import RedfishModuleBase  # type: ignore
import re


class ILOBootOrder(RedfishModuleBase):

    CURRENT_SETTINGS_ENDPOINT = "Systems/1/Bios/boot"
    PENDING_SETTINGS_ENDPOINT = "Systems/1/Bios/boot/settings"

    def argument_spec(self):
        additional_spec = dict(
            patterns=dict(
                type="list",
                elements="str",
                required=True,
            )
        )
        spec = dict()
        spec.update(super(ILOBootOrder, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def run(self):

        before = dict()
        after = dict()

        current_settings = self.api_client.get_request(ILOBootOrder.CURRENT_SETTINGS_ENDPOINT)
        current_order = current_settings.get("PersistentBootConfigOrder", [])
        current_pending_order = self.api_client.get_request(ILOBootOrder.PENDING_SETTINGS_ENDPOINT).get(
            "PersistentBootConfigOrder", []
        )
        before["order"] = current_pending_order
        boot_sources = current_settings["BootSources"]
        boot_sources = list(boot_sources)
        self.result["available_boot_sources"] = list(boot_sources)
        new_order = ILOBootOrder.compute_new_order(boot_sources, self.module.params.get("patterns"))
        self.result["unmatched_boot_sources"] = list(boot_sources)
        after["order"] = new_order

        self.set_changes(before, after)
        self.result["pending"] = self.result["changed"] or current_pending_order != current_order

        if not self.module.check_mode and current_pending_order != new_order:
            self.result["response"] = self.api_client.patch_request(
                ILOBootOrder.PENDING_SETTINGS_ENDPOINT, {"PersistentBootConfigOrder": new_order}
            )

    @staticmethod
    def compute_new_order(boot_sources, patterns):
        new_order = []
        if patterns:
            for p in patterns:
                matcher = re.compile(p)
                for boot_source in list(boot_sources):
                    if matcher.match(boot_source["BootString"]):
                        new_order.append(boot_source["StructuredBootString"])
                        boot_sources.remove(boot_source)
        new_order += [s["StructuredBootString"] for s in boot_sources]
        return new_order


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    ILOBootOrder().main()


if __name__ == "__main__":
    main()
