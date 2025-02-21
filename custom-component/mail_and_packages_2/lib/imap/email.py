from datetime import datetime


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

    def _get_date(self):
        date_str = self.message["Date"]
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")

    def _get_subject(self):
        return self.message["Subject"]

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
