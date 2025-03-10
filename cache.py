import argparse
import logging
import os
import pickle
import sys
import time

from redis import Redis

from lib.amazon import get_amazon_packages_arriving_today
from lib.imap.connection import IMAPConnection
from lib.usps import get_usps_packages_arriving_today, UspsApiType

logging.basicConfig(level=logging.INFO)

IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_USERNAME = os.getenv('IMAP_USERNAME')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
IMAP_FOLDER = os.getenv('IMAP_FOLDER')

PARCELSAPP_KEY = os.getenv('PARCELSAPP_KEY')

if PARCELSAPP_KEY and (not IMAP_HOST or not IMAP_USERNAME or not IMAP_PASSWORD or not IMAP_FOLDER):
    logging.critical('If using parcelsapp, must set IMAP_HOST and IMAP_USERNAME and IMAP_PASSWORD and IMAP_FOLDER environment variables')
    sys.exit(1)

AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')


def main(args):
    redis = Redis(host='localhost', port=6379, db=0)
    while True:
        if PARCELSAPP_KEY:
            logging.info('Fetching USPS tracking data...')
            IMAPConnection.initialise(IMAP_HOST, IMAP_USERNAME, IMAP_PASSWORD)
            usps_arriving_today, usps_delivered_today = get_usps_packages_arriving_today(IMAP_FOLDER, PARCELSAPP_KEY, args.usps_mode)
            IMAPConnection.close_connection()
            redis.set('usps_packages', pickle.dumps((usps_arriving_today, usps_delivered_today)))
            logging.info(f'USPS: {usps_arriving_today} arriving, {usps_delivered_today} delivered')
            # TODO: send tracking numbers to HA so that the dashboard card can link to the tracking page and not have to log in (https://tools.usps.com/go/TrackConfirmAction?tLabels=123%2Casd%2Cabc%2C)

        # return

        if AMAZON_USERNAME and AMAZON_PASSWORD:
            logging.info('Fetching Amazon order statuses...')
            amazon_packages_count, amazon_delivered_today, amazon_packages_items = get_amazon_packages_arriving_today(AMAZON_USERNAME, AMAZON_PASSWORD)
            redis.set('amazon_packages', pickle.dumps((amazon_packages_count, amazon_delivered_today, amazon_packages_items)))
            logging.info(f'AMAZON: {amazon_packages_count} arriving, {amazon_delivered_today} delivered')

        time.sleep(900)  # 15 minutes


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--usps-mode', choices=[UspsApiType.parcelsapp.value, UspsApiType.native.value], default=UspsApiType.parcelsapp.value,
                        help=f'The API type to use for USPS. "{UspsApiType.parcelsapp.value}" (default) uses the parcelsapp API, "native" uses the USPS tracking API.'
                        )

    args = parser.parse_args()
    main(args)
