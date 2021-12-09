#!/usr/bin/env python

################################################################
#
# Page News - lists the recently changed pages in a Massive Wiki.
#
# Copyright 2021 Bill Anderson, Peter Kaminski.
# 
# Page News is licensed under MIT License, see the LICENSE file for details.
# Central repository: <https://github.com/Massive-Wiki/page-news>
#
################################################################

# standard Python libraries
import json
import os
from pathlib import Path
import requests

# `pip install flask`
from flask import Flask, render_template

# set up Flask
app = Flask(__name__)
app.config['FLASK_DEBUG'] = True
app.config['STATIC_FOLDER'] = '/static'
app.config['TEMPLATES_FOLDER'] = '/templates'

# get auth key from environment
syncthing_api_key = os.environ['SYNCTHING_API_KEY']

################################################################

# routes

# /syncthing/config
@app.route("/syncthing/config")
def syncthing_config():
    return render_template('syncthing-config.html', config=get_syncthing_config())

# /syncthing/events
def isItemFinished(event):
    return event['type'] == 'ItemFinished'
@app.route("/syncthing/events")
def syncthing_events():
    return render_template('syncthing-events.html', events=filter(isItemFinished, get_syncthing_events()))

# /page-news
@app.route("/page-news/<path:wikidir>")
def page_news(wikidir):
    # wiki = (name, path) tuple
    return render_template('page-news.html', wiki=(Path(wikidir).name, wikidir))

# /
@app.route("/")
def index():
    obsidian_vaults = []
    try:
        # send a list of (name, path) tuples
        obsidian_vaults = [(Path(p).name, p) for p in get_vault_paths()]
    except Exception as e:
        pass
    return render_template('index.html', obsidian_vaults=obsidian_vaults)

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

if __name__ == '__main__':
    app.run(host="localhost", port=8385, debug=True)
