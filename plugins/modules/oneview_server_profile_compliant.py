#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oneview_server_profile_compliant
author:
    - Janne K. Olesen (@jakrol)

short_description: Content of /rest/server-profiles endpoint of OneView
description:
    - Content of /rest/server-profiles endpoint of OneView

options:

    profile_name:
        description:
            - Profile name. Either profile_name or profile_uuid must be set.
        required: no
        type: str

    profile_uuid:
        description:
            - Profile uuid. Either profile_name or profile_uuid must be set.
        required: no
        type: str

    wait_timeout:
        description:
            - Max seconds to wait for profile becomes compliant.
            - 0 not wait at all.
        type: int
        required: no
        default: 120

extends_documentation_fragment:
    - unbelievable.hpe.oneview_api_client
"""

EXAMPLES = r"""
- name: Get server-profiles
  unbelievable.oneview_server_profile_compliant:
    hostname: https://oneview.server.domain
    username: user
    password: secret
    profile_name: myprofile
  register: result
"""

RETURN = r"""
profile_uuid:
    description:
        - Profile uuid used.
    returned: aways
    type: str
task_id:
    description:
        - OneView task id associated with this change.
    returned: if changed
    type: str
task_result:
    description:
        - OneView rest-api task status.
    returned: if changed
    type: dict
compliance_preview:
    description:
        - OneView compliance preview.
    returned: if changed and failed.
    type: dict
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import OneviewModuleBase, ApiHelper  # type: ignore # noqa: E501


class OneViewServerProfileCompliant(OneviewModuleBase):
    def argument_spec(self):
        additional_spec = dict(
            profile_name=(dict(type="str", required=False)),
            profile_uuid=(dict(type="str", required=False)),
            wait_timeout=dict(type="int", required=False, default=120),
        )
        spec = dict()
        spec.update(super(OneViewServerProfileCompliant, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def module_def_extras(self):
        return dict(required_one_of=[["profile_name", "profile_uuid"]])

    def run(self):
        try:
            self.api_client.login()
            profile = self.get_profile()
            profile_uuid = ApiHelper.ServerProfile.get_profile_uuid(profile)

            self.result["profile_uuid"] = profile_uuid
            status_before = profile["templateCompliance"]

            before = dict()
            before["templateCompliance"] = status_before

            after = dict()
            after["templateCompliance"] = "Compliant"

            self.set_changes(before, after)

            if not self.module.check_mode and status_before != "Compliant":
                resp_headers = self.api_client.server_profile_update(profile_uuid).headers
                self.process_task(profile_uuid, resp_headers["location"].split("/")[-1])

        finally:
            self.api_client.logout()

    def get_profile(self):
        if self.module.params.get("profile_id"):
            return self.api_client.get_server_profile(self.module.params.get("profile_id"))
        else:
            profiles = self.api_client.list_server_profiles(
                "'name' = '{0}'".format(self.module.params.get("profile_name"))
            )
            if not profiles:
                self.module.fail_json(msg="Server profile  not found")
            if len(profiles) > 1:
                self.module.fail_json(msg="Multiple server profiles found")
            return profiles[0]

    def process_task(self, profile_id, task_id):
        self.result["task_id"] = task_id
        timeout = self.module.params.get("wait_timeout")
        if timeout > 0:
            task = self.api_client.wait_for_task(task_id, seconds_to_wait=timeout)
            self.result["task_result"] = task
            if task["taskState"] != "Completed":
                compliance_preview = self.api_client.get_server_profile_compliant_preview(profile_id)
                self.module.fail_json(msg=task["taskStatus"], task=task, compliance_preview=compliance_preview)


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    OneViewServerProfileCompliant().main()


if __name__ == "__main__":
    main()
