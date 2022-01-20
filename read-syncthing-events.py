#!/usr/bin/env python

# set up logging
import logging, os
logging.basicConfig(level=os.environ.get('LOGLEVEL', 'WARNING').upper())

# standard Python libraries
import shelve
from pprint import pprint

def main():
    # open database
    with shelve.open('data/save-syncthing-events-times.shelf', flag='r') as times:

        for filepath in times.keys():
            print(times[filepath], filepath)

if __name__ == "__main__":
    exit(main())
