#!/usr/bin/env python

# set up logging
import logging, os
logging.basicConfig(level=os.environ.get('LOGLEVEL', 'WARNING').upper())

# standard Python libraries
import shelve

def main():
    # open database
    shelf_name = str(os.environ.get('HOME')+'/.page-news/save-syncthing-events-times.shelf')
    with shelve.open(shelf_name, flag='r') as times:

        for filepath in times.keys():
            print(times[filepath], filepath)

if __name__ == "__main__":
    exit(main())
