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


def main():
    redis = Redis(host='localhost', port=6379, db=0)
    redis.flushall()
    while True:
        logging.info('Fetching latest Amazon order status')
        amazon_packages_count, amazon_delivered_today, amazon_packages_items = get_amazon_packages_arriving_today(AMAZON_USERNAME, AMAZON_PASSWORD)
        redis.set('amazon_packages', pickle.dumps((amazon_packages_count, amazon_delivered_today, amazon_packages_items)))
        logging.info(f'{amazon_packages_count} Amazon packages arriving today, {amazon_delivered_today} Amazon packages delivered')
        time.sleep(1800)  # 30 minutes


if __name__ == '__main__':
    main()
