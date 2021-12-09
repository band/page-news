# Page News

Page News lists the recently changed pages in a Massive Wiki.

## Installation

Clone the repo.

Install Python requirements:

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `env.sh-template` to `env.sh`.

Edit `env.sh` to include your Syncthing API key.

## Running

Change to directory containing the `app.py` script.

Set the environment (only need to do once per terminal session):

```shell
source venv/bin/activate
source env.sh
```

Run the script:

```shell
./app.py
```

When the script is running, visit <http://localhost:8385/> in your web browser.

For development, you can use `flask run` rather than `./app.py`.  With Flask in debug mode (`app.config['FLASK_DEBUG'] = True` or `export FLASK_DEBUG=1`), it will auto-reload the script when you change the script in an editor.

## License and Acknowledements

Copyright 2021 Bill Anderson, Peter Kaminski.

Page News is licensed under MIT License, see the LICENSE file for details. Central repository: <https://github.com/Massive-Wiki/page-news>

Newspaper favicon used under CC-BY license from [PICOL](https://picol.org/).
