import json
import logging
import os
import pickle
import sys
import time

import paho.mqtt.client as mqtt
from redis import Redis

from lib.consts import REDIS_DB, REDIS_USPS_KEY, REDIS_AMAZON_KEY, REDIS_FEDEX_KEY, REDIS_UPS_KEY

logging.basicConfig(level=logging.INFO)

MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', 1883))
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'mail-and-packages-2')
MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX', 'mail-and-packages-2')

if not MQTT_BROKER_HOST:
    logging.critical('Missing the MQTT_BROKER_HOST environment variable')
    sys.exit(1)

client = mqtt.Client(client_id=MQTT_CLIENT_ID)
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.will_set(MQTT_TOPIC_PREFIX + '/status', payload='Offline', qos=1, retain=True)
client.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
client.loop_start()


def publish(topic: str, msg: str, attributes: dict = None):
    topic_expanded = MQTT_TOPIC_PREFIX + '/' + topic
    retries = 10
    for i in range(retries):  # retry
        result = client.publish(topic_expanded, msg)
        if attributes:
            client.publish(topic_expanded + '/attributes', json.dumps(attributes))
        status = result[0]
        if status == 0:
            logging.info(f'Sent {msg} to topic {topic_expanded}')
            return
        else:
            logging.warning(f'Failed to send message to topic {topic_expanded}: {result}. Retry {i + 1}/{retries}')
            time.sleep(10)
    logging.error(f'Failed to send message to topic {topic_expanded}.')


def main():
    redis = Redis(db=REDIS_DB)
    amazon_data: bytes = redis.get(REDIS_AMAZON_KEY)
    usps_data: bytes = redis.get(REDIS_USPS_KEY)
    fedex_data: bytes = redis.get(REDIS_FEDEX_KEY)
    ups_data: bytes = redis.get(REDIS_UPS_KEY)
    while amazon_data is None or usps_data is None:
        logging.warning('Redis has not been populated yet. Is cache.py running? Sleeping 10s...')
        time.sleep(10)
        amazon_data = redis.get(REDIS_AMAZON_KEY)
        usps_data = redis.get(REDIS_USPS_KEY)
        fedex_data = redis.get(REDIS_FEDEX_KEY)
        ups_data = redis.get(REDIS_UPS_KEY)
    amazon_arriving_count, amazon_delivered_count, amazon_packages_items = pickle.loads(amazon_data)
    publish('amazon-arriving-count', amazon_arriving_count, attributes={'items': amazon_packages_items})
    publish('amazon-delivered-count', amazon_delivered_count)
    usps_arriving_count, usps_delivered_count, usps_recent_tracking_ids = pickle.loads(usps_data)
    publish('usps-arriving-count', usps_arriving_count, attributes={'tracking_ids': usps_recent_tracking_ids})
    publish('usps-delivered-count', usps_delivered_count)
    fedex_arriving_count, fedex_delivered_count, fedex_recent_tracking_ids = pickle.loads(fedex_data)
    publish('fedex-arriving-count', fedex_arriving_count, attributes={'tracking_ids': fedex_recent_tracking_ids})
    publish('fedex-delivered-count', fedex_delivered_count)
    ups_arriving_count, ups_delivered_count, ups_recent_tracking_ids = pickle.loads(ups_data)
    publish('ups-arriving-count', ups_arriving_count, attributes={'tracking_ids': ups_recent_tracking_ids})
    publish('ups-delivered-count', ups_delivered_count)


if __name__ == '__main__':
    main()
