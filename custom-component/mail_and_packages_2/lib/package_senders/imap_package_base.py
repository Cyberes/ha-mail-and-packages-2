import email
import re
from datetime import date, timedelta
from typing import List, Union

from lib.imap.connection import IMAPConnectionHandler
from lib.imap.email import Email


def search_re_one_result(regex: str, string: str, what: str) -> str:
    matches = re.findall(regex, string)
    if len(matches) == 0:
        raise Exception(f'No {what} found')
    elif len(matches) > 1:
        raise Exception(f'Multiple {what}s found')
    return matches[0]


class ImapPackageSender:
    def __init__(self, name: str, from_email: str, arrival_date_regex: Union[str, None]):
        self._name = name
        self._from_email = from_email
        self._arrival_date = arrival_date_regex

    def search_arrival_date(self, raw_email: str) -> Union[str, None]:
        if self._arrival_date is None:
            return None
        try:
            return search_re_one_result(self._arrival_date, raw_email, 'arrival date')
        except Exception as e:
            raise Exception(f"{self._name}: {e}")

    def search_emails(self, folder: str, days: int) -> List[Email]:
        emails = []
        with IMAPConnectionHandler(folder) as imap:
            three_days_ago = (date.today() - timedelta(days=days)).strftime("%d-%b-%Y")
            search_criteria = f'(FROM "{self._from_email}" SINCE "{three_days_ago}")'
            _, message_numbers = imap.search(None, search_criteria)
            message_numbers = message_numbers[0].split()
            for num in message_numbers:
                _, msg_data = imap.fetch(num, "(RFC822)")
                email_obj = Email(email.message_from_bytes(msg_data[0][1]))
                emails.append(email_obj)
        return emails

    def parse_email(self, email_obj: Email):
        raise NotImplementedError

    def parse_arrival_date(self, date_str: str):
        raise NotImplementedError
