# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.unbelievable.hpe.plugins.module_utils.logger import SilentLogger  # type: ignore
from ansible_collections.unbelievable.hpe.plugins.module_utils.api_client import (  # type: ignore
    JsonRestApiClient,
    ModuleBase,
)

import time


class RedfishApiClient(JsonRestApiClient):

    API_BASE = "/redfish/v1/"

    def __init__(
        self,
        protocol,
        host,
        port,
        username,
        password,
        validate_certs=True,
        proxy=None,
        logger=SilentLogger(),
    ):
        super(RedfishApiClient, self).__init__(
            protocol=protocol,
            host=host,
            port=port,
            api_base=RedfishApiClient.API_BASE,
            username=username,
            password=password,
            validate_certs=validate_certs,
            proxy=proxy,
            logger=logger,
        )


class RedfishModuleBase(ModuleBase):
    def __init__(self):
        super(RedfishModuleBase, self).__init__(param_alias_prefix="ilo")

    def argument_spec(self):
        additional_spec = dict()
        spec = dict()
        spec.update(super(RedfishModuleBase, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def wait_for_ilo_reset(self, seconds_to_wait, param_name="wait_for_reset"):
        time.sleep(5)  # wait 5 seconds for iLO reset to start
        end = time.time() + seconds_to_wait
        data = None
        while time.time() <= end:
            try:
                data = self.api_client.get_request("", timeout=5)
                break
            except BaseException:
                pass
        if not data:
            self.module.fail_json(
                msg=(
                    "Waiting for iLO reset timed out. Changes should be applied successfully, "
                    "but iLO reset still seems to be in progress. Increasing {0}={1} "
                    "should fix this problem."
                ).format(param_name, seconds_to_wait)
            )

    def get_module_api_client(self, protocol, host, port, username, password, validate_certs, proxy, logger):
        return RedfishApiClient(
            protocol=protocol,
            host=host,
            port=port,
            username=username,
            password=password,
            validate_certs=validate_certs,
            proxy=proxy,
            logger=logger,
        )


class ApiHelper(object):
    @staticmethod
    def setdefault_recursive(path, d):
        """Split 'path' on '.' and recursively calls setdefault on nested dict d"""
        value = d if d is not None else dict()
        for key in path.split("."):
            value = value.setdefault(key, dict())
        return value

    @staticmethod
    def get_recursive(path, d):
        """Split 'path' on '.' and recursively get value from nested dict d"""
        if d is None:
            return None
        value = d
        for key in path.split("."):
            if key in value:
                value = value[key]
            else:
                return None
        return value
