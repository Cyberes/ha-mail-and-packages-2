import logging
import os
import pickle
import sys
import time

from redis import Redis

from lib.amazon import get_amazon_packages_arriving_today

logging.basicConfig(level=logging.INFO)

AMAZON_USERNAME = os.getenv('AMAZON_USERNAME')
AMAZON_PASSWORD = os.getenv('AMAZON_PASSWORD')
if not AMAZON_USERNAME or not AMAZON_PASSWORD:
    logging.critical('Must set AMAZON_USERNAME and AMAZON_PASSWORD environment variables')
    print(AMAZON_USERNAME, AMAZON_PASSWORD)
    sys.exit(1)

IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_USERNAME = os.getenv('IMAP_USERNAME')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
IMAP_FOLDER = os.getenv('IMAP_FOLDER')
if not IMAP_HOST or not IMAP_USERNAME or not IMAP_PASSWORD or not IMAP_FOLDER:
    logging.critical('Must set IMAP_HOST and IMAP_USERNAME and IMAP_PASSWORD and IMAP_FOLDER environment variables')
    print(IMAP_HOST, IMAP_USERNAME, IMAP_PASSWORD, IMAP_FOLDER)
    sys.exit(1)


def main():
    redis = Redis(host='localhost', port=6379, db=0)
    redis.flushall()
    while True:
        # logging.info('Fetching USPS tracking data')
        # IMAPConnection.initialise(IMAP_HOST, IMAP_USERNAME, IMAP_PASSWORD)
        # usps_arriving_today, usps_delivered_today = get_usps_packages_arriving_today(IMAP_FOLDER)
        # IMAPConnection.close_connection()
        usps_arriving_today = 0
        usps_delivered_today = 0
        redis.set('usps_packages', pickle.dumps((usps_arriving_today, usps_delivered_today)))
        logging.info(f'USPS: {usps_arriving_today} arriving, {usps_delivered_today} delivered')
        # TODO: send tracking numbers to HA so that the dashboard card can link to the tracking page and not have to log in (https://tools.usps.com/go/TrackConfirmAction?tLabels=123%2Casd%2Cabc%2C)

        logging.info('Fetching Amazon order statuses')
        amazon_packages_count, amazon_delivered_today, amazon_packages_items = get_amazon_packages_arriving_today(AMAZON_USERNAME, AMAZON_PASSWORD)
        redis.set('amazon_packages', pickle.dumps((amazon_packages_count, amazon_delivered_today, amazon_packages_items)))
        logging.info(f'AMAZON: {amazon_packages_count} arriving, {amazon_delivered_today} delivered')
        time.sleep(1800)  # 30 minutes


if __name__ == '__main__':
    main()
