#!/usr/bin/python
#
#    powernap - monitor a system process table; if IDLE amount of time
#               goes by with no monitored PROCESSES running, run ACTION
#    Copyright (C) 2009 Canonical Ltd.
#
#    Authors: Dustin Kirkland <kirkland@canonical.com>
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

import commands
import os
import re
import signal
import sys
import time

global PKG, LOCK, CONFIG
PKG = "powernap"
LOCK = "/var/run/%s" % PKG
CONFIG = "/etc/%s/config" % PKG

# CONFIG values should override these
global INTERVAL, PROCESSES, ACTION, ABSENT, DEBUG
INTERVAL = 1
PROCESSES = [ "init" ]
ACTION = ""
ABSENT = sys.maxint
DEBUG = 1
# Load configuration file
try:
    execfile(CONFIG)
except:
    error("Invalid configuration [%s]" % CONFIG)

class Ballot(object):
    def __init__(self, process):
        self.process = process
        self.regex = re.compile(process)
        self.absent_time = 0

def error(msg):
    print("ERROR: %s" % msg)
    sys.exit(1)

def debug(msg):
    if DEBUG:
        print("DEBUG: %s" % msg)

def establish_lock(lock):
    if os.path.exists(lock):
        f = open(lock,'r')
        pid = f.read()
        f.close()
        error("Another instance is running [%s]" % pid)
    else:
        f = open(LOCK,'w')
        f.write(str(os.getpid()))
        f.close()
        # Set signal handlers
        signal.signal(signal.SIGHUP, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

def signal_handler(signal, frame):
    if os.path.exists(LOCK):
        os.remove(LOCK)
    sys.exit(1)

def find_process(ps, p):
    for x in ps:
        if p.search(x):
            return 1
    return 0

def notify_authorities(action):
    # TODO: notify authorities (mail, signals)
    debug("Taking action [%s], email authorities" % action)

def powernap_loop(ballots, absent, action, interval):
    debug("Starting %s, sleeping [%d] seconds" % (PKG, interval))
    while 1:
        time.sleep(interval)
        # Examine process table, compute absent time of each monitored process
        debug("Examining process table")
        absent_processes = 0
        ps = commands.getoutput("ps -eo args").splitlines()
        for ballot in ballots:
            debug("  Looking for [%s]" % ballot.process)
            if find_process(ps, ballot.regex):
                # process running, so reset absent time
                ballot.absent_time = 0
                debug("    Process found, reset absent time [%d/%d]" % (ballot.absent_time, absent))
            else:
                # process not running, increment absent time
                ballot.absent_time += interval
                debug("    Process not found, increment absent time [%d/%d]" % (ballot.absent_time, absent))
                if ballot.absent_time >= absent:
                    # process missing for >= absent threshold, mark absent
                    debug("    Process absent for >= threshold, so mark absent")
                    absent_processes += 1
        # Determine if action needs to be taken
        if absent_processes == len(ballots):
            # All processes are absent, take action!
            notify_authorities(action)
            for ballot in ballots:
                ballot.absent_time = 0
            os.system(action)
        debug("Done with powernap_loop, sleeping [%d] seconds" % interval)

def main():
    # Ensure that only one instance runs
    establish_lock(LOCK)
    try:
        # Run the main powernap loop
        ballots = [Ballot(process) for process in PROCESSES]
        powernap_loop(ballots, ABSENT, ACTION, INTERVAL)
    finally:
        # Clean up the lock file
        if os.path.exists(LOCK):
            os.remove(LOCK)

######################################################################

if __name__ == '__main__':
    main()
