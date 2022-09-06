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


class OneViewApiClient(JsonRestApiClient):
    API_BASE = "/rest"

    def __init__(
        self,
        protocol,
        host,
        port,
        username,
        password,
        validate_certs=True,
        proxy=None,
        api_version=2400,
        logger=SilentLogger(),
    ):
        super(OneViewApiClient, self).__init__(
            protocol=protocol,
            host=host,
            port=port,
            api_base=OneViewApiClient.API_BASE,
            username=username,
            password=password,
            validate_certs=validate_certs,
            proxy=proxy,
            logger=logger,
        )

        self.api_version = api_version
        self.session = None

    def get_headers(self):
        headers = dict(JsonRestApiClient.get_headers(self))
        headers["X-API-Version"] = str(self.api_version)
        if self.session:
            headers["Auth"] = self.session
        return headers

    def login(self):
        payload = {"userName": self.username, "password": self.password, "loginMsgAck": "true"}
        json = self.post_request("/login-sessions", payload)
        self.session = json.get("sessionID")
        self.logger.debug("OneViewApiClient: Login successful")

    def logout(self):
        if self.session:
            self.delete_request("/login-sessions")
            self.session = None
            self.logger.debug("OneViewApiClient: Logout successful")

    def list_server_hardware(self, filter=None):
        next_url = "/server-hardware"
        if filter:
            next_url += '?filter="' + filter + '"'
        return self._collect_members(next_url)

    def list_server_profiles(self, filter=None):
        next_url = "/server-profiles"
        if filter:
            next_url += '?filter="' + filter + '"'
        return self._collect_members(next_url)

    def get_server_profile(self, id):
        return self.get_request("/server-profiles/" + id)

    def server_profile_update(self, profile_id):
        payload = [{"op": "replace", "path": "/templateCompliance", "value": "Compliant"}]
        return self.patch_request_with_headers("/server-profiles/" + profile_id, payload)

    def get_server_profile_compliant_preview(self, profile_id):
        return self.get_request("/server-profiles/{0}/compliance-preview".format(profile_id))

    def wait_for_task(self, task_id, seconds_to_wait=30):
        url = "tasks/" + task_id
        end = time.time() + seconds_to_wait
        data = None
        while time.time() <= end:
            data = self.get_request(url, timeout=5)
            if data["taskState"] in [
                "Cancelled",
                "Cancelling",
                "Completed",
                "Error",
                "Killed",
                "Terminated",
                "Unknown",
            ]:
                break
        return data

    def list_racks(self):
        return self._collect_members("/racks")

    def _collect_members(self, url):
        next_url = url
        members = []
        while True:
            self.logger.debug("OneViewApiClient: {0}".format(next_url))
            data = self.get_request(next_url)
            if data["members"]:
                members += data["members"]
                next_url = data.get("nextPageUri", "")
                if not next_url:
                    break
            else:
                break
        return members


class OneviewModuleBase(ModuleBase):
    def __init__(self):
        super(OneviewModuleBase, self).__init__(param_alias_prefix="oneview")

    def argument_spec(self):
        additional_spec = dict(api_version=dict(type="int", default=2400, aliases=["oneview_api_version"]))
        spec = dict()
        spec.update(super(OneviewModuleBase, self).argument_spec())
        spec.update(additional_spec)
        return spec

    def get_module_api_client(self, protocol, host, port, username, password, validate_certs, proxy, logger):
        return OneViewApiClient(
            protocol=protocol,
            host=host,
            port=port,
            username=username,
            password=password,
            validate_certs=validate_certs,
            api_version=self.module.params.get("api_version"),
            proxy=proxy,
            logger=logger,
        )


class ApiHelper(object):
    @staticmethod
    def copy_entries(src, entries):
        result = {}
        for entry in entries:
            val = None
            if entry == "rs_mpHostName":
                val = ApiHelper.Host.mpHostName(src)
            elif entry == "rs_mpIpAddress4":
                val = ApiHelper.Host.mpHostIp4(src)
            elif entry == "rs_mpIpAddress6":
                val = ApiHelper.Host.mpHostIp6(src)
            else:
                val = src.get(entry, None)
            if val is not None:
                result[entry] = val
        return result

    @staticmethod
    def copy_path(src, path):
        v = src
        for s in filter(None, path.split("/")):
            v = v[s]
        return v

    class Host(object):
        @staticmethod
        def mpHostName(host):
            name = None
            if host:
                if "mpHostInfo" in host:
                    name = host.get("mpHostInfo", {}).get("mpHostName", None)
                elif "mpDnsName" in host:
                    name = host.get("mpDnsName", None)
            return name

        @staticmethod
        def mpHostIp4(host):
            return ApiHelper.Host._mpHostIp(host, ".")

        @staticmethod
        def mpHostIp6(host):
            return ApiHelper.Host._mpHostIp(host, ":")

        @staticmethod
        def _mpHostIp(host, identifier):
            address = None
            if host:
                if "mpHostInfo" in host:
                    for a in host.get("mpHostInfo", {}).get("mpIpAddresses", []):
                        if a.get("type", "") == "Static" and identifier in a.get("address", ""):
                            address = a.get("address")
                elif "mpIpAddress" in host and identifier in host.get("mpIpAddress", ""):
                    address = host.get("mpIpAddress", None)
            return address

    class ServerProfile(object):
        @staticmethod
        def get_profile_uuid(server_profile):
            if "profileUUID" in server_profile:
                return server_profile["profileUUID"]
            return server_profile["uri"].split("/")[-1]

        @staticmethod
        def get_status(server_profile):
            status = {}
            status["refreshState"] = server_profile["refreshState"]
            for k, v in ApiHelper.ServerProfile.components.items():
                status[k] = ApiHelper.copy_path(server_profile, v)
            return status


class OneViewInventoryBuilder(object):

    MAIN_GROUP = "oneview_members"

    def __init__(self, api_client, inventory):
        self.api_client = api_client
        self.inventory = inventory
        self.preferred_ip = "IPv4"

    def set_preferred_ip(self, preferred_ip):
        self.preferred_ip = preferred_ip

    def set_hostname_short(self, hostname_short):
        self.hostname_short = hostname_short

    def set_add_domain(self, add_domain):
        self.add_domain = add_domain

    def populate(self):
        try:
            self.api_client.login()
            self._populate()
        finally:
            self.api_client.logout()

    def _populate(self):
        hosts_raw = self.api_client.list_server_hardware()
        self.inventory.add_group(OneViewInventoryBuilder.MAIN_GROUP)
        for host in hosts_raw:
            name, host_vars = self._process_hardware_host(host)
            shortModel = host_vars["shortModel"].replace(" ", "_")  # i.e. DL360 Gen10
            self.inventory.add_group(shortModel)
            self.inventory.add_child_group(self.MAIN_GROUP, shortModel)
            mpModel = host_vars["mpModel"].replace(" ", "_")  # i.e. iLO5
            self.inventory.add_group(mpModel)
            self.inventory.add_child_group(self.MAIN_GROUP, mpModel)
            self.inventory.add_host(name, variables=host_vars, group=shortModel)
            self.inventory.add_host_to_group(mpModel, name)

    def _process_hardware_host(self, host):
        name = host["mpHostInfo"]["mpHostName"].lower()
        if self.hostname_short:
            name = name.split(".")[0]
        elif self.add_domain:
            name = name.split(".")[0] + "." + self.add_domain
        host_vars = dict()
        host_vars["shortModel"] = host.get("shortModel")
        host_vars["mpModel"] = host.get("mpModel")
        for mp_ip_address in host["mpHostInfo"]["mpIpAddresses"]:
            if mp_ip_address["type"] == "Static":
                ip = mp_ip_address["address"]
                host_vars["ansible_host"] = ip
                if self.preferred_ip == "IPv4" and "." in ip:
                    break
                if self.preferred_ip == "IPv6" and ":" in ip:
                    break
        return name, host_vars
