import logging
import pickle
import sys
import traceback
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
    elif ('arriving' in text_lower or 'expected' in text_lower) and len(text_lower.split(' ')) > 2:
        if 'overnight' in text_lower:
            return datetime.today() + timedelta(days=1)

        if 'expected' in text_lower:
            date_text = text_lower.replace('now expected by ', '').strip()
        elif 'arriving' in text_lower:
            date_range = text_lower.replace('arriving', '').strip()
            date_text = date_range.split('-')[0]
        else:
            date_text = text_lower

        try:
            return datetime.strptime(date_text.strip(), '%B %d').date().replace(year=today.year)
        except ValueError:
            raise ValueError(f'Failed to parse date: "{text_lower}"\n{traceback.format_exc()}')
    elif text_lower in ['cannot display current status', 'your package may be lost', 'your delivery is still on the way']:
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
    raise ValueError(f'Unrecognized date text: "{text}"')


def get_amazon_session(username: str, password: str) -> AmazonSession:
    s_bytes: bytes = _REDIS.get('amazon_session')
    if s_bytes is not None:
        _LOGGER.info('Loaded cached Amazon session')
        amazon_session = pickle.loads(s_bytes)
    else:
        amazon_session = AmazonSession(username, password)
        _LOGGER.info('Created new Amazon session')

    if not amazon_session.is_authenticated:
        _LOGGER.info('Logging into Amazon...')
        try:
            amazon_session.login()
            _LOGGER.info('Logged into Amazon successfully.')
        except Exception as e:
            _LOGGER.error(f'Failed to log into Amazon: {e}')
            sys.exit(1)
    else:
        _LOGGER.info('Amazon session already authenticated')

    _REDIS.set('amazon_session', pickle.dumps(amazon_session))
    _LOGGER.info('Cached Amazon session')

    return amazon_session


def get_amazon_packages_arriving_today(username: str, password: str):
    amazon_session = get_amazon_session(username, password)
    amazon_orders = AmazonOrders(amazon_session)
    try:
        _LOGGER.info('Fetching Amazon orders...')
        orders = amazon_orders.get_order_history(year=date.today().year)
        _LOGGER.info(f"Fetched {len(orders)} orders from Amazon.")
    except Exception as e:
        _LOGGER.error(f"Failed to fetch order history: {e}")
        sys.exit(1)

    arriving_today = 0
    delivered_today = 0
    items_arriving_today = []

    for order in orders:
        for item in order.shipments:
            status = item.delivery_status.lower()
            status_str = status.split(' ')[0]
            if status_str in ['return', 'refunded'] or 'running late' in status or 'problem occurred' in status:
                continue
            delivery_date = relative_date_to_date(status)
            if delivery_date == date.today():
                if status_str == 'delivered':
                    delivered_today += 1
                else:
                    arriving_today += 1
                items_arriving_today.extend([x.title[:22] + '...' for x in item.items])

    return arriving_today, delivered_today, items_arriving_today
