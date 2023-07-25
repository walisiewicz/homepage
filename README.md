# SSH Authentication Tracker - walisiewicz.com Homepage

Homepage for [www.walisiewicz.com](walisiewicz.com) which displays failed authentication attempts to the domain in real time using Flask, d3.js and websockets. When looking at the SSH logs of a public IP address, it is always slightly concerning to see the number of authentication attempts from unknown IPs - even when practicing good security. This site watches the Linux `auth.log`, queries a public IP-to-location API to convert the IP address to a rough latitude and longitude (usually the center of the closest city), and sends the coordinates to the page over a websocket. The d3.js map takes the location from the websocket and displays it on a map of the world. Red dots are used to display the origin point of the attempt, these slowly grow as more authentication attempts are logged from the same address.

## Technical details

The site is lightweight enough that it can run in a single uwsgi process which allows the safe use of global variables. Three globals are used; one to keep track of the main connection that is watching the log - the `loop_socket`, a second to maintain a list of all connected websockets, and a third to cache IP addresses to locations. This ensures that the log is only open once at a time and that all connections receive location data at the same time. If the primary socket disconnects, another socket will take over within one second without the need for locking. The IP cache is used to reduce the number of API queries for duplicate addresses - many authentication attempts reoccur from the same attackers. The IP-to-location service used is [www.ip-api.com](ip-api.com) as it has the largest number of free queries per day at time of development.

## Setup

Ensure you are using python 3.10 on Mac or Linux, install nginx through your package manager. Install the python requirements from `requirements.txt`. Configure a basic nginx proxy - this is required for the websocket. You may also want to tweak the `config.ini` to adjust the location of your server to be displayed by the map animations or the cache size if your IP experiences a high number of authentication attempts from different addresses. Finally run the app with this command `uwsgi --ini config.ini` .

## License

This repo is licensed under GNU GPLv3.
