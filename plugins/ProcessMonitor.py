#    powernapd plugin - Monitors process table for presence of process
#
#    Copyright (C) 2009 Canonical Ltd.
#
#    Authors: Dustin Kirkland <kirkland@canonical.com>
#             Adam Sutton <dev@adamsutton.me.uk>
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

import re
from logging import error, debug, info, warn
from Monitor import Monitor

# Find list of PIDs that match a given regex (cmdline)
def find_pids ( regex ):
    ret = []
  
    for d in os.listdir('/proc'):
        try:
            path = '/proc/%s/cmdline' % d
            if os.path.isfile(path):
                fp      = open(path)
                cmdline = fp.read()
                fp.close()
                if regex.search(cmdline):
                    ret.append(int(d))
        except: pass

    return ret

# Monitor plugin
#   looks for the presence of a process (by regular expression) in the
#   current process table (whether active or not)
class ProcessMonitor ( Monitor ):

    # Initialise
    def __init__ ( self, config ):
        Monitor.__init__(self, config)
        self._pids  = []
        self._regex = re.compile(config['regex'])
        if not config.has_key('name'):
            self._name = config['regex']

    # Check for PIDs
    def active ( self ):
        if ( find_pids(self.regex) ): self.reset()
        return Monitor.active(self)

# ###########################################################################
# Editor directives
# ###########################################################################

# vim:sts=4:ts=4:sw=4:et
