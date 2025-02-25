import logging
import re
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel

from lib.imap.search import fetch_emails_last_3_days

_LOGGER = logging.getLogger('USPS')


def get_usps_packages_arriving_today(folder: str):
    _LOGGER.info('Searching for USPS emails...')
    arriving_today = []
    delivered_today = []
    for _, item in usps_fetch_items_from_emails(folder).items():
        if item.delivered_date is None and item.arriving_date == date.today():
            arriving_today.append(item)
        elif item.delivered_date == date.today():
            delivered_today.append(item)

    return len(arriving_today), len(delivered_today)


class UspsItem(BaseModel):
    tracking_id: str
    arriving_date: Optional[date] = None
    delivered_date: Optional[date] = None


def usps_fetch_items_from_emails(folder: str):
    emails = fetch_emails_last_3_days('auto-reply@usps.com', folder)
    items = {}
    for email in emails:
        tracking_id = re.search(r'\b(9\d{15,21})\b', email.subject).group(1)
        item = UspsItem(
            tracking_id=tracking_id,
            arriving_date=datetime.strptime(re.search(
                r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}',
                email.subject).group(0), "%A, %B %d, %Y").date() if 'Expected Delivery' in email.subject else None,
            delivered_date=email.date if 'Item Delivered' in email.subject else None,
        )
        if not items.get(tracking_id):
            items[tracking_id] = item
        else:
            if item.delivered_date is not None:
                items[tracking_id].delivered_date = item.delivered_date
    return items
