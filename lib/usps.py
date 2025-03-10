import logging
import re
from datetime import date, datetime
from enum import Enum
from typing import Optional

from dateutil.parser import parse
from pydantic import BaseModel, field_validator

from lib.imap.search import fetch_emails_last_3_days
from lib.parcelsapp import fetch_parcel_data, parcelsapp_get_attr

_LOGGER = logging.getLogger('USPS')


class UspsItem(BaseModel):
    tracking_id: str
    arriving_date: Optional[date] = None
    delivered_date: Optional[date] = None

    class Config:
        validate_assignment = True

    @classmethod
    @field_validator('arriving_date', 'delivered_date', mode='before')
    def convert_datetime_to_date(cls, value):
        if isinstance(value, datetime):
            return value.date()
        return value


class UspsApiType(Enum):
    parcelsapp = 'parcelsapp'
    native = 'native'


def get_usps_packages_arriving_today(folder: str, api_key: str, api_type: str):
    _LOGGER.info('Searching for USPS emails...')
    arriving_today = []
    delivered_today = []
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
    return len(arriving_today), len(delivered_today)


def usps_fetch_items_from_emails(folder: str) -> set:
    emails = fetch_emails_last_3_days('auto-reply@usps.com', folder)
    items = set()
    for email in emails:
        tracking_id = re.search(r'\b(9\d{15,21})\b', email.subject)
        if tracking_id:
            items.add(tracking_id.group(1))
    items = {'9400108105462561148496', '9300110571012423728705', '9400108105462555931813'}
    return items


def usps_parcel_app(tracking_id: str, api_key: str):
    item = UspsItem(tracking_id=tracking_id)
    data = fetch_parcel_data(api_key, [tracking_id])
    eta = parcelsapp_get_attr(data, 'eta')
    if data.get('error'):
        _LOGGER.warning(f'Parcel API error for tracking code "{tracking_id}": {data["error"]}')
    elif data['status'] == 'delivered':
        item.delivered_date = parse(data['lastState']['date'])
    elif eta is not None:
        item.arriving_date = parse(eta[1])

    return item
