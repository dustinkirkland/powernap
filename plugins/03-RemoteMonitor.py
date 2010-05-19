#
# TODO: add header
#

# Monitor UDP messages
class RemoteMonitor ( Monitor, threading.Thread ):
    def __init__ ( self, config ):
        if not config.has_key('port'):
          raise Exception('port not defined')
        if not config.has_key('name'):
          config['name'] = 'remote:%d' % config['port']
        threading.Thread.__init__(self)
        Monitor.__init__(self, config)
        self.data    = False
        self.port    = config['port']

    def reset ( self ): self.data = False

    def start ( self ): threading.Thread.start(self)

    def active ( self ):
        ret = self.data
        self.data = False
        return ret

    # Open port and wait for data (any data will trigger the monitor)
    def run ( self ):
        global RUNNING
        import socket

        # Create socket
        sock   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listen = False

        while RUNNING:
            if not listen:
                try:
                    debug(logging.DEBUG, '%s - configure socket' % self)
                    sock.bind(('', self.port))
                    sock.settimeout(1.0)
                    listen = True
                except Exception, e:
                    debug(logging.ERROR, '%s - failed to config socket [e=%s]' % (self, str(e)))
                    time.sleep(1.0)
            else:
                try:
                    # Wait for data
                    sock.recvfrom(1024)
                    debug(logging.DEBUG, '%s - data packet received' % self)
                    self.data = True
                except: pass # timeout
