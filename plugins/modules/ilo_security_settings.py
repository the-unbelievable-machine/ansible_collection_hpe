#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ilo_security_settings
author:
    - Janne K. Olesen (@jakrol)

short_description: Manage iLO Security settings
description:
    - Manage iLO Security settings

options:
    security_state:
        description:
            - Security state
            - Currently only switching between Production <--> HighSecurity is allowed.
        type: str
        choices: [ Production, HighSecurity ]
        required: yes
        version_added: 1.0.0

extends_documentation_fragment:
    - unbelievable.hpe.redfish_api_client
"""

EXAMPLES = r"""
- name: Set iLO SecurityState
  unbelievable.hpe.ilo_security_settings:
      security_state: HighSecurity
      hostname: '{{ inventory_hostname }}'
      user: user
      password: secret
      delegate_to: localhost
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.redfish_api_client import RedfishModuleBase  # type: ignore # noqa: E501


class ILOSecuritySettings(RedfishModuleBase):

    ENDPOINT = "Managers/1/SecurityService"

    def additional_argument_spec(self):
        return dict(
            security_state=dict(type="str", choices=["Production", "HighSecurity"], required=True),
        )

    def run(self):

        before = dict()
        after = dict()
        patches = dict()

        current_data = self.api_client.get_request(ILOSecuritySettings.ENDPOINT)
        self._security_state(current_data, patches, before, after)

        if not self.module.check_mode:
            if patches:
                self.api_client.patch_request(ILOSecuritySettings.ENDPOINT, data=patches)

        self.set_changes(before, after)

    def _security_state(self, current_data, patches, before, after):
        if self.module.params.get("security_state"):
            current_val = current_data["SecurityState"]
            new_val = self.module.params.get("security_state")
            if new_val != current_val:
                if current_val not in ["Production", "HighSecurity"]:
                    self.module.fail_json(
                        msg="Changing current value for security_state '{0}' is not supported.".format(current_val)
                    )
                self.result["patches"] = patches
                before["SecurityState"] = current_val
                after["SecurityState"] = new_val
                patches["SecurityState"] = new_val
                return True
        return False


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    ILOSecuritySettings().main()


if __name__ == "__main__":
    main()
