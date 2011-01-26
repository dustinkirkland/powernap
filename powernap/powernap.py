#!/usr/bin/python
#
#    powernap.py - handles powernap's config and initializes Monitors.
#
#    Copyright (C) 2010 Canonical Ltd.
#
#    Authors: Andres Rodriguez <andreserl@ubuntu.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ConfigParser, sys
from monitors import ProcessMonitor, LoadMonitor, InputMonitor, TCPMonitor, UDPMonitor, IOMonitor, WoLMonitor, ConsoleMonitor


class PowerNap:

    def __init__(self):
        self.PKG = "powernap"
        self.CONFIG = "/etc/powernap/config"
        #self.CONFIG = "test.config"
        self.ACTION = "/usr/sbin/powernap"
        self.RECOVER_ACTION = "/usr/sbin/pm-powersave false"
        self.ABSENT_SECONDS = sys.maxint
        self.INTERVAL_SECONDS = int(1)
        self.GRACE_SECONDS = int(60)
        self.DEBUG = int(0)
        self.ACTION_METHOD = 0
        self.MONITORS = []
        self.load_config_file()

    def load_config_file(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read(self.CONFIG)

        try:
            # Load items in DEFAULT section
            defaults = cfg.items(self.PKG)
            for items in defaults:
                self.set_default_values(items[0], eval(items[1]))

            # Load items on each monitor
            monitors_config = cfg.sections()
            for monitor in monitors_config:
                if monitor != self.PKG:
                    for items in cfg.items(monitor):
                        self.load_monitors_config(monitor, items)
        except:
            pass

    def set_default_values(self, var, value):
        if var == "absent_seconds":
            self.ABSENT_SECONDS = value
        if var == "interval_seconds":
            self.INTERVAL_SECONDS = value
        if var == "grace_seconds":
            self.GRACE_SECONDS = value
        if var == "debug":
            self.DEBUG = value
        if var == "action":
            self.ACTION = value
        if var == "action_method":
            self.ACTION_METHOD = value

    def load_monitors_config(self, monitor, items):
        if monitor == "ProcessMonitor" or monitor == "IOMonitor" or monitor == "InputMonitor":
            self.MONITORS.append({"monitor":monitor, "name":items[0], "regex":eval(items[1]), "absent":self.ABSENT_SECONDS})
        if monitor == "ConsoleMonitor" and (items[1] == "y" or items[1] == "yes"):
            self.MONITORS.append({"monitor":monitor, "name":items[0]})
        if monitor == "LoadMonitor":
            self.MONITORS.append({"monitor":monitor, "name":items[0], "threshold":items[1]})
        if monitor == "TCPMonitor":
            self.MONITORS.append({"monitor":monitor, "name":items[0], "port":eval(items[1]), "absent":self.ABSENT_SECONDS})
        if monitor == "UDPMonitor":
            # If ACTION_METHOD is 4 (PowerSave) and port is 7 or 9, do *NOT* create a monitor
            # This will cause that the WoL monitor to not be able to bind the port or viceversa.
            # TODO: Display a message that port is not being binded!!
            if self.ACTION_METHOD == 4 and (items[1] != 7 or items[1] != 9):
                self.MONITORS.append({"monitor":monitor, "name":items[0], "port":eval(items[1]), "absent":self.ABSENT_SECONDS})
        if monitor == "WoLMonitor":
            self.MONITORS.append({"monitor":monitor, "name":items[0], "port":eval(items[1]), "absent":self.ABSENT_SECONDS})

    def get_monitors(self):
        monitor = []
        for config in self.MONITORS:
            if config["monitor"] == "ProcessMonitor":
                p = ProcessMonitor.ProcessMonitor(config)
            if config["monitor"] == "LoadMonitor":
                p = LoadMonitor.LoadMonitor(config)
            if config["monitor"] == "UDPMonitor":
                p = UDPMonitor.UDPMonitor(config)
            if config["monitor"] == "WoLMonitor":
                p = WoLMonitor.WoLMonitor(config)
            if config["monitor"] == "InputMonitor":
                p = InputMonitor.InputMonitor(config)
            if config["monitor"] == "ConsoleMonitor":
                p = ConsoleMonitor.ConsoleMonitor(config)
            if config["monitor"] == "IOMonitor":
                p = IOMonitor.IOMonitor(config)
            if config["monitor"] == "TCPMonitor":
                p = TCPMonitor.TCPMonitor(config)
            monitor.append(p)

        return monitor
