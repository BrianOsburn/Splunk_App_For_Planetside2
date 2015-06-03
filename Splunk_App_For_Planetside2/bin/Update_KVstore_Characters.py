#!/bin/python -u

__author__ = 'Brian Osburn'

"""
    This script will connect to your local Splunk instance and fire off
    a search to discover who has logged in the last X amount of time.
    It will then check the KVstore to see if there is any entries in the
    KV Store matching the character_id.
    If there is not a match, it will pull information from the DBG API
    and add it to the KVStore.

    Created:  May 17, 2015
    Author:  Brian Osburn
    Contact:  brianposburn@yahoo.com

"""

""" Generic Imports Go here """
import os
import sys
import json
import subprocess
import re
from urllib import urlopen
import urllib2
import logging
import ConfigParser

"""Look for and automagically add egg files """
SPLUNK_HOME = os.environ.get("SPLUNK_HOME")
egg_dir = SPLUNK_HOME + "/etc/apps/Splunk_App_For_Planetside2/bin/"

for filename in os.listdir(egg_dir):
    if filename.endswith(".egg"):
        sys.path.append(egg_dir + filename)

"""Splunk Specific Imports"""
import splunklib.client as client
import splunklib.results as results


def setuplogging(SPLUNK_HOME):
    logging.basicConfig(filename=SPLUNK_HOME + '/etc/apps/Splunk_App_For_Planetside2/bin/logs/update_kvstore.log',\
    level=logging.DEBUG,\
    format='%(asctime)s - %(levelname)s [%(process)d] -  %(message)s')

    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s [%(process)d] -  %(message)s')

def readconfigfile(SPLUNK_HOME):
    configfile = SPLUNK_HOME + "/etc/apps/Splunk_App_For_Planetside2/bin/scripts.conf"
    readconfig = ConfigParser.ConfigParser()
    readconfig.read(configfile)

    host = readconfig.get("serverinfo", "Host")
    port = readconfig.get("serverinfo", "Port")
    processors = readconfig.get("serverinfo", "Processors")
    admin = readconfig.get("splunkinfo", "Admin_Account")
    password = readconfig.get("splunkinfo", "Admin_Password")
    app = readconfig.get("splunkinfo", "App_Name")
    service_id = readconfig.get("apiinfo", "Service_ID")

    return (host, str(port), str(processors), admin, password, str(app), service_id)


def search_splunk(host, port, admin, password, app):
    logging.info('[search_splunk] - START')
    """Log in to Splunk"""
    service = client.connect(host=host, port=port, username=admin, password=password, app=app)

    """Settings for the search.  Modify earliest_time / latest time to
       modify search range.
    """

    kwargs_export = dict(earliest_time="-6m@m", latest_time="-1m@m", search_mode="normal")

    character_id_query = 'search index=dbg_ps2_pc-streaming payload.event_name=PlayerLogin | rename payload.character_id AS character_id | dedup character_id | table character_id'

    search_results = service.jobs.export(character_id_query, **kwargs_export)

    reader = results.ResultsReader(search_results)

    logging.info('[search_splunk] - STOP')
    return (reader)


def check_kvstore(character_id, host, port, admin, password, app):
    """ Checks the kvstore for existence of character id
    """

    logging.info('[check_kvstore] - START')
    logging.info('[check_kvstore] - Checking Character ID: %s', character_id)

    kvstoreendpoint = "https://" + host + ":" + port + "/servicesNS/nobody/" \
                      + app + "/storage/collections/data/ps2_characters?query=%7B%22character_id%22%3A%22" \
                      + character_id + "%22%7D"

    command = "/usr/bin/curl -k -s -u " + admin + ":" + password + " " + kvstoreendpoint

    search_result = subprocess.check_output(command, shell=True)

    check_results = re.search(r'character_id', search_result, re.M | re.I)

    if check_results:
        logging.info('[check_kvstore] - Character Found.')
        check_status = "found"
        logging.info('[check_kvstore] - STOP')
        return check_status
    else:
        logging.info('[check_kvstore] - Character Not Found.')
        check_status = "not found"
        logging.info('[check_kvstore] - STOP')
        return check_status


def name_lookup(character_id, service_id):
    logging.info('[name_lookup] - START')
    endpoint = 'http://census.daybreakgames.com/s:' \
               + service_id + '/get/ps2:v2/character?c:resolve=faction(name.en),online_status,world&c:lang=en&c:hide=head_id,times,certs,daily_ribbon&character_id=' \
               + str(character_id)

    logging.info('[name_lookup] - connecting to DBG API service looking up character_id %s', character_id)

    try:
        connection = urlopen(endpoint)
    except urllib2.HTTPError, e:
        logging.error('[name_lookup] - Connection to endpoint failed.')
        logging.error('[name_lookup] - Error Returned:  ' + s(e.code))
        sys.exit(1)
    except urllib2.URLError, e:
        logging.error('[name_lookup] - URL Error Returned.')
        logging.error('[name_lookup] - URL Error: ' + str(e.reason))
        sys.exit(1)
    except urllib2.HTTPException, e:
        logging.error('[name_lookup] - HTTP Exception returned.')
        sys.exit(1)
    except Exception:
        import traceback
        logging.error('[name_lookup] - Generic Error')
        logging.error('[name_lookup] - ' + traceback.format_exc())
        sys.exit(1)

    endpoint_results = connection.read()

    connection.close()

    try:
        result = json.loads(endpoint_results)
    except  ValueError, e:
        logging.error('[name_lookup] - Invalid JSON returned - what was returned: %s',endpoint_results)
        logging.error('[name_lookup] - Class returned instead of json:  %s', result.__name__)
        logging.error('[name_lookup] - Character ID That Errored:  %s',character_id)
        character_name = "ERROR"
        battle_rank = "ERROR"
        faction_name = "ERROR"
        world_id = "ERROR"
        logging.info('[name_lookup] - STOP')
        return character_name, battle_rank, faction_name, world_id

    result = json.loads(endpoint_results)

    if result["returned"] == 1:
        logging.info("[name_lookup] - Record Found")
        character_name = result["character_list"][0]["name"]["first"]
        battle_rank = result["character_list"][0]["battle_rank"]["value"]
        faction_name = result["character_list"][0]["faction"]["name"]["en"]
        world_id = result["character_list"][0]["world_id"]

        logging.info('[name_lookup] - STOP')
        return character_name, battle_rank, faction_name, world_id

    elif result["returned"] == 0:
        logging.info('[name_lookup] - Record was not found.  Private Account - character_id = %s', character_id)
        character_name = "PRIVATE_NAME"
        battle_rank = "PRIVATE_RANK"
        faction_name = "PRIVATE_FACTION"
        world_id = "PRIVATE_WORLD"
        logging.info('[name_lookup] - STOP')
        return character_name, battle_rank, faction_name, world_id


def update_kvstore(host, port, app, username, password, character_id, character_name, battle_rank, faction_name,
                   world_id):
    logging.info('[update_kvstore] - START')
    update_stats = {}
    port = str(port)

    base_url = "https://" + host + ":" + port + "/servicesNS/nobody/" + app + "/storage/collections/data/ps2_characters/"
    base_headers = "\'Content-Type: application/json\'"
    data = "\'{\"character_id\" : \"" + character_id + "\" ,\
        \"character_name\" : \"" + character_name + "\",\
        \"battle_rank\" : \"" + battle_rank + "\",\
        \"faction_name\" : \"" + faction_name + "\",\
        \"world_id\" : \"" + world_id + "\"}\'"

    base_url = str(base_url)
    base_headers = str(base_headers)
    data = str(data)

    full_command = "/usr/bin/curl -k -s -u " + username + ":" + password + " " + base_url + " -H " + base_headers + " -d " + data

    update_status = subprocess.check_output(full_command, shell=True)

    check_results = re.search(r'_key', update_status, re.M | re.I)

    if check_results:
        logging.info('[update_kvstore] - Update Successful')
        update_result = "Success"
        logging.info('[update_kvstore] - STOP')
        return update_result
    else:
        logging.error('[update_kvstore] - Update Failed')
        logging.error('[update_kvstore] - Update Error: %s', update_status)
        update_result = "Failure"
        logging.info('[update_kvstore] - STOP')
        return update_result


def main():
    setuplogging(SPLUNK_HOME)
    logging.info('[main] - START')
    character_id = []
    (host, port, processors, admin, password, app, service_id) = readconfigfile(SPLUNK_HOME)
    (search_results) = search_splunk(host, port, admin, password, app)

    for id in search_results:
        if isinstance(id, dict):
            character_id.append(id['character_id'])

    recordsfound = len(character_id)

    if recordsfound == 0:
        logging.info('[main] - No results found, exiting')
        logging.info('[main] - STOP')
        sys.exit(0)

    else:
        logging.info('[main] - Found %i character_ids to check', recordsfound)

    notfoundcount = 0
    foundcount = 0
    updatenumber = 0

    for charid in character_id:
        check_status = check_kvstore(charid, host, port, admin, password, app)

        if check_status == "not found":

            logging.info('[main] - Starting Update %s of %s', updatenumber, recordsfound)
            (character_name, battle_rank, faction_name, world_id) = name_lookup(charid, service_id)

            update_result = update_kvstore(host, port, app, admin, password, charid, character_name, battle_rank,
                                           faction_name, world_id)
            updatenumber += 1
            notfoundcount += 1
        else:
            updatenumber += 1
            foundcount += 1

    logging.info('[main] - Character IDs Found: %s', recordsfound)
    logging.info('[main] - KVStore Updates Done: %s', notfoundcount)
    logging.info('[main] - Character IDs Already Existing: %s', foundcount)
    logging.info('[main] - STOP')

    sys.exit(0)


if __name__ == "__main__":
    main()

