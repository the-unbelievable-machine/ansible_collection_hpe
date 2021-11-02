#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ilo_thermal_settings
author:
    - Janne K. Olesen (@jakrol)

short_description: Manage iLO Thermal settings
description:
    - Manage iLO Thermal settings

options:
    thermal_configuration:
        description:
            - Use this option to select the fan cooling solution for the system. Optimal Cooling provides the most
              efficient solution by configuring fan speeds to the minimum required speed to provide adequate cooling.
              Increased Cooling runs fans at higher speeds to provide additional cooling. Select Increased Cooling
              when third-party storage controllers are cabled to the embedded hard drive cage, or if the system is
              experiencing thermal issues that cannot be resolved. Maximum cooling provides the maximum cooling
              available on this platform. Enhanced CPU Cooling runs the fans at a higher speed to provide additional
              cooling to the processors. Selecting Enhanced CPU Cooling may improve system performance with
              certain processor intensive workloads.
            - Changing this value will trigger an iLO reset.
        type: str
        choices: [ OptimalCooling, IncreasedCooling, MaximumCooling, EnhancedCooling ]
        required: no
        version_added: 1.0.0
    fan_percent_minimum:
        description:
            - Minimum fan speed in percentage
        type: int
        required: no
        version_added: 1.0.0
    wait_for_reset:
        description:
            - Max seconds to wait for iLO reset to be completed.
            - 0 not wait at all.
        type: int
        required: no
        default: 60
        version_added: 1.0.0

extends_documentation_fragment:
    - unbelievable.hpe.redfish_api_client
"""

EXAMPLES = r"""
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.redfish_api_client import RedfishModuleBase  # type: ignore # noqa: E501


class ILOThermalSettings(RedfishModuleBase):

    ENDPOINT = "Chassis/1/Thermal"

    def additional_argument_spec(self):
        return dict(
            thermal_configuration=dict(
                type="str",
                choices=["OptimalCooling", "IncreasedCooling", "MaximumCooling", "EnhancedCooling"],
                required=False,
            ),
            fan_percent_minimum=dict(
                type="int",
                required=False,
            ),
            wait_for_reset=dict(type="int", required=False, default=60),
        )

    def module_def_extras(self):
        return dict(required_one_of=[["thermal_configuration", "fan_percent_minimum"]])

    def run(self):

        before = dict()
        after = dict()
        patches = dict()

        current_data = self.api_client.get_request(ILOThermalSettings.ENDPOINT)
        termal_config = self._thermal_configuration(current_data, patches, before, after)
        self._fan_percent_minimum(current_data, patches, before, after)

        if not self.module.check_mode:
            if patches:
                self.api_client.patch_request(ILOThermalSettings.ENDPOINT, data=patches)

                if termal_config and self.module.params.get("wait_for_reset") > 0:
                    self.set_changes(before, after)
                    self.wait_for_ilo_reset(self.module.params.get("wait_for_reset"))

        self.set_changes(before, after)

    def _thermal_configuration(self, current_data, patches, before, after):
        if self.module.params.get("thermal_configuration"):
            current_val = self.get_recursive("Oem.Hpe.ThermalConfiguration", current_data)
            new_val = self.module.params.get("thermal_configuration")
            if new_val != current_val:
                self.result["patches"] = patches
                before["ThermalConfiguration"] = current_val
                after["ThermalConfiguration"] = new_val
                self.setdefault_recursive("Oem.Hpe", patches)["ThermalConfiguration"] = new_val
                return True
        return False

    def _fan_percent_minimum(self, current_data, patches, before, after):
        if self.module.params.get("fan_percent_minimum"):
            current_val = self.get_recursive("Oem.Hpe.FanPercentMinimum", current_data)
            new_val = self.module.params.get("fan_percent_minimum")
            if not 0 <= new_val <= 100:
                self.module.fail_json(
                    msg="fan_percent_minimum must be between 0 and 100. Invalid value '{0}'.".format(new_val)
                )
            if new_val != current_val:
                self.result["patches"] = patches
                before["FanPercentMinimum"] = current_val
                after["FanPercentMinimum"] = new_val
                self.setdefault_recursive("Oem.Hpe", patches)["FanPercentMinimum"] = new_val
                return True
        return False


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    ILOThermalSettings().main()


if __name__ == "__main__":
    main()
