import logging

from func_timeout import func_timeout

from lib.imap.search import fetch_emails_last_n_days
from lib.tracking import process_tracking_ids

_LOGGER = logging.getLogger('Fedex')


def get_fedex_packages_arriving_today(folder: str, api_key: str):
    def run():
        _LOGGER.info('Searching for Fedex emails...')
        tracking_ids = set()
        for email in fetch_emails_last_n_days(14, 'TrackingUpdates@fedex.com', folder):
            # Fedex has a million different tracking ID formats but they are always the last item in the subject.
            # We'll just feed whatever it is into the API.
            tracking_ids.add(email.subject.split(' ')[-1])

        return process_tracking_ids(tracking_ids, api_key, 'Fedex')

    return func_timeout(60, run)
