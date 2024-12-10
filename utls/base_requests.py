import json
from urllib.parse import urlparse

import requests
from lxml import html

import config


def login(username: str, password):
    """Write session into file"""
    session = requests.Session()

    headers = {
        "User-Agent": config.values.get('requests.user_agent'),
        "Referer": config.LOGIN_URL
    }
    response = session.get(config.LOGIN_URL)

    tree = html.fromstring(response.content)
    csrf_token = tree.xpath('//input[@name="csrfmiddlewaretoken"]/@value')[0]

    payload = {
        "csrfmiddlewaretoken": csrf_token,
        "username": username,
        "password": password
    }

    session.post(config.LOGIN_URL, data=payload, headers=headers)
    with open(config.values.get("requests.session_file"), "w") as file_session:
        file_session.write(json.dumps(session.cookies.get_dict()))


def load_session() -> requests.Session:
    """Load session form file"""
    session = requests.Session()

    session.headers.update(
        {"User-Agent": config.values.get('requests.user_agent')}
    )
    with open(config.values.get("requests.session_file"), "r") as file_session:
        session.cookies.update({json.loads(file_session.read())})

    return session


class Article:
    def __init__(self, page_name: str, session=load_session()):
        self.session = session
        self.page_name = page_name

    def get_source(self) -> dict:
        return self.session.get(f'{config.API_ARTICLES}{self.page_name}').json()

    def files_list(self):
        pass

    def upload_file(self):
        pass

    def remove_file(self):
        pass


class File:
    def __init__(self, page_name: str, filename: str, file_bytes=None, session=load_session()):
        self.session = session
        self.page_name = page_name
        self.filename = filename
        self._file_bytes = file_bytes

    @property
    def file_bytes(self):
        if self._file_bytes is bytes:
            return self._file_bytes
        #self.session.get()
        pass

    @file_bytes.setter
    def file_bytes_set(self, new_file_bytes: bytes):
        pass
