#!/usr/bin/env python

################################################################
#
# Page News - lists the recently changed pages in a Massive Wiki.
#
# Copyright 2021, 2022 Bill Anderson, Peter Kaminski.
# 
# Page News is licensed under MIT License, see the LICENSE file for details.
# Central repository: <https://github.com/Massive-Wiki/page-news>
#
################################################################

# standard Python libraries
from datetime import datetime
import json
import os
from pathlib import Path
import re

# `pip install requests`
import requests

# `pip install flask`
from flask import Flask, render_template

# `pip install python-dateutil`
from dateutil.parser import *

# set up Flask
app = Flask(__name__)
app.config['FLASK_DEBUG'] = True
app.config['STATIC_FOLDER'] = '/static'
app.config['TEMPLATES_FOLDER'] = '/templates'

# get auth key from environment
syncthing_api_key = os.environ['SYNCTHING_API_KEY']

################################################################
#
# generate wiki content test files using APScheduler
#
################################################################

# `pip install apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

# set up generate_test_file_job properties
import random

# the 25 rules of civilized conduct in a dictionary
civility_rules={1: 'Pay Attention', 2: 'Acknowledge Others', 3: 'Think the Best', 4: 'Listen', 5: 'Be Inclusive', 6: 'Speak Kindly', 7: "Don't Speak Ill", 8: 'Accept and Give Praise', 9: 'Respect Even a Subtle "No"', 10: "Respect Other's Opinions", 11: 'Mind Your Body', 12: 'Be Agreeable', 13: 'Keep It Down (and Rediscover Silence)', 14: "Respect Other People's Time", 15: "Respect Other People's Space", 16: 'Apologize Earnestly', 17: 'Assert Yourself', 18: 'Avoid Personal Questions', 19: 'Care for Your Guests', 20: 'Be a Considerate Guest', 21: 'Think Twice Before Asking for Favors', 22: 'Refrain from Idle Complaints', 23: 'Accept and Give Constructive Criticism', 24: 'Respect the Environment and Be Gentle to Animals', 25: "Don't Shift Responsibility and Blame"}

def generate_test_file_job():
    ruleN = random.randint(1,25)
    filename="/Users/band/Documents/syncthing/sync+swim/nothingBurger/civilityrule" + str(ruleN) + ".md"
    print('I am working ... on ' + filename +'\n')
    with open(filename, "w") as file:
        file.writelines(["# Civility rule number " + str(ruleN) + ":\n\n",
                         "##  " + civility_rules[ruleN] + "\n\n",
                         " - from [Choosing Civility: the twenty-five rules of considerate conduct](http://www.worldcat.org/oclc/955532052) by P.M. Forni\n\n"])

scheduler = BackgroundScheduler(timezone=utc)
job = scheduler.add_job(generate_test_file_job, 'cron', day_of_week='mon-fri', hour='13-17', jitter=120)
scheduler.start()


################################################################
#
# utility functions
#
################################################################

# get syncthing events
def get_syncthing_events():
    r = requests.get('http://localhost:8384/rest/events', headers={"X-API-Key":syncthing_api_key})
    try:
        return r.json()
    except Exception as e:
        app.logger.debug(f"get_syncthing_events error: {e}")
        return None

# get syncthing config, for devices and folders
def get_syncthing_config():
    r = requests.get('http://localhost:8384/rest/config', headers={"X-API-Key":syncthing_api_key})
    try:
        return r.json()
    except Exception as e:
        app.logger.debug(f"get_syncthing_config error: {e}")
        return None

# find all the vaults Obsidian is tracking
# taken from https://github.com/peterkaminski/obsidian-settings-manager
# TODO: do something nice (don't crash) if Obsidian isn't installed, or if OS is not Mac
def get_vault_paths():
    vault_paths = []

    # read primary file
    # location per https://help.obsidian.md/Advanced+topics/How+Obsidian+stores+data#System+directory
    # (TODO: should be parameterized and support other OSes)
    with open(Path.home() / 'Library/Application Support/obsidian/obsidian.json') as infile:
        obsidian = json.load(infile)
        vaults = obsidian['vaults']
        for vault in vaults:
            # skip Help or other system directory vaults
            # TODO: support other OSes
            if Path(vaults[vault]['path']).parent == Path.home() / 'Library/Application Support/obsidian':
                continue
            vault_paths.append(vaults[vault]['path'])

        # sort paths (case-insensitive)
        vault_paths.sort(key=str.lower)

    # return paths
    return vault_paths

################################################################
#
# initial data load
#
################################################################

# get Syncthing config (devices and folders)
# TODO: add a "refresh" route to refresh this info
# TODO: or maybe just don't rely on cached data, and get it every time (maybe use list comprehension rather than `filter`)

syncthing_config = get_syncthing_config()
syncthing_folders_by_path = {}
for folder in syncthing_config["folders"]:
    syncthing_folders_by_path[folder['path']] = folder['id']

################################################################
#
# routes
#
################################################################

# /syncthing/config
@app.route("/syncthing/config")
def syncthing_config():
    return render_template('syncthing-config.html', config=get_syncthing_config())

# /syncthing/events
def isItemFinished(event):
    return event['type'] == 'ItemFinished'
def isItemFinished_or_localIndexUpdated(event):
    return event['type'] == 'ItemFinished' or event['type'] == 'LocalIndexUpdated'
def isLocalIndexUpdated(event):
    return event['type'] == 'LocalIndexUpdated'
@app.route("/syncthing/events")
def syncthing_events():
    return render_template('syncthing-events.html', events=filter(isLocalIndexUpdated, get_syncthing_events()))

# /page-news
@app.route("/page-news/<path:wikidir>")
def page_news(wikidir):
    folders = get_syncthing_config()['folders']
    folder_id = None
    for folder in folders:
        if folder['path'] == f"/{wikidir}":
            folder_id = folder['id']
    events = [event for event in get_syncthing_events() if
        (event['type'] == 'LocalIndexUpdated') and
        ('folder' in event['data']) and
        (event['data']['folder'] == folder_id)
    ]
    times = {}
    for event in events:
        for filename in event['data']['filenames']:
            if filename not in times or parse(event['time']) > times[filename]:
                # TODO: make these filters optional
                if not re.match(".*Untitled.*", filename) and not re.match("^\.|/\.", filename):
                        times[filename] = parse(event['time'])
    sorted_times = sorted(times.items(), key=lambda p: p[1], reverse=True) # sort by datetime, reverse
    # wiki = (name, path) tuple
    return render_template('page-news.html', wiki=(Path(wikidir).name, wikidir), sorted_times=sorted_times)

# /
def hasGit(p):
    return (Path(p) / ".git").is_dir()
def hasSyncthing(p):
    return p in syncthing_folders_by_path
@app.route("/")
def index():
    obsidian_vaults = []
    try:
        # send a list of (name, path, hasGit) tuples
        obsidian_vaults = [(Path(p).name, p, hasGit(p), hasSyncthing(p)) for p in get_vault_paths()]
    except Exception as e:
        app.logger.debug(f"can't retrieve Obsidian vaults error: {e}")
        pass
    return render_template('index.html', obsidian_vaults=obsidian_vaults)

################################################################
#
# script start
#
################################################################

if __name__ == '__main__':
    app.run(host="localhost", port=8385, debug=True, use_reloader=False)
