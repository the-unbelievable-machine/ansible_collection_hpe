# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
    hostname:
        description:
            - The hostname or IP address of the iLO server
        type: str
        required: yes
        aliases: [ name, ilo_server ]
        version_added: 1.0.0
    username:
        description:
            - The username of the iLO server
        required: yes
        type: str
        aliases: [ user, ilo_user ]
        version_added: 1.0.0
    password:
        description:
            - The password of the iLO server
        required: yes
        type: str
        aliases: [ passwd, ilo_password ]
        version_added: 1.0.0
    validate_certs:
        description:
            - Verify SSL certificate if using HTTPS.
        type: bool
        required: no
        default: yes
        version_added: 1.0.0
    protocol:
        description:
            - Protocol to use when connecting to the iLO server
            - Mainly for testing / devloping.
        type: str
        choices: [ http, https ]
        default: https
        aliases: [ ilo_protocol ]
        version_added: 1.0.0
    port:
        description:
            - Port to use when connecting to the iLO server
        type: int
        default: 443
        aliases: [ ilo_port ]
        version_added: 1.0.0
    proxy:
        description:
            - Proxy to use when connecting to the iLO server.
            - if requests where installed like 'pip install requests[socks]', then socks proxies
              are supported.
        type: str
        version_added: 1.0.0
"""
