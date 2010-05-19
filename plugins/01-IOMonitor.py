#    powernapd plugin - Monitors process table for process with IO activity
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

# Monitor plugin
#   looks for processes that have IO activity. Useful for some server
#   processes that are always present in the process list even when idle
class IOMonitor ( ProcessMonitor ):

    # Initialise
    def __init__ ( self, config ):
        ProcessMonitor.__init__(self, config)
        self._iocounts = {}
        if not config.has_key('name'):
            self._name = 'ioproc:%s' % config['regex']
        
    # Check for activity
    def active ( self ):
        
        # Get new PID list from parent
        pids = find_pids(self._regex)

        # Get IO counts for all PIDs
        io_counts = {}
        for pid in pids:
            io_counts[pid] = {}
            try:
                fp = open('/proc/%d/io' % pid)
                for l in fp.readlines():
                    pts = l.split(':')
                    io_counts[pid][pts[0].strip()] = int(pts[1].strip())
                fp.close()
            except: pass # its possible the proc will die in here!

        # Update counts
        for pid in pids:

            # New process (assume activity)
            if pid not in self._iocounts:
               debug('    %s - adding new PID %d to list' % (self, pid))

            # Existing: check for change
            else:
                tmp = False
                for f in self._iocounts[pid]:
                    if self._iocounts[pid][f] != io_counts[pid][f]: self.reset()
                if ( tmp ): debug('    %s - PID %d has IO activity' % (self, pid))

            # Update count
            self._iocounts[pid] = io_counts[pid]

        # Remove old
        rem = []
        for pid in self._iocounts:
            if pid not in pids:
                rem.append(pid)
        for pid in rem:
            debug('    %s - PID %d no longer exists' % (self, pid))
            self._iocounts.pop(pid)

        # Use grand parent to signal result
        return Monitor.active(self)

# ###########################################################################
# Editor directives
# ###########################################################################

# vim:sts=4:ts=4:sw=4:et
