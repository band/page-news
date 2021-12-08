#!/usr/bin/env python

from flask import Flask
from flask import render_template
import json
from pathlib import Path

app = Flask(__name__)

################################################################

# routes
@app.route("/page-news/<path:wikidir>")
def page_news(wikidir):
    return render_template('page-news.html', wikidir=wikidir)

@app.route("/")
def index():
    wikidirs = get_vault_paths()
    return render_template('index.html', wikidirs=wikidirs)

################################################################

# find all the vaults Obsidian is tracking
# taken from https://github.com/peterkaminski/obsidian-settings-manager
# TODO: don't fail if they don't have Obsidian installed
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
