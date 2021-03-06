#!/usr/bin/python -u

"""
Connect to the DayBreakGames Streaming Service and subscribe
"""

import os
import sys
import re
import logging

### Standard Values ###
install_dir = "/opt/Splunk_App_For_Planetside2/External_Scripts/scripts"

### Set Up Logging ###
log_file = install_dir + '/../logs/streaming.log'

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

### Open the output file ###
data_file = install_dir + '/../data/dbg_streaming_events.log'
datafile = open(data_file, 'a', 0)

### Dynamically load eggs ###
egg_dir = install_dir + '/../eggs/'

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

        message = str(message)

        """ Filtering out system messages """
        filter_events = re.search(r'payload', message, re.M | re.I)

        if filter_events:
            """Filter out based on world_id"""
            filter_worlds = re.search(r'world_id\":\"17\"', message, re.M | re.I)

            if filter_worlds is not None:
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
