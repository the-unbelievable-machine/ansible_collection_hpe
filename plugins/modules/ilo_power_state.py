#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ilo_power_state
author:
    - Janne K. Olesen (@jakrol)

short_description: Manage server power state via iLO
description:
    - Manage server power state via iLO

options:
    action:
        description:
            - Power state
        type: str
        choices: ['On', 'ForceOff', 'GracefulShutdown', 'ForceRestart', 'PushPowerButton', 'GracefulRestart']
        required: yes

extends_documentation_fragment:
    - unbelievable.hpe.redfish_api_client
"""

EXAMPLES = r"""
- name: Set iLO SecurityState
  unbelievable.hpe.ilo_power_state:
      action: On
      hostname: '{{ inventory_hostname }}'
      user: user
      password: secret
      delegate_to: localhost
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.redfish import RedfishModuleBase  # type: ignore


class ILOPowerState(RedfishModuleBase):
    def argument_spec(self):

        additional_spec = dict(
            action=dict(
                type="str",
                choices=[
                    "On",
                    "ForceOff",
                    "GracefulShutdown",
                    "ForceRestart",
                    "PushPowerButton",
                    "GracefulRestart",
                ],
                required=True,
            ),
        )
        spec = dict()
        spec.update(super(ILOPowerState, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def run(self):

        before = dict()
        after = dict()

        current_state = self.get_current_power_state()
        before["state"] = current_state
        action = self.module.params.get("action")
        after["state"] = action
        self.set_changes(before, after)

        change_required = ILOPowerState.change_required(current_state, action)
        self.set_changed(change_required)

        if not self.module.check_mode and change_required:
            self.api_client.post_request("Systems/1/Actions/ComputerSystem.Reset", {"ResetType": action})

    @staticmethod
    def change_required(current_state, action):
        change = False
        if current_state == "Off":
            change = action in ["On", "ForceRestart", "PushPowerButton", "GracefulRestart"]
        elif current_state == "On":
            change = action in ["ForceOff", "ForceRestart", "PushPowerButton", "GracefulRestart", "GracefulShutdown"]
        else:
            raise ValueError("Unexpected state: {0}".format(current_state))
        return change

    def get_current_power_state(self):
        data = self.api_client.get_request("Systems/1")
        return data["PowerState"]


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    ILOPowerState().main()


if __name__ == "__main__":
    main()
