# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.unbelievable.hpe.plugins.module_utils.logger import SilentLogger, ModuleLogger  # type: ignore
from ansible_collections.unbelievable.hpe.plugins.module_utils.api_client import (  # type: ignore
    JsonRestApiClient,
    HAS_REQUESTS,
    REQUESTS_IMP_ERR,
)
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.six.moves.urllib.parse import urlencode  # type: ignore


class OneViewApiClient(JsonRestApiClient):
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
            username=username,
            password=password,
            validate_certs=validate_certs,
            proxy=proxy,
        )

        self.api_version = api_version
        self.logger = logger
        self.session = None

    def get_headers(self):
        headers = {"X-API-Version": str(self.api_version)}
        if self.session:
            headers["Auth"] = self.session
        return headers

    def login(self):
        endpoint = "/rest/login-sessions"
        payload = {"userName": self.username, "password": self.password, "loginMsgAck": "true"}
        json = self.post_request(endpoint, payload)
        self.session = json.get("sessionID")
        self.logger.debug("OneViewApiClient: Login successful")

    def logout(self):
        if self.session:
            endpoint = "/rest/login-sessions"
            self.delete_request(endpoint)
            self.session = None
            self.logger.debug("OneViewApiClient: Logout successful")

    def list_server_hardware(self, filter=None):
        next_url = "/rest/server-hardware"
        if filter:
            next_url += "?filter=" + urlencode(filter)
        server = []
        while True:
            self.logger.debug("OneViewApiClient: {0}".format(next_url))
            data = self.get_request(next_url)
            if data["members"]:
                server += data["members"]
                next_url = data.get("nextPageUri", "")
                if not next_url:
                    break
            else:
                break
        return server

    def list_racks(self):
        next_url = "/rest/racks"
        racks = []
        while True:
            self.logger.debug("OneViewApiClient: {0}".format(next_url))
            data = self.get_request(next_url)
            if data["members"]:
                racks += data["members"]
                next_url = data.get("nextPageUri", "")
                if not next_url:
                    break
            else:
                break
        return racks


class OneviewModuleBase(object):
    def main(self):
        # define available arguments/parameters a user can pass to the module
        argument_spec = OneviewModuleBase.argument_spec()
        argument_spec.update(self.additional_argument_spec())

        self.module = AnsibleModule(
            argument_spec=argument_spec, supports_check_mode=self.supports_check_mode(), **self.module_def_extras()
        )

        if not HAS_REQUESTS:
            self.module.fail_json(msg=missing_required_lib("requests"), exception=REQUESTS_IMP_ERR)

        try:
            self.api_client = self.get_api_client()
            self.result = dict(
                changed=False,
                diff=None,
            )

            self.init()
            self.run()
            self.module.exit_json(**self.result)
        except BaseException as e:
            self.module.fail_json(e)

    def supports_check_mode(self):
        return True

    def additional_argument_spec(self):
        """Overwrite this to provide additional module argument specs"""
        return dict()

    def module_def_extras(self):
        return dict()

    def init(self):
        """Overwrite this to init your module"""
        pass

    def run(self):
        """Overwrite this to implement the module action"""
        pass

    def get_api_client(self):
        return OneViewApiClient(
            protocol=self.module.params.get("protocol"),
            host=self.module.params.get("hostname"),
            port=self.module.params.get("port"),
            username=self.module.params.get("username"),
            password=self.module.params.get("password"),
            validate_certs=self.module.params.get("validate_certs"),
            api_version=self.module.params.get("api_version"),
            proxy=self.module.params.get("proxy") if "proxy" in self.module.params else None,
            logger=ModuleLogger(self.module),
        )

    def set_changed(self, changed):
        self.result["changed"] = changed

    def set_changes(self, before=None, after=None):
        self.result["diff"] = {"before": before, "after": after}
        self.set_changed(before != after)

    def set_message(self, message):
        self.result["message"] = message

    @staticmethod
    def argument_spec():
        return dict(
            protocol=dict(
                type="str", choices=["http", "https"], required=False, default="https", aliases=["oneview_protocol"]
            ),
            hostname=dict(type="str", required=True, aliases=["host", "url", "oneview_url"]),
            port=dict(type="int", default=443, aliases=["oneview_port"]),
            username=dict(type="str", required=True, aliases=["user", "oneview_user"]),
            password=dict(type="str", required=True, aliases=["passwd", "oneview_password"], no_log=True),
            validate_certs=dict(type="bool", required=False, default=True),
            api_version=dict(type="int", default=2400, aliases=["oneview_api_version"]),
            proxy=dict(type="str", required=False),
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
