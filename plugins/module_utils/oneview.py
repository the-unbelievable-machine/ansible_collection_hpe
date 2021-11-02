# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from abc import abstractmethod
from distutils.version import LooseVersion

try:
    import requests

    if LooseVersion(requests.__version__) < LooseVersion("1.1.0"):
        raise ImportError
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class Logger(object):
    @abstractmethod
    def debug(self, msg):
        pass

    @abstractmethod
    def info(self, msg):
        pass

    @abstractmethod
    def warn(self, msg):
        pass


class ModuleLogger(Logger):
    def __init__(self, module):
        super().__init__()
        self.module = module

    def debug(self, msg):
        self.module.debug(msg)

    def info(self, msg):
        self.module.log(msg)

    def warn(self, msg):
        self.module.log("[warn] {0}".format(msg))


class BaseInventoryPluginLogger(Logger):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def debug(self, msg):
        self.plugin.display.vv(msg)

    def info(self, msg):
        self.plugin.display.v(msg)

    def warn(self, msg):
        self.plugin.display.warning(msg)


class Inventory(object):
    @abstractmethod
    def add_group(self, group):
        pass

    @abstractmethod
    def add_child_group(self, parent, child):
        pass

    @abstractmethod
    def add_host_to_group(self, group, host):
        pass

    @abstractmethod
    def add_host(self, host, variables=None, group=None):
        pass


class OneViewInventory(object):

    MAIN_GROUP = "oneview_members"

    def __init__(self):
        super().__init__()
        self.base_url = None
        self.username = None
        self.password = None
        self.validate_certs = True
        self.preferred_ip = "IPv4"
        self.session = None
        self.proxies = None
        self.logger = None
        if not HAS_REQUESTS:
            raise ImportError(
                "oneview: This module requires Python Requests 1.1.0 or higher: https://github.com/psf/requests."
            )

    def init(
        self,
        base_url,
        username,
        password,
        inventory,
        logger,
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.inventory = inventory
        self.logger = logger

    def set_validate_certs(self, validate_certs):
        self.validate_certs = validate_certs

    def set_preferred_ip(self, preferred_ip):
        self.preferred_ip = preferred_ip

    def set_proxy(self, proxy):
        if proxy:
            self.proxies = {"http": proxy, "https": proxy}
        else:
            self.proxies = None
        proxy = None

    def set_hostname_short(self, hostname_short):
        self.hostname_short = hostname_short

    def set_add_domain(self, add_domain):
        self.add_domain = add_domain

    def _get_headers(self):
        headers = {"X-API-Version": "800"}
        if self.session:
            headers["Auth"] = self.session
        return headers

    def _get_request(self, uri_path):
        url = "{0}{1}".format(self.base_url, uri_path)
        r = requests.get(url, headers=self._get_headers(), verify=self.validate_certs, proxies=self.proxies)

        if r.ok:
            return r.json()
        else:
            r.raise_for_status

    def login(self):

        data_get = {"userName": self.username, "password": self.password, "loginMsgAck": "true"}
        r = requests.post(
            "{0}/rest/login-sessions".format(self.base_url),
            json=data_get,
            headers=self._get_headers(),
            verify=self.validate_certs,
            proxies=self.proxies,
        )
        if r.ok:
            self.session = r.json().get("sessionID")
            self.logger.debug("oneview: Login successful")
        else:
            raise r.raise_for_status

    def logout(self):
        if self.session:
            r = requests.delete(
                "{0}/rest/login-sessions".format(self.base_url),
                headers=self._get_headers(),
                verify=self.validate_certs,
                proxies=self.proxies,
            )
            if r.ok:
                self.session = None
                self.logger.debug("oneview: Logout successful")
            else:
                self.logger.debug("oneview: Logout failed")

    def populate(self):
        next_url = "/rest/server-hardware"
        while True:
            self.logger.debug("oneview: query {0}".format(next_url))
            data = self._list_hardware(next_url)
            self.inventory.add_group(OneViewInventory.MAIN_GROUP)
            self._process_hardware_list(data)
            next_url = data.get("nextPageUri", "")
            if not next_url:
                break

    def _list_hardware(self, uri_path):
        return self._get_request(uri_path)

    def _process_hardware_list(self, data):
        if not data:
            self.logger.warn("oneview: got no hardware_list")
            return
        for member in data.get("members", []):
            name, host_vars = self._process_hardware_member(member)
            shortModel = host_vars["shortModel"].replace(" ", "_")  # i.e. DL360 Gen10
            self.inventory.add_group(shortModel)
            self.inventory.add_child_group(self.MAIN_GROUP, shortModel)
            mpModel = host_vars["mpModel"].replace(" ", "_")  # i.e. iLO5
            self.inventory.add_group(mpModel)
            self.inventory.add_child_group(self.MAIN_GROUP, mpModel)
            self.inventory.add_host(name, variables=host_vars, group=shortModel)
            self.inventory.add_host_to_group(mpModel, name)

    def _process_hardware_member(self, member):
        name = member["mpHostInfo"]["mpHostName"].lower()
        if self.hostname_short:
            name = name.split(".")[0]
        elif self.add_domain:
            name = name.split(".")[0] + "." + self.add_domain
        host_vars = dict()
        host_vars["shortModel"] = member.get("shortModel")
        host_vars["mpModel"] = member.get("mpModel")
        for mp_ip_address in member["mpHostInfo"]["mpIpAddresses"]:
            if mp_ip_address["type"] == "Static":
                ip = mp_ip_address["address"]
                host_vars["ansible_host"] = ip
                if self.preferred_ip == "IPv4" and "." in ip:
                    break
                if self.preferred_ip == "IPv6" and ":" in ip:
                    break
        return name, host_vars
