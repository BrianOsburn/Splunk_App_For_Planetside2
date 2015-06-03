#!/usr/bin/python -u
'''
    Generates Lookup Files based on API calls
    Saves the hassle of going out and making API calls everytime
    you want to enrich some data.
'''
__author__ = 'Brian Osburn'

'''Generic Imports
'''
import os
import logging
import sys
import csv
import json
import urllib
import ConfigParser

def setuplogging(SPLUNK_HOME):
    logging.basicConfig(filename=SPLUNK_HOME + '/etc/apps/Splunk_App_For_Planetside2/bin/logs/outfit_lookup.log',\
    level=logging.DEBUG,\
    format='%(asctime)s - %(levelname)s [%(process)d] -  %(message)s')

    #logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s [%(process)d] -  %(message)s')

def readconfigfile(SPLUNK_HOME):
    configfile = SPLUNK_HOME + "/etc/apps/Splunk_App_For_Planetside2/bin/scripts.conf"
    readconfig = ConfigParser.ConfigParser()
    readconfig.read(configfile)

    service_id = readconfig.get("apiinfo", "Service_ID")

    return (service_id)

def lookupoutfitbyid(outfitid,service_id):
    logging.info('[GetOutfitByID] - START')

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/outfit?outfit_id=" + outfitid

    logging.info('[GetOutfitByID] - Endpoint: %s',endpoint)
    logging.info('[GetOutfitByID] - Calling API Now')

    try:
        connection = urllib.urlopen(endpoint)
    except Exception,e:
        logging.info('[GetOutfitById] - Something went wrong with urlopen')

    try:
        endpoint_results = connection.read()
    except Exception,e:
        logging.info('[GetOutfitByID]  - Somethin went wrong with reading the results')
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[GetOutfitByID] - Invalid JSON returned.  What I got instead:  %s', result)

    outfit_name=result["outfit_list"][0]["name"]

    logging.info('[GetOutfitByID] - STOP')
    return outfit_name

def lookupoutfitbyname(outfitname,service_id):
    logging.info('[GetOutfitByName] - START')

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/outfit?name_lower=" + outfitname

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[GetOutfitByName - Invalid JSON returned.  What I got instead:  %s', result)

    outfit_id=result["outfit_list"][0]["outfit_id"]

    logging.info('[GetOutfitByName] - STOP')
    return outfit_id

def main():

    SPLUNK_HOME = os.environ.get("SPLUNK_HOME")

    setuplogging(SPLUNK_HOME)

    logging.info('[main] - START')

    if len(sys.argv) != 3:
        logging.error('[main] - Missing Outfit ID or Outfit Name')
        logging.error('[main] - Usage:  Outfit_Lookup.py <outfitid> <outfitname>')

    idfield = sys.argv[1]
    namefield = sys.argv[2]

    logging.info('[main] - IDField = %s',idfield)
    logging.info('[main] - namefield = %s',namefield)
    logging.info('[main] - SPLUNK_HOME = %s',SPLUNK_HOME)

    service_id = readconfigfile(SPLUNK_HOME)

    logging.info('[main] - ServiceID passed = %s', service_id)

    infile = sys.stdin
    outfile = sys.stdout

    logging.info('[main] - Infile = %s',infile)

    inputCSV = csv.DictReader(infile)
    header = inputCSV.fieldnames

    outputCSV = csv.DictWriter(outfile, fieldnames=inputCSV.fieldnames)
    outputCSV.writeheader()

    for entry in inputCSV:
        if entry[idfield] and entry[namefield]:
            outputCSV.writerow(entry)
        elif entry[idfield]:
            outfit_id = entry[idfield]
            if outfit_id == "0":
                outfit_name = "N/A"
                entry["outfit_name"] = outfit_name
                logging.info('[main] - outfit_name = %s',outfit_name)
                outputCSV.writerow(entry)
            elif outfit_id > "0":
                (outfit_name) = lookupoutfitbyid(outfit_id, service_id)
                entry["outfit_name"] = outfit_name
                logging.info('[main] - outfit_name = %s',outfit_name)
                outputCSV.writerow(entry)
        elif entry[namefield]:
            outfit_name = entry[namefield]
            outfit_name = outfit_name.lower()
            (outfit_id) = lookupoutfitbyname(outfit_name, service_id)
            entry["outfit_id"] = outfit_id
            logging.info('[main] - outfit_id = %s',outfit_name
                    )
            outputCSV.writerow(entry)

    sys.exit(0)

if __name__ == "__main__":
    main()