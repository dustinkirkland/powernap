#    powernapd plugin - Monitors /dev/input for user activity
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

import os, re, threading
import select
from fcntl import fcntl, F_NOTIFY, DN_CREATE, DN_DELETE, DN_MULTISHOT
from logging import error, debug, info, warn
from Monitor import Monitor

# Monitor plugin
#   Monitors devices in /dev/input for activity
class InputMonitor ( Monitor, threading.Thread ):

    # Initialise
    def __init__ ( self, config ):
        threading.Thread.__init__(self)
        Monitor.__init__(self, config)
        if config.has_key('regex'):
            if hasattr(config['regex'], '__iter__'):
                self._regex = map(re.compile, config['regex'])
            else:
                self._regex = [ re.compile(config['regex']) ]
        else:
            self._regex = None
        self._running = False
        if not config.has_key('config'):
            self._path = '/dev/input'
        else:
            self._path = config['path']
        if not config.has_key('name'): self._name = self._path

        # Register for directory events / setup input watches
        self._inputs = {}
        self._poll   = select.poll()
        self._update_inputs()
        self._dd     = os.open(self._path, 0)
        fcntl(self._dd, F_NOTIFY, DN_DELETE | DN_CREATE | DN_MULTISHOT)

    # Update the input events list
    def _update_inputs ( self ):
        events = {}
        for p in os.listdir(self._path):
            path = os.path.abspath(os.path.join(self._path, p))

            # Ignore dirs
            if os.path.isdir(path): continue

            # Attempt to ignore already included
            if os.path.islink(path):
                path = os.path.abspath(os.readlink(path))
                if path in events: continue

            # Search expressions
            res = not self._regex
            for r in self._regex:
                res = r.match(p)
                if res: break
            if not res: continue

            # Existing
            if path in self._inputs:
                events[path] = self._inputs
    
            # New
            else:
                fp = open(path)
                events[path] = fp
                self._poll.register(fp.fileno(), select.POLLIN|select.POLLPRI)
                debug('%s - adding input device %s' % (self, path))

        # Remove
        for path in self._inputs:
            if not path in events:
                debug('%s - removing input device %s' % (self, path))
                fp = self._inputs[path]
                self._poll.unregister(fp.fileno())
                fp.close()

        # Update
        self._inputs = events

    # Start the thread
    def start ( self ):
        self._running = True
        threading.Thread.start(self)

    # Stop thread
    def stop ( self ): self._running = False

    # Monitor /dev/input
    def run ( self ):

        # Poll for events
        while self._running:
            res = self._poll.poll(1000)
            if ( res ):
                for fd, e in res:
                    if e & (select.POLLIN|select.POLLPRI):
                        os.read(fd, 32768) # Read what is there!
                        self.reset()
        
                        # Debug
                        path = None
                        for p in self._inputs:
                            if self._inputs[p].fileno() == fd:
                                path = p
                                break
                        debug('%s - input on %s' % (self, path)) 

# ###########################################################################
# Editor directives
# ###########################################################################

# vim:sts=4:ts=4:sw=4:et
