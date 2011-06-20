#!/usr/bin/python
#
#    powerwake.py - handles powerwaked config and initializes Monitors.
#
#    Copyright (C) 2011 Canonical Ltd.
#
#    Authors: Andres Rodriguez <andreserl@canonical.com>
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

import ConfigParser, sys, re, os
from monitors import ARPMonitor 


class PowerWake:

    def __init__(self):
        self.PKG = "powerwake"
        self.CONFIG = "/etc/powernap/powerwaked.conf"
        self.ACTION = "/usr/bin/powerwake"
        self.INTERVAL_SECONDS = int(1)
        self.DEBUG = int(0)
        self.MONITORS = []
        # Load default config file (/etc/powernap/config)
        self.load_config_file()

    def load_config_file(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read(self.CONFIG)

        try:
            # Load items in DEFAULT section
            defaults = cfg.items(self.PKG)
            for items in defaults:
                self.set_default_values(items[0], items[1])

            monitors_config = cfg.sections()
            for monitor in monitors_config:
                for items in cfg.items(monitor):
                    self.load_monitors_config(monitor, items)
        except:
            pass

    def set_default_values(self, var, value):
        if var == "interval_seconds":
            self.INTERVAL_SECONDS = eval(value)
        if var == "debug":
            self.DEBUG = eval(value)
        if var == "action":
            self.ACTION = eval(value)
        if var == "warn":
            if value == "y" or value == "yes":
                self.WARN = True

    def load_monitors_config(self, monitor, items):
        if monitor == "ARPMonitor" and (items[1] == "y" or items[1] == "yes"):
            self.MONITORS.append({"monitor":monitor, "cache":self.get_arp_cache()})

    def get_monitors(self):
        monitor = []
        for config in self.MONITORS:
            if config["monitor"] == "ARPMonitor":
                p = ARPMonitor.ARPMonitor(config)
            monitor.append(p)

        return monitor

    def get_arp_cache(self):
        host_to_mac = {}
        PKG = 'powerwake'
        for file in ["/var/cache/%s/ethers" % PKG, "/etc/ethers"]:
            if os.path.exists(file):
                f = open(file, 'r')
                for i in f.readlines():
                    try:
                        (m, h) = i.split()
                        host_to_mac[h] = m
                    except:
                        pass
                f.close()
        return host_to_mac
        
