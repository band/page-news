
# 2022-02-05 this bit of code can replace page-news use of requests module
# or a command line curl -H expression
#   <https://stackoverflow.com/questions/70989059/curl-to-python-for-post-request>

from urllib import request

url='http://localhost:8384/rest/events'
hdr = {"X-API-Key": api_key}
>>> hdr
{'X-API-Key': 'QymboetHnd6F9PStTPAS3qCwocxg4C2c'}

req=request.Request(url, headers=hdr)
resp=request.urlopen(req)
content=resp.read()
data=json.loads(content.decode('utf-8'))
print(data)

# possible refactoring

events = json.loads(resp.read().decode('utf-8'))

# replace this code with urllib version:
# get syncthing events
def get_syncthing_events():
    r = requests.get('http://localhost:8384/rest/events', headers={"X-API-Key":syncthing_api_key})
    try:
        return r.json()
    except Exception as e:
        logging.debug(f"get_syncthing_events error: {e}")
        return None

# urllib version
def get_syncthing_events():
    req = request.Request('http://localhost:8384/rest/events', headers={"X-API-Key":syncthing_api_key})
    r = request.urlopen(req)
    try:
        return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        logging.debug(f"get_syncthing_events error: {e}")
        return None


# 2022-02-06 here is the iso_parse Python datetime lib hack required:
from datetime import datetime

def iso_parse(dt_string):
    dtsplit = dt_string.split('.')
    dtmstzsplit = dtsplit[1].split('-')
    dtiso = str(dtsplit[0] +"."+ dtmstzsplit[0].zfill(6) +"-"+ dtmstzsplit[1])
    return datetime.fromisoformat(dtiso)


>>> iso_parse(t1)
datetime.datetime(2022, 2, 5, 5, 47, 28, 62769, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=64800)))
>>> iso_parse('2022-02-05T05:43:37.236189-06:00')
datetime.datetime(2022, 2, 5, 5, 43, 37, 236189, tzinfo=datetime.timezone(datetime.timedelta(days=-1, seconds=64800)))
