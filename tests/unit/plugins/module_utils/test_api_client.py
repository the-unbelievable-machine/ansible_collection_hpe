# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type


import pytest
import unittest
from mock import MagicMock, patch


from ansible_collections.unbelievable.hpe.plugins.module_utils.api_client import JsonRestApiClient  # type: ignore # noqa: E501
from ansible_collections.unbelievable.hpe.plugins.module_utils.api_client import JsonRestApiResponse  # type: ignore # noqa: E501


@pytest.mark.parametrize(
    "api_base, expected",
    [
        ("", ""),
        ("/", ""),
        ("foo/bar", "/foo/bar"),
        ("/foo/bar", "/foo/bar"),
        ("foo/bar/", "/foo/bar"),
        ("/foo/bar/", "/foo/bar"),
    ],
)
def test_init_api_base(api_base, expected):
    api_client = JsonRestApiClient(protocol="http", host="host", port=443, api_base=api_base)
    assert expected == api_client.api_base


@pytest.mark.parametrize(
    "proxy, expected",
    [
        (None, None),
        ("test", {"http": "test", "https": "test"}),
    ],
)
def test_get_proxy(proxy, expected):
    api_client = JsonRestApiClient(protocol="http", host="host", port=443, proxy=proxy)
    assert expected == api_client.get_proxies()


@pytest.mark.parametrize(
    "username, password, expected",
    [
        (None, None, None),
        ("user", "passwd", ("user", "passwd")),
    ],
)
def test_get_auth(username, password, expected):
    api_client = JsonRestApiClient(protocol="http", host="host", port=443, username=username, password=password)
    assert expected == api_client.get_auth()


@pytest.mark.parametrize(
    "api_base, uri_path, expected",
    [
        ("/", "", ""),
        ("/", "/", ""),
        ("/", "/foo", "foo"),
        ("/", "/foo/bar", "foo/bar"),
        ("/foo/", "", ""),
        ("/foo/", "/", ""),
        ("/foo/", "/foo", ""),
        ("/foo/", "/foo/bar", "bar"),
        ("/foo/", "/foo/bar/test", "bar/test"),
        ("/foo/bar/", "/foo/bar", ""),
        ("/foo/bar/", "/foo/bar/", ""),
    ],
)
def test_cleanup_uri_path(api_base, uri_path, expected):
    api_client = JsonRestApiClient(protocol="http", host="host", port=443, api_base=api_base)
    assert expected == api_client.cleanup_uri_path(uri_path)


@pytest.mark.parametrize(
    "verb",
    [("GET"), ("PUT"), ("POST"), ("DELETE"), ("HEAD"), ("PATCH")],
)
def test__execute_request(verb):
    api_client = JsonRestApiClient("http", "host.domain", 443)
    api_client.cleanup_uri_path = MagicMock(return_value="mocked")
    api_client.get_headers = MagicMock(return_value={"header": "header"})
    api_client.get_auth = MagicMock(return_value={"user": "password"})
    api_client.validate_certs = "validate"
    payload = {"pay": "load"}
    headers = {"key": "value", "Content-Type": "application/json"}
    response = {"response": "data"}
    expected = JsonRestApiResponse(headers, response)

    with patch("requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=response)
        mock_response.headers = headers
        mock_request.return_value = mock_response
        data = api_client._execute_request(verb, "", data=payload, timeout=123)
        mock_request.assert_called_once_with(
            verb,
            url="http://host.domain:443/mocked",
            headers=api_client.get_headers(),
            auth=api_client.get_auth(),
            verify=api_client.validate_certs,
            json=payload,
            timeout=123,
            proxies=api_client.get_proxies(),
        )
        print(data)
        assert expected == data


class TestJsonRestApiClient(unittest.TestCase):
    def setUp(self):
        self.api_client = JsonRestApiClient(
            "http", "host.domain", 443, username="user", password="password", proxy="proxy"
        )
        self.payload = {"pay": "load"}
        self.response = {"response": "data"}
        self.header = {"key": "value"}
        self.api_client._execute_request = MagicMock(return_value=JsonRestApiResponse(self.header, self.response))

    def test_get_headers(self):
        self.assertEqual(
            {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
            },
            self.api_client.get_headers(),
        )

    def test_get_request(self):
        data = self.api_client.get_request("test", timeout=123)
        self.api_client._execute_request.assert_called_once_with("GET", "test", data=None, timeout=123)
        self.assertEqual(self.response, data)

    def test_put_request(self):
        data = self.api_client.put_request("test", self.payload, timeout=123)
        self.api_client._execute_request.assert_called_once_with("PUT", "test", data=self.payload, timeout=123)
        self.assertEqual(self.response, data)

    def test_post_request(self):
        data = self.api_client.post_request("test", self.payload, timeout=123)
        self.api_client._execute_request.assert_called_once_with("POST", "test", data=self.payload, timeout=123)
        self.assertEqual(self.response, data)

    def test_delete_request(self):
        data = self.api_client.delete_request("test", self.payload, timeout=123)
        self.api_client._execute_request.assert_called_once_with("DELETE", "test", data=self.payload, timeout=123)
        self.assertEqual(self.response, data)

    def test_head_request(self):
        data = self.api_client.head_request("test", timeout=123)
        self.api_client._execute_request.assert_called_once_with("HEAD", "test", data=None, timeout=123)
        self.assertEqual(self.response, data)

    def test_patch_request(self):
        data = self.api_client.patch_request("test", self.payload, timeout=123)
        self.api_client._execute_request.assert_called_once_with("PATCH", "test", data=self.payload, timeout=123)
        self.assertEqual(self.response, data)
