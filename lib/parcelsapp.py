import logging
import time

import requests

_logger = logging.getLogger('PARCELSAPP')

_API_URL = 'https://parcelsapp.com/api/v3/shipments/tracking'


def fetch_parcel_data(api_key: str, tracking_ids: list):
    """
    https://parcelsapp.com/api-docs
    """
    data = [{'trackingId': x, 'language': 'en', 'country': 'United States'} for x in tracking_ids]
    post_response = requests.post(_API_URL, json={'apiKey': api_key, 'shipments': data})
    post_response.raise_for_status()
    post_data = post_response.json()

    if post_data.get('error'):
        _logger.error(post_data)
        return

    if post_data.get('uuid'):
        while True:
            time.sleep(1)
            get_response = requests.get(_API_URL, params={'apiKey': api_key, 'uuid': post_response.json()['uuid']})
            get_response.raise_for_status()
            tracking_data = get_response.json()
            break
    else:
        tracking_data = post_data

    if len(tracking_ids) == 1:
        return tracking_data['shipments'][0]
    return tracking_data


def parcelsapp_get_attr(tracking_data: dict, attr: str, match_by: str = 'l'):
    for x in tracking_data.get('attributes', []):
        if match_by == 'l' and x.get('l') == attr:
            return x['l'], x.get('val'), x.get('n'), x.get('code')
        elif match_by == 'n' and x.get('n') == attr:
            return x.get('l'), x.get('val'), x['n'], x.get('code')
    return None, None, None, None
