#!/usr/bin/python -u
'''
    Generates Lookup Files based on API calls
    Saves the hassle of going out and making API calls everytime
    you want to enrich some data.
'''
__author__ = 'Brian Osburn'

'''Generic Imports
'''

import logging
import os
import sys
import json
import urllib
import ConfigParser

def setuplogging(SPLUNK_HOME):
    logging.basicConfig(filename=SPLUNK_HOME + '/etc/apps/Splunk_App_For_Planetside2/bin/logs/update_lookups.log',\
    level=logging.DEBUG,\
    format='%(asctime)s - %(levelname)s [%(process)d] -  %(message)s')

def readconfigfile(SPLUNK_HOME):
    configfile = SPLUNK_HOME + "/etc/apps/Splunk_App_For_Planetside2/bin/scripts.conf"
    readconfig = ConfigParser.ConfigParser()
    readconfig.read(configfile)

    service_id = readconfig.get("apiinfo", "Service_ID")

    return (service_id)

def factionid_lookup(destination, service_id):
    logging.info('[Update FactionID] - START')

    faction_count = 0
    header_row = "faction_id,faction_name\r\n"

    lookup_name = destination + "Faction_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/faction?c:lang=en&c:show=faction_id,name.en&c:limit=1000"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update FactionID] - Invalid JSON returned.  What I got instead:  %s', result)
        logging.error('[Update FactionID] - Character ID That Errored:  %s', character_id)

    number_of_results = result["returned"]

    while faction_count < number_of_results:
        faction_id = result["faction_list"][faction_count]["faction_id"]
        faction_name = result["faction_list"][faction_count]["name"]["en"]
        output_csv.write(faction_id + "," + faction_name + "\r\n")
        faction_count += 1

    logging.info('[Update FactionID] - STOP')


def world_lookup(destination, service_id):
    logging.info('[Update WorldID] - START')

    world_count = 0
    header_row = "world_id,world_name\r\n"

    lookup_name = destination + "World_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/world?c:lang=en&c:limit=100"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update WorldID] - Invalid JSON returned.  What I got instead:  %s', result)
        logging.error('[Update WorldID] - Character ID That Errored:  %s', character_id)

    number_of_results = result["returned"]

    while world_count < number_of_results:
        world_id = result["world_list"][world_count]["world_id"]
        world_name = result["world_list"][world_count]["name"]["en"]
        output_csv.write(world_id + "," + world_name + "\r\n")
        world_count += 1

    logging.info('[Update WorldID] - STOP')


def firemode_lookup(destination, service_id):
    logging.info('[Update FireMode] - START')

    firemode_count = 0
    header_row = "fire_mode_id,fire_mode_type,fire_mode_description\r\n"

    lookup_name = destination + "FireMode_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2//fire_mode?c:lang=en&c:limit=10000&c:show=fire_mode_id,type,description.en"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update FireMode] - Invalid JSON returned.  What I got instead:  %s', endpoint_results)

    number_of_results = result["returned"]

    while firemode_count < number_of_results:
        fire_mode_id = result["fire_mode_list"][firemode_count]["fire_mode_id"]
        fire_mode_type = result["fire_mode_list"][firemode_count]["type"]

        try:
            fire_mode_description = result["fire_mode_list"][firemode_count]["description"]["en"]
        except Exception, e:
            fire_mode_description = "No Description Available"
        else:
            fire_mode_description = result["fire_mode_list"][firemode_count]["description"]["en"]

        output_csv.write(fire_mode_id + "," + fire_mode_type + "," + fire_mode_description + "\r\n")
        firemode_count += 1

    logging.info('[Update FireMode] - STOP')


def vehicle_lookup(destination, service_id):
    logging.info('[Update VehicleLookup] - START')

    vehicle_count = 0
    header_row = "vehicle_id,vehicle_name\r\n"

    lookup_name = destination + "Vehicle_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/vehicle?c:limit=1000&c:lang=en&c:show=vehicle_id,name.en"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update VehicleLookup] - Invalid JSON returned.  What I got instead:  %s', result)

    number_of_results = result["returned"]

    while vehicle_count < number_of_results:
        vehicle_id = result["vehicle_list"][vehicle_count]["vehicle_id"]
        vehicle_name = result["vehicle_list"][vehicle_count]["name"]["en"]

        output_csv.write(vehicle_id + "," + vehicle_name + "\r\n")
        vehicle_count += 1

    logging.info('[Update VehicleLookup] - STOP')


def loadout_lookup(destination, service_id):
    logging.info('[Update LoadoutLookup] - START')

    loadout_count = 0
    header_row = "loadout_id,loadout_name\r\n"

    lookup_name = destination + "Loadout_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/loadout?c:limit=1000&c:lang=en"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update LoadoutLookup] - Invalid JSON returned.  What I got instead:  %s', result)

    number_of_results = result["returned"]

    while loadout_count < number_of_results:
        loadout_id = result["loadout_list"][loadout_count]["loadout_id"]
        loadout_name = result["loadout_list"][loadout_count]["code_name"]

        output_csv.write(loadout_id + "," + loadout_name + "\r\n")
        loadout_count += 1

    logging.info('[Update LoadoutLookup] - STOP')


def weapon_lookup(destination, service_id):
    logging.info('[Update WeaponLookup] - START')

    weapon_count = 0
    header_row = "weapon_id,weapon_name\r\n"

    lookup_name = destination + "Weapon_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/item_to_weapon?c:join=item^inject_at:weapondata^show:name.en&c:limit=1000"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update WeaponLookup] - Invalid JSON returned.  What I got instead:  %s', result)

    number_of_results = result["returned"]

    while weapon_count < number_of_results:
        weapon_id = result["item_to_weapon_list"][weapon_count]["weapon_id"]
        try:
            weapon_name = result["item_to_weapon_list"][weapon_count]["weapondata"]["name"]["en"]
        except Exception, e:
            weapon_name = "Unknown Weapon"
        else:
            weapon_name = result["item_to_weapon_list"][weapon_count]["weapondata"]["name"]["en"]

        output_csv.write(weapon_id + "," + weapon_name + "\r\n")
        weapon_count += 1

    logging.info('[Update WeaponLookup] - STOP')


def zone_lookup(destination, service_id):
    logging.info('[Update ZoneLookup] - START')

    zone_count = 0
    header_row = "zone_id,zone_name\r\n"

    lookup_name = destination + "Zone_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/zone?c:limit=200&c:lang=en&c:show=zone_id,name.en"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update ZoneLookup] - Invalid JSON returned.  What I got instead:  %s', result)

    number_of_results = result["returned"]

    while zone_count < number_of_results:
        zone_id = result["zone_list"][zone_count]["zone_id"]
        zone_name = result["zone_list"][zone_count]["name"]["en"]

        output_csv.write(zone_id + "," + zone_name + "\r\n")
        zone_count += 1

    logging.info('[Update ZoneLookup] - STOP')

def achievement_lookup(destination, service_id):
    logging.info('[Update AchievementLookup] - START')

    achievement_count = 0
    header_row = "achievement_id,achievement_name,achievement_description\r\n"

    lookup_name = destination + "Achievement_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/achievement?c:limit=10000&c:lang=en&c:show=achievement_id,name.en,description.en"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update AchievementLookup] - Invalid JSON returned.  What I got instead:  %s', result)

    number_of_results = result["returned"]

    while achievement_count < number_of_results:
        achievement_id = result["achievement_list"][achievement_count]["achievement_id"]
        achievement_name = result["achievement_list"][achievement_count]["name"]["en"]
        try:
            achievement_description = result["achievement_list"][achievement_count]["description"]["en"]
        except Exception, e:
            achievement_description = "Missing Description"
        else:
            achievement_description = result["achievement_list"][achievement_count]["description"]["en"]

        output_csv.write(achievement_id + "," + achievement_name + "," + achievement_description + "\r\n")
        achievement_count += 1

    logging.info('[Update AchievementLookup] - STOP')

def facility_lookup(destination, service_id):
    logging.info('[Update FacilityLookup] - START')

    facility_count = 0
    header_row = "facility_id,facility_name,facility_type\r\n"

    lookup_name = destination + "Facility_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/map_region?c:limit=10000&c:show=facility_id,facility_name,facility_type"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update FacilityLookup] - Invalid JSON returned.  What I got instead:  %s', result)

    number_of_results = result["returned"]

    while facility_count < number_of_results:
        facility_id = result["map_region_list"][facility_count]["facility_id"]
        facility_name = result["map_region_list"][facility_count]["facility_name"]
        facility_type = result["map_region_list"][facility_count]["facility_type"]

        output_csv.write(facility_id + "," + facility_name + "," + facility_type + "\r\n")
        facility_count += 1

    logging.info('[Update FacilityLookup] - STOP')

def metagame_lookup(destination, service_id):
    logging.info('[Update MetagameLookup] - START')

    metagame_count = 0
    header_row = "metagame_id,metagame_name,metagame_description\r\n"

    lookup_name = destination + "Metagame_Lookup.csv"

    output_csv = open(lookup_name, 'w')
    output_csv.write(header_row)

    endpoint = "http://census.daybreakgames.com/s:" + service_id + "/get/ps2:v2/metagame_event?c:limit=1000&c:lang=en&c:show=metagame_event_id,name.en,description.en"

    connection = urllib.urlopen(endpoint)
    endpoint_results = connection.read()
    connection.close()

    try:
        result = json.loads(endpoint_results)
    except ValueError, e:
        logging.error('[Update MetagameLookup] - Invalid JSON returned.  What I got instead:  %s', result)

    number_of_results = result["returned"]

    while metagame_count < number_of_results:
        metagame_id = result["metagame_event_list"][metagame_count]["metagame_event_id"]
        metagame_name = result["metagame_event_list"][metagame_count]["name"]["en"]
        metagame_description = result["metagame_event_list"][metagame_count]["description"]["en"]

        output_csv.write(metagame_id + "," + metagame_name + "," + metagame_description + "\r\n")
        metagame_count += 1

    logging.info('[Update MetagameLookup] - STOP')

def main():
    SPLUNK_HOME = os.environ.get("SPLUNK_HOME")
    setuplogging(SPLUNK_HOME)
    logging.info('[main] - START')

    service_id = readconfigfile(SPLUNK_HOME)
    logging.info('[main] - ServiceID passed = %s', service_id)

    destination = SPLUNK_HOME + "/etc/apps/Splunk_App_For_Planetside2/lookups/"

    factionid_lookup(destination, service_id)
    world_lookup(destination, service_id)
    firemode_lookup(destination, service_id)
    vehicle_lookup(destination, service_id)
    loadout_lookup(destination, service_id)
    weapon_lookup(destination, service_id)
    zone_lookup(destination, service_id)
    achievement_lookup(destination, service_id)
    facility_lookup(destination,service_id)
    metagame_lookup(destination,service_id)

    logging.info('[main] - STOP')

    sys.exit(0)


if __name__ == "__main__":
    main()
