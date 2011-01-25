#    powernapd plugin - Monitors system load
#
#    Copyright (C) 2011 Canonical Ltd.
#
#    Authors: Dustin Kirkland <kirkland@ubuntu.com>
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

import os, re, commands
from logging import error, debug, info, warn

class LoadMonitor():

    # Initialise
    def __init__(self, config):
        self._type = config['monitor']
        self._name = config['name']
        if config['threshold'] == "n":
            self._threshold = commands.getoutput("getconf _NPROCESSORS_ONLN")
        else:
            self._threshold = config['threshold']
        self._absent_seconds = 0

    # Check system load
    def active(self):
        f = open("/proc/loadavg")
        l = f.read().split()
        f.close()
        if l[0] > self._threshold:
	    return True
	return False

    def start(self):
        pass

# ###########################################################################
# Editor directives
# ###########################################################################

# vim:sts=4:ts=4:sw=4:et
