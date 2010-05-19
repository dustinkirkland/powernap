#
# TODO: add header
#

# Monitor /dev/input
class InputMonitor ( Monitor, threading.Thread ):

    # Initialise
    def __init__ ( self, config ):
        if not config.has_key('name'): config['name'] = 'console'
        threading.Thread.__init__(self)
        Monitor.__init__(self, config)
        self.event   = False

    def reset ( self ): self.event = False

    def start ( self ): threading.Thread.start(self)

    def active ( self ):
        ret = self.event
        self.event = False
        return ret

    # Monitor /dev/input
    #   Note: it is assumed that /dev/input is completely static!
    #         i.e. if someone plugs a hot-pluggable input device (such as a 
    #              USB keyboard/mouse) this will not be detected (unless
    #              present when this process starts
    #   TODO: would be better to fix this, I've done it before so not too 
    #         difficult
    def run ( self ):
        global RUNNING
        import select

        # Get all events
        poll = select.poll()
        fps  = []
        for f in os.listdir('/dev/input'):
            path = os.path.join('/dev/input', f)
            if not os.path.isdir(path):
                fp   = open(path)
                fps.append(fp)
                poll.register(fp, select.POLLIN)
                debug(logging.DEBUG, '%s - adding input device %s' % (self, path))

        # Poll for events
        while RUNNING:
            res = poll.poll(1000)
            if ( res ):
               for fd, e in res:
                   if e & select.POLLIN:
                       self.event = True
                       os.read(fd, 32768) # Read what is there!

        # Close the files
        for fp in fps: fp.close()
