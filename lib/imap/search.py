import email
from datetime import datetime, timedelta

from lib.imap.connection import IMAPConnectionHandler
from lib.imap.email import Email


def fetch_emails_last_3_days(sender: str = None, folder: str = None):
    since_date = (datetime.now() - timedelta(days=3)).strftime("%d-%b-%Y")
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
