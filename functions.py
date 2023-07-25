import re
import time
import json
import requests
import subprocess

import logging

from utilities import config, logger

sockets = list()
loop_socket = None
ip_cache = dict()


def handle_socket(socket):
    logger.info("Opening socket")
    sockets.append(socket)
    home_loc = dict(home=True, lat=config.getfloat('HOME_LAT'), lon=config.getfloat('HOME_LON'))
    socket.send(json.dumps(home_loc))
    while socket.connected and loop_socket:
        time.sleep(1)
    if not loop_socket:
        loop(socket)
    else:
        logger.info(f"Connection {socket} disconnected")
        sockets.remove(socket)


def loop(primary_socket):
    global loop_socket
    loop_socket = primary_socket
    logger.info(f"New loop: {loop_socket}")
    log_follower = subprocess.Popen(['tail', '-n', '1', '-f', config.get('LOG_PATH')],
                                    stdout=subprocess.PIPE)
    while loop_socket.connected:
        line = log_follower.stdout.readline().decode('utf-8').replace('\n', '')
        loc_data = parse_line(line)
        if loc_data:
            logger.info(f'Sending location {loc_data} to {len(sockets)} sockets')
            for socket in sockets:
                socket.send(json.dumps(loc_data))
    log_follower.kill()
    loop_socket = None
    logger.info("Loop socket disconnected")
    sockets.remove(primary_socket)
    if not sockets:
        logger.info("All sockets disconnected")


def parse_line(line):
    if 'Failed' in line:
        ips = re.findall(r'[0-9]+(?:\.[0-9]+){3}', line)
        if ips:
            logger.debug(f"Got IP: {ips[0]}")
            return get_location(ips[0])


def get_location(ip):
    if cache_hit := ip_cache.get(ip):
        cache_hit['time'] = time.time()
        return cache_hit['loc']
    else:
        logger.debug("Cache miss, looking up IP location")
        req = requests.get(config.get('API_TEMPLATE').format(ip=ip))
        if req.ok:
            loc = dict(lat=req.json()['lat'], lon=req.json()['lon'])
            add_cache(ip, loc)
            return loc
        else:
            logger.error(f"Could not lookup IP {ip}: {ret.text}")


def add_cache(ip, loc):
    ip_cache[ip] = dict(time=time.time(), loc=loc)
    while len(ip_cache) > config.getint('MAX_CACHE_SIZE'):
        sorted_cache = sorted(ip_cache, key=lambda x: ip_cache[x]['time'])
        oldest_ip = sorted_cache[0]
        del ip_cache[oldest_ip]
