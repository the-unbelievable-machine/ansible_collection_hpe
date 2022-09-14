#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: imc_configfile
author:
    - Janne K. Olesen (@jakrol)

short_description: Create/Delete config files
description:
    - Create/Delete config files.
    - IMC api does not support updating, instead files are deleted and recreated if necessary. This will
      change the file_id

options:
    folder_id:
        description:
            - Folder id of the folder the file is in / should be placed in. Mutually exclusive with folder_name.
        type: int
        required: no
        default: -1
        version_added: 3.3.0
    folder_name:
        description:
            - Folder name of the folder the file is in / should be placed in. Mutually exclusive with folder_id.
        type: str
        required: no
        version_added: 3.3.0
    file_name:
        description:
            - File name. Leading '/' is ignored.
        type: str
        required: yes
        version_added: 3.3.0
    file_type:
        description:
            - IMC file type
        type: str
        choices: [file, segment, cli_script]
        required: yes
        version_added: 3.3.0
    state:
        description:
            - "present: create or update config file. Requires content."
            - "absent: delete config file."
        type: str
        choices: [present, absent]
        required: no
        default: "present"
        version_added: 3.3.0
    content:
        description:
            - File content. Required if state is "present".
        type: str
        required: no
        version_added: 3.3.0


extends_documentation_fragment:
    - unbelievable.hpe.imc_api_client
"""

EXAMPLES = r"""
- name: Create config file
  unbelievable.imc_configfile:
    hostname: https://imc.server.domain
    username: user
    password: secret
    state: present
    file_name: myconfig.txt
    content:
"""

RETURN = r"""
folder_id:
    description:
        - Folder id. Id of the folder the file was placed in.
    returned: success
    type: int
file_id:
    description:
        - Id of the file created if state is present. 'check_mode' if file is running in check mode.
        - Id of the file deleted if state is absent. None if file does not exist.
    returned: success
    type: int
file_id_deleted:
    description:
        - If state is absent, this is the same as file_id
        - If state is present, this is the id of replaced file
    returned: success
    type: int
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.imc import ImcModuleBase  # type: ignore # noqa: E501


class ImcConfigFile(ImcModuleBase):
    def argument_spec(self):
        additional_spec = dict(
            folder_id=dict(type="int", required=False, default=-1),
            folder_name=dict(type="str", required=False),
            file_name=dict(type="str", required=True),
            file_type=dict(type="str", choices=["file", "segment", "cli_script"], required=True),
            state=dict(type="str", choices=["present", "absent"], required=False, default="present"),
            content=dict(type="str", required=False),
        )
        spec = dict()
        spec.update(super(ImcConfigFile, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def module_def_extras(self):
        return dict(mutually_exclusive=[["folder_id", "folder_name"]], required_if=[["state", "present", ["content"]]])

    def run(self):

        folder_id = self.get_folder_id()
        file_name = self.module.params.get("file_name")
        file_type = self.get_file_type()
        file_id = self.api_client.get_file_id(folder_id, file_name, file_type)

        self.result["folder_id"] = folder_id

        state = self.module.params.get("state")
        if state == "absent":
            self.delete_file(file_id)
        elif file_id:  # state == present and file exists
            self.update_file(folder_id, file_name, file_type, file_id)
        else:  # state == present and file does not exist
            self.create_file(folder_id, file_name, file_type)

    def delete_file(self, file_id):
        self.result["file_id"] = file_id
        self.result["file_id_deleted"] = file_id
        self.set_changed(file_id is not None)
        if file_id and not self.module.check_mode:
            self.api_client.delete_file(file_id)

    def create_file(self, folder_id, file_name, file_type):
        new_content = self.module.params.get("content")
        self.set_changes(None, new_content)
        file_id = "check_mode"
        if not self.module.check_mode:
            file_id = self.api_client.create_file(folder_id, file_name, file_type, new_content)
        self.result["file_id"] = file_id

    def update_file(self, folder_id, file_name, file_type, file_id):

        current_content = self.api_client.get_file(file_id)["content"] if file_id else ""
        new_content = self.module.params.get("content")
        self.set_changes(current_content, new_content)

        self.result["file_id"] = file_id
        if new_content != current_content:
            self.delete_file(file_id)
            self.create_file(folder_id, file_name, file_type)


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    ImcConfigFile().main()


if __name__ == "__main__":
    main()
