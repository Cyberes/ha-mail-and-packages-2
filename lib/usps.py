import json
import logging
import re
from enum import Enum

from dateutil.parser import parse
from func_timeout import func_timeout

from lib.imap.search import fetch_emails_last_n_days
from lib.parcelsapp import fetch_parcel_data

_LOGGER = logging.getLogger('USPS')

from datetime import date, datetime, timedelta
from typing import Optional
from pydantic import BaseModel, field_validator


class UspsItem(BaseModel):
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


class UspsApiType(Enum):
    parcelsapp = 'parcelsapp'
    native = 'native'


def get_usps_packages_arriving_today(folder: str, api_key: str, api_type: str):
    def run():
        _LOGGER.info('Searching for USPS emails...')
        arriving_today = []
        upcoming_tracking_ids = []
        delivered_today = []
        delivered_tracking_ids = []
        for tracking_id in usps_fetch_items_from_emails(folder):
            if api_type == UspsApiType.parcelsapp.value:
                item = usps_parcel_app(tracking_id, api_key)
            elif api_type == UspsApiType.native.value:
                raise NotImplementedError
            else:
                raise ValueError

            if item.delivered_date is None and item.arriving_date == date.today():
                arriving_today.append(item)
            elif item.delivered_date == date.today():
                delivered_today.append(item)
            elif item.arriving_date is not None and item.arriving_date > date.today():
                _LOGGER.info(f'{item.tracking_id} arriving on {item.arriving_date} ({(item.arriving_date - date.today()).days} days)')

            if item.delivered_date is not None and item.delivered_date >= date.today() - timedelta(days=1):
                delivered_tracking_ids.append(tracking_id)
            elif item.arriving_date is not None and item.arriving_date >= date.today() - timedelta(days=1):
                upcoming_tracking_ids.append(tracking_id)
        return len(arriving_today), len(delivered_today), upcoming_tracking_ids + delivered_tracking_ids

    # Prevent the IMAP call from freezing and stopping everything.
    return func_timeout(30, run)


def usps_fetch_items_from_emails(folder: str) -> set:
    emails = fetch_emails_last_n_days(sender='auto-reply@usps.com', folder=folder)
    items = set()
    for email in emails:
        tracking_id = re.search(r'\b(9\d{15,21})\b', email.subject)
        if tracking_id:
            items.add(tracking_id.group(1))
    return items


def usps_parcel_app(tracking_id: str, api_key: str):
    item = UspsItem(tracking_id=tracking_id)
    data = fetch_parcel_data(api_key, [tracking_id])

    # TODO: dumping state to see what the "status" tag shows when out for delivery
    _LOGGER.info(json.dumps(data))

    eta = data.get('delivered_by')
    if data.get('error'):
        _LOGGER.warning(f'Parcel API error for tracking code "{tracking_id}": {data["error"]}')
    elif data['status'] == 'delivered':
        item.delivered_date = parse(data['lastState']['date'])
    # TODO: need to figure out what the status looks like when its out for delivery. Then, set arriving_date to today
    # elif something:
    elif eta is not None:
        item.arriving_date = datetime.strptime(eta, '%Y-%m-%dT%H:%M:%SZ')

    return item
