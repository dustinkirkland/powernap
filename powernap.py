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
LOCK = "/var/run/"+PKG
CONFIG = "/etc/"+PKG+"/config"

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
    error("Invalid configuration ["+CONFIG+"]")


def error(msg):
    print("ERROR: "+msg)
    exit(1)

def debug(msg):
    if DEBUG:
        print("DEBUG: "+msg)

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
        # Set signal handlers
        signal.signal(signal.SIGHUP, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

def signal_handler(signal, frame):
    if os.path.exists(LOCK):
        os.remove(LOCK)
    exit(1)

def reset_ballot(size):
    ballot = list()
    for i in range(size):
        ballot.append(0)
    return ballot

def compile_regexes(processes):
    regexes = list()
    for i in range(len(processes)):
        regexes.append(re.compile(processes[i]))
    return regexes

def find_process(ps, p):
    for i in range(len(ps)):
        if p.search(ps[i]):
            return 1
    return 0


def notify_authorities(action):
    # TODO: notify authorities (mail, signals)
    debug("Taking action ["+action+"], email authorities")

def powernap_loop(processes, absent, action, interval):
    ballot = reset_ballot(len(processes))
    regexes = compile_regexes(processes)
    debug("Starting "+PKG+", sleeping ["+str(interval)+"] seconds")
    while 1:
        time.sleep(interval)
        # Examine process table, compute absent time of each monitored process
        debug("Examining process table")
        absent_processes = 0
        ps = commands.getoutput("ps -eo args").splitlines()
        for i in range(len(regexes)):
            debug("Looking for ["+str(processes[i])+"]")
            if find_process(ps, regexes[i]):
                # process running, so reset absent time
                ballot[i] = 0
                debug("Process found, reset absent time ["+str(ballot[i])+"/"+str(absent)+"]")
            else:
                # process not running, increment absent time
                ballot[i] += interval
                debug("Process not found, increment absent time ["+str(ballot[i])+"/"+str(absent)+"]")
                if ballot[i] >= absent:
                    # process missing for >= absent threshold, mark absent
                    debug("Process absent for >= threshold, so mark absent")
                    absent_processes += 1
        # Determine if action needs to be taken
        if absent_processes == len(processes):
            # All processes are absent, take action!
            notify_authorities(action)
            ballot = reset_ballot(len(processes))
            os.system(action)
        debug("Done with powernap_loop, sleeping ["+str(interval)+"] seconds")

def main():
    # Ensure that only one instance runs
    establish_lock(LOCK)
    try:
        # Run the main powernap loop
        powernap_loop(PROCESSES, ABSENT, ACTION, INTERVAL)
    finally:
        # Clean up the lock file
        if os.path.exists(LOCK):
            os.remove(LOCK)

######################################################################

if __name__ == '__main__':
    main()
