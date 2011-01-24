#    powernapd plugin - Monitors process table for presence of process
#
#    Copyright (C) 2009 Canonical Ltd.
#
#    Authors: Dustin Kirkland <kirkland@canonical.com>
#             Andres Rodriguez <andreserl@ubuntu.com>
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

# Obtain the interrupts at any given point in time
def get_interrupts():
    interrupts = 0
    f = open("/proc/interrupts", "r")
    for line in f.readlines():
        items = line.split()
        source = items.pop()
        if source == "i8042" or source == "keyboard" or source == "mouse":
            items.pop(0)
            items.pop()
            for i in items:
                interrupts += int(i)
    f.close()
    return interrupts

class PS2Monitor():

    # Initialise
    def __init__(self, config):
        self._type = config['monitor']
        self._name = config['name']
        self._regex = re.compile(config['regex'])
        self._absent_seconds = 0
        self._interrupts = get_interrupts()

    # Check for PIDs
    def active(self):
        current_i = get_interrupts()
        if current_i > self._interrupts:
                self._interrupts = current_i
		return True
	return False

    def start(self):
        pass

