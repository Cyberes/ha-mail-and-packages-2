import argparse
import logging
import os
import pickle
import sys
import time
import traceback

from redis import Redis

from lib.amazon import get_amazon_packages_arriving_today
from lib.consts import REDIS_USPS_KEY, REDIS_DB, REDIS_AMAZON_KEY, REDIS_FEDEX_KEY
from lib.fedex import get_fedex_packages_arriving_today
from lib.imap.connection import IMAPConnection
from lib.usps import get_usps_packages_arriving_today

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
    redis = Redis(db=REDIS_DB)
    encountered_error = False

    if PARCELSAPP_KEY:
        IMAPConnection.initialise(IMAP_HOST, IMAP_USERNAME, IMAP_PASSWORD)

    while True:
        if PARCELSAPP_KEY:
            ## USPS ##
            usps_arriving_count = usps_delivered_count = -1
            usps_recent_tracking_ids = []
            try:
                usps_arriving_count, usps_delivered_count, usps_recent_tracking_ids = get_usps_packages_arriving_today(IMAP_FOLDER, PARCELSAPP_KEY)
                logging.info(f'USPS: {usps_arriving_count} arriving today, {usps_delivered_count} delivered')
            except:
                encountered_error = True
                logging.error(f'Failed to fetch USPS tracking data:\n{traceback.format_exc()}')
            redis.set(REDIS_USPS_KEY, pickle.dumps((usps_arriving_count, usps_delivered_count, usps_recent_tracking_ids)))

            ## Fedex ##
            fedex_arriving_count = fedex_delivered_count = -1
            fedex_recent_tracking_ids = []
            try:
                fedex_arriving_count, fedex_delivered_count, fedex_recent_tracking_ids = get_fedex_packages_arriving_today(IMAP_FOLDER, PARCELSAPP_KEY)
                logging.info(f'Fedex: {fedex_arriving_count} arriving today, {fedex_delivered_count} delivered')
            except:
                encountered_error = True
                logging.error(f'Failed to fetch USPS tracking data:\n{traceback.format_exc()}')
            redis.set(REDIS_FEDEX_KEY, pickle.dumps((fedex_arriving_count, fedex_delivered_count, fedex_recent_tracking_ids)))

        ## Amazon ##
        if AMAZON_USERNAME and AMAZON_PASSWORD:
            amazon_packages_count = amazon_delivered_today = -1
            amazon_packages_items = ['error']
            try:
                logging.info('Fetching Amazon order statuses...')
                amazon_packages_count, amazon_delivered_today, amazon_packages_items = get_amazon_packages_arriving_today(AMAZON_USERNAME, AMAZON_PASSWORD)
                logging.info(f'AMAZON: {amazon_packages_count} arriving today, {amazon_delivered_today} delivered')
            except:
                encountered_error = True
                logging.error(f'Failed to fetch Amazon tracking data:\n{traceback.format_exc()}')
            redis.set(REDIS_AMAZON_KEY, pickle.dumps((amazon_packages_count, amazon_delivered_today, amazon_packages_items)))

        if encountered_error:
            logging.critical('Exiting due to earlier exception')
            sys.exit(1)

        logging.info('Sleeping...')
        time.sleep(900)  # 15 minutes


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--usps-mode', choices=[UspsApiType.parcelsapp.value, UspsApiType.native.value], default=UspsApiType.parcelsapp.value,
    #                     help=f'The API type to use for USPS. "{UspsApiType.parcelsapp.value}" (default) uses the parcelsapp API, "native" uses the USPS tracking API.'
    #                     )
    args = parser.parse_args()
    main(args)
