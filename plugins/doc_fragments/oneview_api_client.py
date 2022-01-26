# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    protocol:
        description:
            - Protocol to use when connecting to the OneView server
            - Mainly for testing / devloping.
        type: str
        choices: [ http, https ]
        default: https
        aliases: [ oneview_protocol ]
        version_added: 2.0.0
    hostname:
        description:
            - The hostname or IP address of the OneView server
        type: str
        required: yes
        aliases: [ host, url, oneview_url ]
        version_added: 2.0.0
    port:
        description:
            - Port to use when connecting to the OneView server
        type: int
        default: 443
        aliases: [ oneview_port ]
        version_added: 2.0.0
    username:
        description:
            - OneView api authentication user.
        required: yes
        type: str
        aliases: [user, oneview_user]
        version_added: 1.0.0
    password:
        description:
            - OneView authentication password.
        required: yes
        type: str
        aliases: [passwd, oneview_password]
        version_added: 1.0.0
    validate_certs:
        description:
            - Verify SSL certificate if using HTTPS.
        type: bool
        default: yes
        version_added: 1.0.0
    proxy:
        description:
            - Proxy to use when accessing OneView API.
            - if requests where installed like 'pip install requests[socks]', then socks proxies
                are supported.
            - "example: http://localhost:8080"
        required: no
        type: str
        version_added: 1.0.0
    api_version:
        description:
            - OneView API version.
        default: 2400
        type: int
        aliases: [oneview_api_version]
        version_added: 2.0.0
"""
