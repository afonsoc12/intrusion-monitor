import os
import logging
from pprint import pprint

import requests
import pygeohash

def extract_ip_info(ip):
    api_key = os.getenv('API_KEY')
    req_str = 'http://api.ipstack.com/{ip}?access_key={apikey}'

    try:
        logging.debug('Trying API connection on {}'.format(req_str.format(ip=ip, apikey='XXXX')))
        req = requests.get(req_str.format(ip=ip, apikey=api_key))
        logging.debug(f'\t> Got HTTP code {req.status_code}')
    except:
        logging.error(f'Something occurred while getting API connection...')
        return None

    if req.status_code == 200:
        try:
            data = req.json()
            logging.debug(f'\t> Data parsed to json')
        except:
            logging.error(f'\t> An error occurred parsing API data to json. Data starts with: {req.text[0:20]}')
            return None

        # Data in json but API returned an error
        if 'status' in data and not data['success']:
            logging.error(f'\t> API returned an error. API response: \n{pprint(data)}')
            return None
        else:
            logging.debug(f'\t> API response is valid. API response: \n{data}')
            data['geohash'] = compute_geohash(data['latitude'], data['longitude'])
            logging.debug('\t> Geohash computed is: {}'.format(data['geohash']))

    else:
        logging.error(f'\t> An error occurred parsing API data to json. Data starts with: {req.text[0:20]}')

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