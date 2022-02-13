import os
import logging
from pprint import pprint

from requests_cache import CachedSession
import pygeohash

rc = CachedSession('intrusion_monitor_http_cache', backend='sqlite', use_temp=True, expire_after=604800)

def extract_ip_info(data):

    # Data in json but API returned an error
    if data['status'] == 'success':
        logging.debug(f'\t> API response valid and "status" is {data["status"]}. API response: \n{data}')
        data['geohash'] = compute_geohash(data['lat'], data['lon'])
        if data['geohash']:
            logging.debug(f'\t> Geohash computed is: {data["geohash"]}')
        else:
            logging.error(f'\t> Unable to compute geohash for ip={data["ip"]}; latitude={data["latitude"]}; longitude={data["longitude"]}')
    else:
        logging.error(f'\t> API response is valid but "status" is {data["status"]}. Message: {data["message"]}')
        return None


    return data

def compute_geohash(lat, lon):

    try:
        logging.debug(f'Computing geohash for {lat}, {lon}')
        geohash = pygeohash.encode(lat, lon)
        logging.debug(f'Geohash computed: {geohash}')
    except Exception as e:
        logging.error(f'An error occurred while computing geohash: {e}')
        geohash = None

    return geohash