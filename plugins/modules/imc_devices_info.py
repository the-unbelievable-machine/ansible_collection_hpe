#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: imc_devices_info
author:
    - Janne K. Olesen (@jakrol)

short_description: Content of /plat/res/device endpoint of IMC
description:
    - Content of /plat/res/device endpoint of IMC

extends_documentation_fragment:
    - unbelievable.hpe.imc_api_client
"""

EXAMPLES = r"""
- name: Get devices_info
  unbelievable.imc_devices_info:
    hostname: https://imc.server.domain
    username: user
    password: secret
  register: devices
"""

RETURN = r"""
devices:
    description:
        - List of devices. Always present, but may be empty.
    returned: success
    type: list
    elements: dict
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.imc import ImcModuleBase  # type: ignore # noqa: E501


class ImcDevicesInfo(ImcModuleBase):
    def run(self):
        self.result["devices"] = self.api_client.list_devices()


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    ImcDevicesInfo().main()


if __name__ == "__main__":
    main()
