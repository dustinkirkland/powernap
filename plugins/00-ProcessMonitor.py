#
# TODO: add header
#

# Process monitor
#   monitors static processes (i.e. presence in /proc is enough)
class ProcessMonitor ( Monitor ):
    def __init__ ( self, config ):
        if not config.has_key('regex'): raise Exception('Key regex is required')
        if not config.has_key('name'): config['name'] = config['regex']
        Monitor.__init__(self, config)
        self.regex = re.compile(config['regex'])
        self.pids  = []

    def reset ( self ): self.pids = []

    def active ( self ):
      self.pids = find_pids(self.regex)
      return len(self.pids) > 0
