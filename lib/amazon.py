import logging
import pickle
import sys
from datetime import date, timedelta, datetime

from amazonorders.orders import AmazonOrders
from amazonorders.session import AmazonSession
from redis import Redis

_REDIS = Redis(host='localhost', port=6379, db=0)
_LOGGER = logging.getLogger('AMAZON')


def relative_date_to_date(text: str) -> date | None:
    today = datetime.today()
    text_lower = text.lower()

    if 'today' in text_lower:
        return today.date()

    elif 'tomorrow' in text_lower:
        return (today + timedelta(days=1)).date()

    elif 'delivered' in text_lower:
        date_str = text_lower.replace('delivered', '').strip()
        try:
            delivered_date = datetime.strptime(date_str, '%B %d').date()
            delivered_date = delivered_date.replace(year=today.year)
            return delivered_date
        except ValueError:
            pass

    elif 'arriving' in text_lower:
        if 'overnight' in text_lower:
            return datetime.today() + timedelta(days=1)
        else:
            date_range = text_lower.replace('arriving', '').strip()
            start_date_str = date_range.split('-')[0]
            return datetime.strptime(start_date_str.strip(), '%B %d').date().replace(year=today.year)
    elif text_lower == 'cannot display current status':
        return None
    else:
        weekdays = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }
        for day_name, day_num in weekdays.items():
            if day_name in text_lower:
                days_ahead = day_num - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return (today + timedelta(days=days_ahead)).date()

    raise ValueError(f"Unrecognized date text: '{text}'")


def get_amazon_session(username: str, password: str) -> AmazonSession:
    s_bytes: bytes = _REDIS.get('amazon_session')
    if s_bytes is not None:
        _LOGGER.info('Loaded cached Amazon session')
        return pickle.loads(s_bytes)
    else:
        s = AmazonSession(username, password)
        # TODO: https://github.com/alexdlaird/amazon-orders/issues/49
        _REDIS.set('amazon_session', pickle.dumps(s))
        _LOGGER.info('Created and cached new Amazon session')
        return s


def get_amazon_packages_arriving_today(username: str, password: str):
    amazon_session = get_amazon_session(username, password)
    
    if not amazon_session.is_authenticated:
        try:
            amazon_session.login()
            logging.info("Logged into Amazon successfully.")
        except Exception as e:
            logging.error(f"Failed to log into Amazon: {e}")
            sys.exit(1)

    amazon_orders = AmazonOrders(amazon_session)
    try:
        orders = amazon_orders.get_order_history(year=date.today().year)
        logging.info(f"Fetched {len(orders)} orders from Amazon.")
    except Exception as e:
        logging.error(f"Failed to fetch order history: {e}")
        sys.exit(1)

    arriving_today = 0
    delivered_today = 0
    items_arriving_today = []

    for order in orders:
        for item in order.shipments:
            status = item.delivery_status.lower()
            status_str = status.split(' ')[0]
            if status_str in ['return', 'refunded'] or 'running late' in status:
                continue
            delivery_date = relative_date_to_date(status)
            if delivery_date == date.today():
                if status_str == 'delivered':
                    delivered_today += 1
                else:
                    arriving_today += 1
                items_arriving_today.extend([x.title[:22] + '...' for x in item.items])

    return arriving_today, delivered_today, items_arriving_today
