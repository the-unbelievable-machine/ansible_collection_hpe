# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type


import unittest
from mock import MagicMock, call


from ansible_collections.unbelievable.hpe.plugins.module_utils.oneview import OneViewApiClient  # type: ignore # noqa: E501


class TestOneViewApiClient(unittest.TestCase):
    def setUp(self):
        self.api_client = OneViewApiClient(
            "http", "host.domain", 443, username="user", password="password", proxy="proxy"
        )

    def test_api_base(self):
        self.assertEqual("/rest", self.api_client.api_base)

    def test_get_headers_api_version(self):
        self.api_client.api_version = "api_version"
        self.api_client.session = None
        headers = self.api_client.get_headers()
        self.assertDictContainsSubset({"X-API-Version": "api_version"}, headers)

    def test_get_headers_no_session(self):
        self.api_client.session = None
        headers = self.api_client.get_headers()
        self.assertNotIn("Auth", headers)

    def test_get_headers_session(self):
        self.api_client.session = "secret"
        headers = self.api_client.get_headers()
        self.assertDictContainsSubset({"Auth": "secret"}, headers)

    def test_login(self):
        payload = {"userName": "user", "password": "password", "loginMsgAck": "true"}
        self.api_client._execute_request = MagicMock(return_value={"sessionID": "session-id"})
        self.api_client.login()
        self.api_client._execute_request.assert_called_once_with("POST", "/login-sessions", data=payload, timeout=None)
        self.assertEqual("session-id", self.api_client.session)

    def test_logout_not_loggedin(self):
        self.api_client.session = None
        self.api_client._execute_request = MagicMock()
        self.api_client.logout()
        self.assertFalse(self.api_client._execute_request.called)
        self.assertIsNone(self.api_client.session)

    def test_logout(self):
        self.api_client.session = "secret"
        self.api_client._execute_request = MagicMock()
        self.api_client.logout()
        self.api_client._execute_request.assert_called_once_with("DELETE", "/login-sessions", data=None, timeout=None)
        self.assertIsNone(self.api_client.session)

    def test__collect_members(self):
        return_values = [
            {"members": [1, 2], "nextPageUri": "/rest/something/1"},
            {"members": [3, 4], "nextPageUri": "/rest/something/2"},
            {"members": [5]},
        ]
        self.api_client._execute_request = MagicMock(side_effect=return_values)
        members = self.api_client._collect_members("/something")
        self.api_client._execute_request.assert_has_calls(
            [
                call("GET", "/something", data=None, timeout=None),
                call("GET", "/rest/something/1", data=None, timeout=None),
                call("GET", "/rest/something/2", data=None, timeout=None),
            ]
        )
        self.assertEqual([1, 2, 3, 4, 5], members)

    def test_list_racks(self):
        return_values = [
            {"members": [1, 2], "nextPageUri": "/rest/racks/1"},
            {"members": [3, 4], "nextPageUri": "/rest/racks/2"},
            {"members": [5]},
        ]
        self.api_client._execute_request = MagicMock(side_effect=return_values)
        racks = self.api_client.list_racks()
        self.api_client._execute_request.assert_has_calls(
            [
                call("GET", "/racks", data=None, timeout=None),
                call("GET", "/rest/racks/1", data=None, timeout=None),
                call("GET", "/rest/racks/2", data=None, timeout=None),
            ]
        )
        self.assertEqual([1, 2, 3, 4, 5], racks)

    def test_list_server_hardware(self):
        return_values = [
            {"members": [1, 2], "nextPageUri": "/rest/server-hardware/1"},
            {"members": [3, 4], "nextPageUri": "/rest/server-hardware/2"},
            {"members": [5]},
        ]
        self.api_client._execute_request = MagicMock(side_effect=return_values)
        racks = self.api_client.list_server_hardware()
        self.api_client._execute_request.assert_has_calls(
            [
                call("GET", "/server-hardware", data=None, timeout=None),
                call("GET", "/rest/server-hardware/1", data=None, timeout=None),
                call("GET", "/rest/server-hardware/2", data=None, timeout=None),
            ]
        )
        self.assertEqual([1, 2, 3, 4, 5], racks)
