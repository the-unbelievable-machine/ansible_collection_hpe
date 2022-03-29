# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
import unittest

from ansible_collections.unbelievable.hpe.plugins.module_utils.redfish import RedfishApiClient, ApiHelper  # type: ignore # noqa: E501


@pytest.mark.parametrize(
    "path, d, value, d_after",
    [
        ("a", {}, {}, {"a": {}}),
        ("a.b", {}, {}, {"a": {"b": {}}}),
        ("a.b.c", {}, {}, {"a": {"b": {"c": {}}}}),
        ("a.b", {"a": {"b": "c"}}, "c", {"a": {"b": "c"}}),
        ("a.b.d", {"a": {"b": {"c": "c1"}}}, {}, {"a": {"b": {"c": "c1", "d": {}}}}),
    ],
)
def test_setdefault_recursive(path, d, value, d_after):
    val = ApiHelper.setdefault_recursive(path, d)
    assert val == value
    assert d == d_after


@pytest.mark.parametrize(
    "path, d, value",
    [
        ("a.b.c", {}, None),
        ("a.b.c", {"a": {}}, None),
        ("a.b.c", {"a": {"b": {}}}, None),
        ("a.b.c", {"a": {"b": {"c": "d"}}}, "d"),
    ],
)
def test_get_recursive(path, d, value):
    val = ApiHelper.get_recursive(path, d)
    assert val == value


class TestRedfishApiClient(unittest.TestCase):
    def setUp(self):
        self.api_client = RedfishApiClient(
            "http", "host.domain", 443, username="user", password="password", proxy="proxy"
        )

    def test_api_base(self):
        self.assertEqual("/redfish/v1", self.api_client.api_base)
