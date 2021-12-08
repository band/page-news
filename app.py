#!/usr/bin/env python

from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/page-news/<wikidir>")
def page_news(wikidir):
    return render_template('page-news.html', wikidir=wikidir)

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="localhost", port=8385, debug=True)
