#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: oneview_server_profile_info
author:
    - Janne K. Olesen (@jakrol)

short_description: Content of /rest/server-profiles endpoint of OneView
description:
    - Content of /rest/server-profiles endpoint of OneView

options:
    filter:
        description:
            - OneView rest-api filter
            - see https://techlibrary.hpe.com/docs/enterprise/servers/oneview6.0/cicf-api/en/index.html#stdparams
        required: no
        type: str

extends_documentation_fragment:
    - unbelievable.hpe.oneview_api_client
"""

EXAMPLES = r"""
- name: Get server-profiles
  unbelievable.oneview_server_profile_info:
    hostname: https://oneview.server.domain
    username: user
    password: secret
  register: result
"""

RETURN = r"""
profiles:
    description:
        - List of server profile. Always present, but may be empty.
    returned: success
    type: list
    elements: dict
"""


from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import OneviewModuleBase, ApiHelper  # type: ignore # noqa: E501


class OneViewServerProfileInfo(OneviewModuleBase):
    def argument_spec(self):
        additional_spec = dict(
            filter=dict(type="str", required=False),
        )
        spec = dict()
        spec.update(super(OneViewServerProfileInfo, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def init(self):
        self.filter = self.module.params.get("filter")

    def run(self):
        try:
            self.api_client.login()
            server_profiles_raw = self.api_client.list_server_profiles(self.filter)
            self.result["profiles"] = self.process_server_profiles(server_profiles_raw)
        finally:
            self.api_client.logout()

    def process_server_profiles(self, raw):
        profiles = []
        for r in raw:
            p = r.copy()
            p["_profile_uuid"] = ApiHelper.ServerProfile.get_profile_uuid(r)
            profiles.append(p)
        return profiles


def main():
    # just to keep ansibles sanity test 'validate_modules' happy
    OneViewServerProfileInfo().main()


if __name__ == "__main__":
    main()
