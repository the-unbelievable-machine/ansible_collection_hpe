# -*- coding: utf-8 -*-
#
# (c) 2021, The unbelievable Machine Company GmbH
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from abc import abstractmethod


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


class SilentLogger(Logger):
    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warn(self, msg):
        pass


class ModuleLogger(Logger):
    def __init__(self, module):
        self.module = module

    def debug(self, msg):
        self.module.debug(msg)

    def info(self, msg):
        self.module.log(msg)

    def warn(self, msg):
        self.module.log("[warn] {0}".format(msg))


class InventoryPluginLogger(Logger):
    def __init__(self, plugin):
        self.plugin = plugin

    def debug(self, msg):
        self.plugin.display.vv(msg)

    def info(self, msg):
        self.plugin.display.v(msg)

    def warn(self, msg):
        self.plugin.display.warning(msg)
