#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: imc_configdirectory
author:
    - Janne K. Olesen (@jakrol)

short_description: Create/Delete config file directory
description:
    - Create/Delete config files.
    - IMC api does not support updating, instead files are deleted and recreated if necessary. This will
      change the file_id

options:
    parent_folder_id:
        description:
            - Folder id of the parent folder. Mutually exclusive with parent_folder_name.
        type: int
        required: no
        default: -1
        version_added: 3.3.0
    parent_folder_name:
        description:
            - Folder name of the parent folder. Mutually exclusive with folder_id.
        type: str
        required: no
        version_added: 3.3.0
    folder_name:
        description:
            - File name. Leading '/' is ignored.
        type: str
        required: yes
        version_added: 3.3.0
    state:
        description:
            - "present: create folder."
            - "absent: delete folder."
        type: str
        choices: [present, absent]
        required: no
        default: "present"
        version_added: 3.3.0
    recursive:
        description:
            - Unless true, deleting non empty directories will fail.
        type: bool
        required: no
        default: False
        version_added: 3.3.0

extends_documentation_fragment:
    - unbelievable.hpe.imc_api_client
"""

EXAMPLES = r"""
- name: Create config directory
  unbelievable.imc_configdirectory:
    hostname: https://imc.server.domain
    username: user
    password: secret
    state: present
    folder_name: my-dir
"""

RETURN = r"""
parent_folder_id:
    description:
        - Parent folder id.
    returned: success
    type: int
folder_id:
    description:
        - Folder id. Id of the folder.
        - If state is absent, id of the deleted folder or None, if folder does not exist.
        - If state is present, this is the id of folder. 'check_mode' if module is running in check_mode.
    returned: success
    type: int
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.imc import ImcApiClient, ImcModuleBase  # type: ignore # noqa: E501


class ImcConfigDirectory(ImcModuleBase):
    def argument_spec(self):
        additional_spec = dict(
            parent_folder_id=dict(type="int", required=False, default=-1),
            parent_folder_name=dict(type="str", required=False),
            folder_name=dict(type="str", required=True),
            recursive=dict(type="bool", required=False, default=False),
            state=dict(type="str", choices=["present", "absent"], required=False, default="present"),
        )
        spec = dict()
        spec.update(super(ImcConfigDirectory, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def module_def_extras(self):
        return dict(mutually_exclusive=[["parent_folder_id", "parent_folder_name"]])

    def run(self):

        parent_folder_id = self.get_folder_id(param_name_name="parent_folder_name", param_name_id="parent_folder_id")
        folder_name = self.module.params.get("folder_name")
        folder_id = self.api_client.get_file_id(parent_folder_id, folder_name, ImcApiClient.FILE_TYPE_FOLDER)

        self.result["parent_folder_id"] = parent_folder_id
        self.result["folder_id"] = folder_id

        state = self.module.params.get("state")
        if state == "absent":
            self.delete_folder(folder_id)
        else:
            self.create_folder(parent_folder_id, folder_id, folder_name)

    def delete_folder(self, folder_id):
        self.set_changed(folder_id is not None)
        if folder_id:
            if not self.module.params.get("recursive"):
                content = self.api_client.list_folder(folder_id)
                if content:
                    self.module.fail_json(
                        (
                            "msg: Directory with id: {0} contains {1} items. " "Use recursive: true to delete anyway"
                        ).format(folder_id, len(content))
                    )
            if not self.module.check_mode:
                self.api_client.delete_folder(folder_id)

    def create_folder(self, parent_folder_id, folder_id, folder_name):
        self.set_changed(folder_id is None)
        if not folder_id:
            folder_id = "check_mode"
            if not self.module.check_mode:
                folder_id = self.api_client.create_folder(parent_folder_id, folder_name)
            self.result["folder_id"] = folder_id


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    ImcConfigDirectory().main()


if __name__ == "__main__":
    main()
