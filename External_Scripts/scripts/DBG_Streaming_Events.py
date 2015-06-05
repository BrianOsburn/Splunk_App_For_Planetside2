#!/usr/bin/python -u

"""
Connect to the DayBreakGames Streaming Service and subscribe
"""

import os
import sys
import re
import signal
import logging

### Standard Values ###
# cwd = os.getcwd()
cwd = "/opt/dbg_games/scripts"

### Set Up Logging ###
log_file = cwd + '/../logs/streaming.log'

logging.basicConfig(filename=log_file,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s [%(process)d] -  %(message)s')

logging.info('[main] - Starting Process Now')

### Check Arguments ###
if len(sys.argv) <= 1:
    print "Missing argument - Service ID"
    print "Please get one from http://census.daybreakgames.com"
    logging.info('[main] - Missing argument - exiting.')
    sys.exit(1)

### Setup the pidfile
pid = str(os.getpid())
pidfile = cwd + "/dbg_streaming.pid"

### Check to see if the pid file exists, and if it does, is the process still running?
if os.path.isfile(pidfile):
    with open(pidfile, 'r') as f:
        pidnumber = f.read()

        ### Check /proc/$pidnumber$/cmdline to see if the command line matches ours
        proc = "/proc/" + pidnumber + "/cmdline"

        if os.path.isfile(proc):
            with open(proc) as proc:
                cmdline = proc.read()

                cmdsearch = re.search(r'DBG_Streaming_Events.py', cmdline, re.M | re.I)

                ##If command line matches ours, kill the previous version and restart
                if cmdsearch:
                    logging.info('[main] - found previously running process. Killing pid %s' % pidnumber)
                    os.kill(int(pidnumber), signal.SIGTERM)

                ###Not our process, so stale pid and needs cleaning up
                else:
                    logging.info('[main] - Stale PID found, cleaning pid file.')
                    os.remove(pidfile)
        else:
            logging.info('[main] - Stale PID found, cleaning pid file.')
            os.remove(pidfile)

file(pidfile, 'w').write(pid)

### Open the output file ###
data_file = cwd + '/../data/dbg_streaming_events.log'
datafile = open(data_file, 'a')

### Dynamically load eggs ###
egg_dir = cwd + '/../eggs/'

for filename in os.listdir(egg_dir):
    if filename.endswith(".egg"):
        sys.path.append(egg_dir + filename)

### Import WebSocketClient ###
from ws4py.client.threadedclient import WebSocketClient

### Class Defintion ###
class DBGClient(WebSocketClient):
    def opened(self):
        playerlogevents = """
  {
	  "service":"event",
	  "action":"subscribe",
	  "worlds":["all"],
      "characters":["all"],
	  "eventNames":["PlayerLogin","PlayerLogout","AchievementEarned","BattleRankUp","Death","VehicleDestroy","PlayerFacilityCapture","PlayerFacilityDefend","ContinentLock","ContinentUnlock","FacilityControl","MetagameEvent"]
}
        """

        logging.info('[main] - Send Subscription Request')
        self.send(playerlogevents)

    def closed(self, code, reason=None):
        logging.info('[main] - Connection closed with code %s - %s', code, reason)
        datafile.close()

    def received_message(self, m):
        message = m
        # print m

        message = str(message)
        filter_events = re.search(r'payload', message, re.M | re.I)

        if filter_events:
            message = message + "\r\n"
            datafile.write(message)


service_id = sys.argv[1]
url = 'wss://push.planetside2.com/streaming?environment=ps2&service-id=s:' + service_id

try:
    logging.info('[main] - opening connections')
    ws = DBGClient(url)
    ws.connect()
    ws.run_forever()
except KeyboardInterrupt:
    ws.close()
    os.remove(pidfile)
