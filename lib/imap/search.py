import email
import re
from datetime import datetime, timedelta

from lib.imap.connection import IMAPConnectionHandler
from lib.imap.email import Email


def fetch_emails_last_n_days(days: int = 14, sender: str = None, folder: str = None):
    since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
    with IMAPConnectionHandler(folder) as conn:
        search_criteria = f'(SINCE "{since_date}")'
        if sender:
            search_criteria += f' (FROM "{sender}")'

        _, message_numbers = conn.search(None, search_criteria)

        emails = []
        for num in message_numbers[0].split():
            _, msg_data = conn.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            email_message = email.message_from_bytes(raw_email)
            email_obj = Email(email_message)
            emails.append(email_obj)

    return emails


def search_subject_for_regex(from_email: str, folder: str, regex: str):
    emails = fetch_emails_last_n_days(sender=from_email, folder=folder)
    items = set()
    for item in emails:
        tracking_id = re.search(regex, item.subject)
        if tracking_id:
            items.add(tracking_id.group(1))
            break
    return items
