import logging

import requests
from requests_cache import CachedSession

# Cached requests
rc = CachedSession(
    "intrusion_monitor_http_cache", backend="sqlite", use_temp=True, expire_after=604800
)


def url_builder(ip, fields_id=66846719, base_url=False):
    """
    The parameter `fields_id` encodes the following json generated fields:
    - status
    - message
    - continent
    - continentCode
    - country
    - countryCode
    - region
    - regionName
    - city
    - district
    - zip
    - lat
    - lon
    - timezone
    - offset
    - currency
    - isp
    - org
    - as
    - asname
    - reverse
    - mobile
    - proxy
    - hosting
    - query"""
    if base_url:
        return f"http://ip-api.com/json"
    else:
        return f"http://ip-api.com/json/{ip}?fields={fields_id}"


def api_request(ip):
    """Returns the request data provided from http://ip-api.com."""

    req_str = url_builder(ip)

    try:
        logging.debug(f"Trying API connection on {req_str}")
        req = rc.get(req_str)
        logging.debug(
            f"\t> Got HTTP code {req.status_code}. Request from cache: {req.from_cache}"
        )
    except:
        err = "Something occurred while getting API connection..."
        logging.error(err, exc_info=True)
        raise ConnectionError(err)

    return req


def process_request(req):
    """Processes the data from a request object."""

    if req.status_code == 200:
        try:
            data = req.json()
            logging.debug(f"\t> Data parsed to json")
        except:
            err = f"\t> An error occurred parsing API data to json. Data starts with: {req.text[0:20]}"
            logging.error(err)
            raise ValueError(err[3:])
    else:
        err = f"\t> Request status code {req.status_code} != 200. Reason: {req.reason}"
        logging.error(err)
        raise requests.HTTPError(err[3:])

    return data


def api_request_and_process(ip):
    """Returns the json data provided from http://ip-api.com."""

    req = api_request(ip)

    data = process_request(req)

    return data
