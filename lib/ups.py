import logging

from func_timeout import func_timeout

from lib.imap.search import fetch_emails_last_n_days
from lib.regex import find_re_matches
from lib.tracking import process_tracking_ids

_LOGGER = logging.getLogger('UPS')

_USPS_TRACKING_RE = [r'1Z[A-Z0-9]{16}']


def get_ups_packages_arriving_today(folder: str, api_key: str):
    def run():
        _LOGGER.info('Searching for UPS emails...')
        tracking_ids = set()
        for email in fetch_emails_last_n_days(14, 'pkginfo@ups.com', folder):
            if 'Tracking Number' in email.subject:
                # Some UPS emails always put the tracking number at the end of the subject.
                tracking_ids.add(email.subject.split(' ')[-1])
            else:
                # Fall back to matching regex.
                for x in find_re_matches(email.html_body, _USPS_TRACKING_RE):
                    tracking_ids.add(x)
        return process_tracking_ids(tracking_ids, api_key, 'UPS')

    return func_timeout(60, run)
