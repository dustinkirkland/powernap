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

import os
import signal
import sys
import time

PKG = "powernap"
LOCK = "/var/run/"+PKG
CONFIG = "/etc/"+PKG+"/config"
INTERVAL = 5


def error(msg):
    print "ERROR: "+msg
    exit(1)

def establish_lock(lock):
    if os.path.exists(lock):
        f = open(lock,'r')
        pid = f.read()
        f.close()
        error("Another instance is running ["+pid+"]")
    else:
        f = open(LOCK,'w')
        f.write(`os.getpid()`)
        f.close()

def signal_handler(signal, frame):
    if os.path.exists(LOCK):
        os.remove(LOCK)
    exit(1)

def reset_ballot(size):
    ballot = []
    for i in range (0, size-1):
        ballot[i] = 0
    return ballot

def notify_authorities():
    # TODO: notify authorities (mail, signals)
    print("Taking action, email authorities")

def powernap_loop(processes, absence, action):
    while 1:
        absent_processes = 0
        # Examine process table, compute absence time of each monitored process
        for i in range(0, len(processes)-1):
            if os.system('pgrep -f "'+processes[i]+'" >/dev/null'):
                # process not running, increment absence time
                ballot[i] += INTERVAL
                if ballot[i] >= absence:
                    # process missing for >= absence threshold, mark absent
                    absent_processes += 1
            else:
                # process running, so reset absence time
                ballot[i] = 0
        # Determine if action needs to be taken
        if absent_processes == len(processes):
            # All processes are absent, take action!
            notify_authorities()
            reset_ballot(len(processes))
            os.system(action)
        time.sleep(INTERVAL)

def main():
    # Ensure that only one instance runs
    establish_lock(LOCK)
    try:
        # Set signal handlers
        signal.signal(signal.SIGHUP, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        # Load configuration
        try:
            # Configuration should load variables:
            # ACTION, IDLE, PROCESSES
            execfile(CONFIG)
            ballot = reset_ballot(len(PROCESSES))
        except:
            error("Invalid configuration ["+CONFIG+"]")
        powernap_loop(PROCESSES, ABSENCE, ACTION)
    finally:
        if os.path.exists(LOCK):
            os.remove(LOCK)

######################################################################

if __name__ == '__main__':
    main()
