#!/usr/bin/python

import ConfigParser, sys
from monitors import ProcessMonitor, InputMonitor, RemoteMonitor, IOMonitor

class PowerNap:

    def __init__(self):
        self.PKG = "powernap"
        #self.CONFIG = "/etc/powernap/config"
	self.CONFIG = "test.config"
        self.ACTION = "/usr/bin/powernap"
        self.ABSENT_SECONDS = sys.maxint
        self.INTERVAL_SECONDS = 1
        self.GRACE_SECONDS = 60
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
                    #self.load_monitors_config(monitor, cfg.items(monitor))
                    for items in cfg.items(monitor):
                        self.load_monitors_config(monitor, items)
        except:
            pass

    def set_default_values(self, var, value):
        if var == "absent_seconds":
            self.ABSENT_SECONDS = value
        if var == "interval_seconds":
            self.INTERVAL_SECONDS = int(value)
        if var == "grace_seconds":
            self.GRACE_SECONDS = value
        if var == "debug":
            self.DEBUG = value
        if var == "action_method":
            self.ACTION_METHOD = value

    def load_monitors_config(self, monitor, items):
        self.MONITORS.append({"monitor":monitor, "name":items[0], "regex":eval(items[1]), "absent":self.ABSENT_SECONDS})

    def get_monitors(self):
        monitor = []
        for config in self.MONITORS:
            if config["monitor"] == "ProcessMonitor":
                p = ProcessMonitor.ProcessMonitor(config)
            if config["monitor"] == "RemoteMonitor":
                p = RemoteMonitor.RemonteMonitor(config)
            if config["monitor"] == "InputMonitor":
                p = InputMonitor.InputMonitor(config)
            if config["monitor"] == "IOMonitor":
                p = IOMonitor.IOMonitor(config)
            monitor.append(p)

        return monitor
