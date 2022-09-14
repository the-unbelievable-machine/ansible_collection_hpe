#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: imc_configfiles_info
author:
    - Janne K. Olesen (@jakrol)

short_description: List of content (config files) of a folder.
description:
    - List of content (config files) of a folder.

options:
    folder_id:
        description:
            - Folder id to list content of. Default -1 is the root folder. Mutually exclusive with folder_name.
        type: int
        required: no
        default: -1
        version_added: 3.3.0
    folder_name:
        description:
            - Folder name to list content of. in / should be placed in. Mutually exclusive with folder_id.
        type: str
        required: no
        version_added: 3.3.0
extends_documentation_fragment:
    - unbelievable.hpe.imc_api_client
"""

EXAMPLES = r"""
- name: Get config files
  unbelievable.imc_configfiles_info:
    hostname: https://imc.server.domain
    username: user
    password: secret
  register: devices
"""

RETURN = r"""
content:
    description:
        - Folder content. Always present, but may be empty.
    returned: success
    type: list
    elements: dict
folder_id:
    description:
        - Folder id that was queried.
    returned: success
    type: int
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.imc import ImcModuleBase  # type: ignore # noqa: E501


class ImcConfigFilesInfo(ImcModuleBase):
    def argument_spec(self):
        additional_spec = dict(
            folder_id=dict(type="int", required=False, default=-1),
            folder_name=dict(type="str", required=False),
        )
        spec = dict()
        spec.update(super(ImcConfigFilesInfo, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def module_def_extras(self):
        return dict(mutually_exclusive=[["folder_id", "folder_name"]])

    def run(self):
        folder_id = self.get_folder_id()
        self.result["folder_id"] = folder_id
        self.result["content"] = self.api_client.list_folder(folder_id)
        self.result["total"] = len(self.result["content"])


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    ImcConfigFilesInfo().main()


if __name__ == "__main__":
    main()
