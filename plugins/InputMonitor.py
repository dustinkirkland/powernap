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

    # Start the thread
    def start ( self ):
        self._running = True
        threading.Thread.start(self)

    # Stop thread
    def stop ( self ): self._running = False

    # Monitor /dev/input
    #   Note: it is assumed that /dev/input is static once powernapd starts
    #         i.e. if someone plugs a hot-pluggable input device (such as a 
    #              USB keyboard/mouse) this will not be detected (unless
    #              present when this process starts
    #   TODO: remove the requirement for static /dev/input
    def run ( self ):
        import select

        # Get all events
        poll = select.poll()
        fps  = {}
        for f in os.listdir(self._path):
            path = os.path.join(self._path, f)
            if not os.path.isdir(path):
                
                # Check each regex
                res = self._regex is None
                if not res:
                    for r in self._regex:
                        res = r.match(f)
                        if res: break
            
                # Include
                if res:
                    fp = open(path)
                    fps[fp.fileno()] = fp
                    poll.register(fp, select.POLLIN)
                    debug('%s - adding input device %s' % (self, path))

        # Poll for events
        while self._running:
            res = poll.poll(1000)
            if ( res ):
                for fd, e in res:
                    if e & select.POLLIN:
                        debug('%s - input on %s' % (self, fps[fd].name)) 
                        os.read(fd, 32768) # Read what is there!
                        self.reset()

        # Close the files
        for fd in fps: fps[fd].close()

# ###########################################################################
# Editor directives
# ###########################################################################

# vim:sts=4:ts=4:sw=4:et
