import logging

import requests
from requests_cache import CachedSession

# Cached requests
rc = CachedSession(
    "intrusion_monitor_http_cache", backend="sqlite", use_temp=True, expire_after=604800
)


def api_call(ip, fields_id=66846719):
    """Returns the json data provided from http://ip-api.com.

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
     - query
    """

    req_str = f"http://ip-api.com/json/{ip}?fields={fields_id}"

    try:
        logging.debug(f"Trying API connection on {req_str}")
        req = rc.get(req_str)
        logging.debug(
            f"\t> Got HTTP code {req.status_code}. Request from cache: {req.from_cache}"
        )
    except:
        logging.error(
            f"Something occurred while getting API connection...", exc_info=True
        )
        return None

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
