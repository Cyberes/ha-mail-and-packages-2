import logging
import re
from datetime import date
from typing import Optional

from dateutil.parser import parse
from pydantic import BaseModel

from lib.imap.search import fetch_emails_last_3_days
from lib.parcelapp import fetch_parcel_data

_LOGGER = logging.getLogger('USPS')


class UspsItem(BaseModel):
    tracking_id: str
    arriving_date: Optional[date] = None
    delivered_date: Optional[date] = None


def get_usps_packages_arriving_today(folder: str, parcel_api_key: str):
    _LOGGER.info('Searching for USPS emails...')
    arriving_today = []
    delivered_today = []
    for tracking_id in usps_fetch_items_from_emails(folder):
        item = UspsItem(tracking_id=tracking_id)
        data = fetch_parcel_data(parcel_api_key, [tracking_id])
        if data['status'] == 'delivered':
            item.delivered_date = parse(data['lastState']['date'])
        # elif

    # if item.delivered_date is None and item.arriving_date == date.today():
    #     arriving_today.append(item)
    # elif item.delivered_date == date.today():
    #     delivered_today.append(item)

    return len(arriving_today), len(delivered_today)


def usps_fetch_items_from_emails(folder: str):
    emails = fetch_emails_last_3_days('auto-reply@usps.com', folder)
    items = set()
    for email in emails:
        tracking_id = re.search(r'\b(9\d{15,21})\b', email.subject)
        if tracking_id:
            items.add(tracking_id.group(1))
    return items
