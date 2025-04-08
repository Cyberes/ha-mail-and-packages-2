import logging

from func_timeout import func_timeout

from lib.imap.search import search_subject_for_regex
from lib.tracking import process_tracking_ids

_LOGGER = logging.getLogger('USPS')


def get_usps_packages_arriving_today(folder: str, api_key: str):
    def run():
        _LOGGER.info('Searching for USPS emails...')
        tracking_ids = set()
        for tracking_id in search_subject_for_regex('auto-reply@usps.com', folder, r'\b(9\d{15,21})\b'):
            tracking_ids.add(tracking_id)
        return process_tracking_ids(tracking_ids, api_key, 'USPS')

    return func_timeout(60, run)
