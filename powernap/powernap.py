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
from monitors import ProcessMonitor, InputMonitor, RemoteMonitor, IOMonitor

class PowerNap:

    def __init__(self):
        self.PKG = "powernap"
        #self.CONFIG = "/etc/powernap/config"
	self.CONFIG = "test.config"
        self.ACTION = "/usr/bin/powernap"
        self.ABSENT_SECONDS = sys.maxint
        self.INTERVAL_SECONDS = int(1)
        self.GRACE_SECONDS = int(60)
        self.DEBUG = 0
        self.ACTION_METHOD = 0
        self.MONITORS = []

    def load_config_file(self):
        cfg = ConfigParser.ConfigParser()
        cfg.read(self.CONFIG)

        try:
            # Load items in DEFAULT section
            defaults = cfg.items(self.PKG)
            for items in defaults:
                self.set_default_values(items[0], items[1])

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
            self.ABSENT_SECONDS = int(value)
        if var == "interval_seconds":
            self.INTERVAL_SECONDS = int(value)
        if var == "grace_seconds":
            self.GRACE_SECONDS = int(value)
        if var == "debug":
            self.DEBUG = value
        if var == "action_method":
            self.ACTION_METHOD = value

    def load_monitors_config(self, monitor, items):
        if monitor == "ProcessMonitor" or monitor == "IOMonitor" or monitor == "InputMonitor":
            self.MONITORS.append({"monitor":monitor, "name":items[0], "regex":eval(items[1]), "absent":self.ABSENT_SECONDS})
        if monitor == "RemoteMonitor":
            self.MONITORS.append({"monitor":monitor, "name":items[0], "port":eval(items[1]), "absent":self.ABSENT_SECONDS})

    def get_monitors(self):
        monitor = []
        for config in self.MONITORS:
            if config["monitor"] == "ProcessMonitor":
                p = ProcessMonitor.ProcessMonitor(config)
            if config["monitor"] == "RemoteMonitor":
                p = RemoteMonitor.RemoteMonitor(config)
            if config["monitor"] == "InputMonitor":
                p = InputMonitor.InputMonitor(config)
            if config["monitor"] == "IOMonitor":
                p = IOMonitor.IOMonitor(config)
            monitor.append(p)

        return monitor
