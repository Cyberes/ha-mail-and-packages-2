import logging

from func_timeout import func_timeout

from lib.imap.search import fetch_emails_last_n_days
from lib.tracking import process_tracking_ids

_LOGGER = logging.getLogger('USPS')


def get_usps_packages_arriving_today(folder: str, api_key: str):
    def run():
        _LOGGER.info('Searching for USPS emails...')
        tracking_ids = set()
        for email in fetch_emails_last_n_days(14, 'auto-reply@usps.com', folder):
            # USPS emails always put the tracking number at the end of the subject.
            tracking_ids.add(email.subject.split(' ')[-1])
        return process_tracking_ids(tracking_ids, api_key, 'USPS')

    return func_timeout(60, run)
