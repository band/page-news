#!/usr/bin/env python

# set up logging
import logging, os
logging.basicConfig(level=os.environ.get('LOGLEVEL', 'WARNING').upper())

# standard Python libraries
import shelve

# `pip install requests`
import requests

# `pip install python-dateutil`
from dateutil.parser import *

# get auth key from environment
syncthing_api_key = os.environ['SYNCTHING_API_KEY']

# get syncthing events
def get_syncthing_events():
    r = requests.get('http://localhost:8384/rest/events', headers={"X-API-Key":syncthing_api_key})
    try:
        return r.json()
    except Exception as e:
        logging.debug(f"get_syncthing_events error: {e}")
        return None

def main():
    # open database
    # TODO: refactor this app so writeback can be False, to save memory
    shelf_name = str(os.environ.get('HOME')+'/.page-news/save-syncthing-events-times.shelf')
    with shelve.open(shelf_name, flag='c', writeback=True) as times:

        # read events from API, filter for LocalIndexUpdated
        events = [event for event in get_syncthing_events() if
            (event['type'] == 'LocalIndexUpdated')
        ]

        # save newer events
        for event in events:
            for filename in event['data']['filenames']:
                if filename not in times or parse(event['time']) > times[filename]:
                    times[filename] = parse(event['time'])

if __name__ == "__main__":
    exit(main())
