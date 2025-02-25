import imaplib
from threading import Lock


class IMAPConnection:
    __connection = None
    lock = Lock()

    @classmethod
    def initialise(cls, host, username, password, port=993, ssl=True):
        if cls.__connection is not None:
            raise Exception('IMAP connection is already initialised')
        if ssl:
            cls.__connection = imaplib.IMAP4_SSL(host, port)
        else:
            cls.__connection = imaplib.IMAP4(host, port)
        cls.__connection.login(username, password)

    @classmethod
    def get_connection(cls):
        if cls.__connection is None:
            raise Exception('IMAP connection is not initialised')
        return cls.__connection

    @classmethod
    def close_connection(cls):
        if cls.__connection is not None:
            cls.__connection.logout()
            cls.__connection = None


class IMAPConnectionHandler:
    def __init__(self, folder="INBOX"):
        self.folder = folder

    def __enter__(self):
        IMAPConnection.lock.acquire()
        self.conn = IMAPConnection.get_connection()
        self.conn.select(self.folder, readonly=True)
        return self.conn

    def __exit__(self, exception_type, exception_value, exception_traceback):
        IMAPConnection.lock.release()
