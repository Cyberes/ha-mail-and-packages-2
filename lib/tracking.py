import json
import logging
from datetime import date, datetime, timedelta
from typing import Optional, Set

from dateutil.parser import parse
from pydantic import BaseModel, field_validator

from lib.parcelsapp import fetch_parcel_data

_LOGGER = logging.getLogger('Tracking')


class TrackedPackage(BaseModel):
    tracking_id: str
    arriving_date: Optional[date] = None
    delivered_date: Optional[date] = None

    class Config:
        validate_assignment = True

    @field_validator('arriving_date', 'delivered_date', mode='before')
    @classmethod
    def convert_datetime_to_date(cls, value):
        if isinstance(value, datetime):
            return value.date()
        return value


def process_tracking_ids(tracking_ids: Set[str], api_key: str, carrier: str):
    carrier_logger = logging.getLogger(carrier)
    arriving_today = []
    upcoming_tracking_ids = []
    delivered_today = []
    delivered_tracking_ids = []
    carrier_logger.info(f'Parsing {len(tracking_ids)} tracking IDs...')

    for tracking_id in tracking_ids:
        item = parse_parcelapp_tracking(tracking_id, api_key)
        if item.delivered_date is None and item.arriving_date == date.today():
            arriving_today.append(item)
        elif item.delivered_date is not None:
            if item.delivered_date == date.today():
                delivered_today.append(item)
            carrier_logger.info(f'{item.tracking_id} delivered on {item.delivered_date}')
        elif item.arriving_date is not None and item.arriving_date > date.today():
            carrier_logger.info(f'{item.tracking_id} arriving on {item.arriving_date} ({(item.arriving_date - date.today()).days} days)')

        if item.delivered_date is not None and item.delivered_date >= date.today() - timedelta(days=1):
            delivered_tracking_ids.append(tracking_id)
        elif item.arriving_date is not None and item.arriving_date >= date.today() - timedelta(days=1):
            upcoming_tracking_ids.append(tracking_id)

    return len(arriving_today), len(delivered_today), upcoming_tracking_ids + delivered_tracking_ids


def parse_parcelapp_tracking(tracking_id: str, api_key: str):
    item = TrackedPackage(tracking_id=tracking_id)
    data = fetch_parcel_data(api_key, [tracking_id])

    if 'status' not in data.keys():
        raise KeyError(f'Bad parcelsapp JSON:\n{json.dumps(data)}')

    if data['status'] not in ['delivered', 'transit']:
        _LOGGER.info(json.dumps(data))

    eta = data.get('delivered_by')
    if data.get('error'):
        _LOGGER.warning(f'Parcel API error for tracking code "{tracking_id}": {data["error"]}')
    elif data['status'] == 'delivered':
        item.delivered_date = parse(data['lastState']['date'])
    elif data['status'] == 'pickup':
        item.arriving_date = date.today()
    elif eta is not None:
        item.arriving_date = datetime.strptime(eta, '%Y-%m-%dT%H:%M:%SZ')

    return item
