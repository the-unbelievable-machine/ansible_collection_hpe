# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from abc import abstractmethod


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


class InventoryPluginInventory(Inventory):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def add_group(self, group):
        self.plugin.inventory.add_group(group)

    def add_child_group(self, parent, child):
        self.plugin.inventory.add_child(parent, child)

    def add_host_to_group(self, group, host):
        self.plugin.inventory.add_child(group, host)

    def add_host(self, host, variables=None, group=None):
        self.plugin._populate_host_vars(hosts=[host], variables=variables, group=group)


class DictInventory(Inventory):
    def __init__(self):
        self.d = dict(hosts={}, groups={})

    def add_group(self, group):
        self.d["groups"].setdefault(group, dict(name=group, children=list()))

    def add_child_group(self, parent, child):
        if parent in self.d["groups"]:
            if child not in self.d["groups"][parent]["children"]:
                self.d["groups"][parent]["children"].append(child)
        else:
            raise ValueError("group '{0}' not found".format(parent))

    def add_host_to_group(self, group, host):
        if group not in self.d["groups"]:
            raise ValueError("group '{0}' not found".format(group))
        if host in self.d["hosts"]:
            if group not in self.d["hosts"][host]["groups"]:
                self.d["hosts"][host]["groups"].append(group)
        else:
            raise ValueError("host '{0}' not found".format(host))

    def add_host(self, host, variables=None, group=None):
        self.d["hosts"].setdefault(host, dict(name=host, vars=variables, groups=list([group])))

    def get_inventory(self):
        return self.d
