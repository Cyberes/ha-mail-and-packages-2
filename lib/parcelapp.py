import logging
import time

import requests

logger = logging.getLogger('PARCELAPP')

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
        logger.error(post_data)
        return

    if post_data.get('uuid'):
        logger.info('Parcelapp returned a UUID, sleeping 10 seconds and checking if updated...')
        time.sleep(10)
    else:
        if len(tracking_ids) == 1:
            return post_data['shipments'][0]
        return post_data

    get_response = requests.get(_API_URL, params={'apiKey': api_key, 'uuid': post_response.json()['uuid']})
    get_response.raise_for_status()

    # TODO: what is the UUID response???
    raise Exception(f'{post_data}\n{get_response.json()}')

    if get_response.json()['done']:
        print('Tracking complete')
