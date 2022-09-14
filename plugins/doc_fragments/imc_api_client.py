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
            - Protocol to use when connecting to the IMC server
            - Mainly for testing / devloping.
        type: str
        choices: [ http, https ]
        default: https
        aliases: [ imc_protocol ]
        version_added: 3.3.0
    hostname:
        description:
            - The hostname or IP address of the IMC server
        type: str
        required: yes
        aliases: [ name, host, server, imc_host, imc_server ]
        version_added: 3.3.0
    port:
        description:
            - Port to use when connecting to the IMC server
        type: int
        default: 443
        aliases: [ imc_port ]
        version_added: 3.3.0
    username:
        description:
            - IMC api authentication user.
        required: yes
        type: str
        aliases: [user, imc_user]
        version_added: 3.3.0
    password:
        description:
            - IMC authentication password.
        required: yes
        type: str
        aliases: [passwd, imc_password]
        version_added: 3.3.0
    validate_certs:
        description:
            - Verify SSL certificate if using HTTPS.
        type: bool
        default: yes
        version_added: 3.3.0
    proxy:
        description:
            - Proxy to use when accessing IMC API.
            - if requests where installed like 'pip install requests[socks]', then socks proxies
                are supported.
            - "example: http://localhost:8080"
        required: no
        type: str
        version_added: 3.3.0
"""
