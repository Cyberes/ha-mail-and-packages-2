from datetime import datetime, date
from email.header import decode_header


class Email:
    def __init__(self, message):
        self.message = message
        self.sender = self._get_sender()
        self.date = self._get_date()
        self.subject = self._get_subject()
        self.body = self._get_body()
        self.html_body = self._get_html_body()

    def _get_sender(self):
        return self.message["From"]

    def _get_date(self) -> date:
        date_str = self.message["Date"]
        # Remove timezone name in parentheses if present
        date_str = date_str.split('(')[0].strip()

        # Try different date formats
        date_formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # RFC 2822 format
            "%a, %d %b %Y %H:%M:%S %Z",  # With timezone name
            "%d %b %Y %H:%M:%S %z",  # Without day name
            "%a, %d %b %Y %H:%M:%S",  # Without timezone
        ]

        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format).date()
            except ValueError:
                continue

        # If no format matches, raise an error
        raise ValueError(f"Unable to parse date string: {date_str}")

    def _get_subject(self):
        return self._decode_header(self.message["Subject"])

    def _get_body(self):
        if self.message.is_multipart():
            for part in self.message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
        else:
            return self.message.get_payload(decode=True).decode()

    def _get_html_body(self):
        if self.message.is_multipart():
            for part in self.message.walk():
                if part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode()
        return None

    def __str__(self):
        return f"From: {self.sender}\nDate: {self.date}\nSubject: {self.subject}\n\n{self.body}"

    def _decode_header(self, header):
        if header is None:
            return None

        decoded_parts = decode_header(header)
        decoded_string = ""

        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                if charset:
                    decoded_string += part.decode(charset)
                else:
                    decoded_string += part.decode()
            else:
                decoded_string += part

        return decoded_string
