#
# TODO : add header
#

# IO monitor
#   monitor IO activity on a process (i.e. presence alone is not enough)
class IOMonitor ( ProcessMonitor ):
    def __init__ ( self, config ):
        if not config.has_key('regex'): raise Exception('regex is required')
        if not config.has_key('name'):
          config['name'] = "ioproc:%s" % config['regex']
        ProcessMonitor.__init__(self, config)
        self.io_counts = {}

    def reset ( self ):
        ProcessMonitor.reset(self)
        self.io_counts = {}

    def active ( self ):
        ret = False
        
        # Get new PID list from parent
        ProcessMonitor.active(self)

        # Get IO counts for all PIDs
        io_counts = {}
        for pid in self.pids:
            io_counts[pid] = {}
            try:
                fp = open('/proc/%d/io' % pid)
                for l in fp.readlines():
                    pts = l.split(':')
                    io_counts[pid][pts[0].strip()] = int(pts[1].strip())
                fp.close()
            except: pass # its possible the proc will die in here!

        # Update counts
        for pid in self.pids:

            # New process (assume activity)
            if pid not in self.io_counts:
               ret = True
               debug('    %s - adding new PID %d to list' % (self, pid))

            # Existing: check for change
            else:
                tmp = False
                for f in self.io_counts[pid]:
                    if self.io_counts[pid][f] != io_counts[pid][f]: tmp = True
                if ( tmp ): debug('    %s - PID %d has IO activity' % (self, pid))
                ret = tmp

            # Update count
            self.io_counts[pid] = io_counts[pid]

        # Remove old
        rem = []
        for pid in self.io_counts:
            if pid not in self.pids:
                rem.append(pid)
        for pid in rem:
            debug('    %s - PID %d no longer exists' % (self, pid))
            self.io_counts.pop(pid)

        return ret
