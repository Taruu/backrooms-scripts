import json
from urllib.parse import urlparse

import magic
import requests
from lxml import html
from setuptools._distutils.command.config import config

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


class ArticleFile:
    def __init__(self, page_name: str, filename: str,
                 file_id=None, file_bytes=None, mime_type=None,
                 session=load_session()):
        """
        file_bytes = None : if we create new image for page we forse setup bytes
        """
        self.file_id: int = file_id
        self.is_file_new = False
        self.session = session
        self.page_name: str = page_name
        self.filename: str = filename
        self._file_bytes: bytes = file_bytes
        self.mime_type: str = mime_type

        if file_bytes:
            self.is_file_new = True
            self.mime_type: str = magic.from_buffer(self.file_bytes, mime=True)

    def _get_id_by_name(self):
        file_json = requests.get(f"{config.API_ARTICLES}{self.page_name}/files").json()
        for file_info in file_json.get("files"):
            if self.filename == file_info.get("name"):
                self.file_id = file_info.get("id")

    def upload(self, overwrite=False, check=False):
        """
        overwrite = False : status about overwrite file
        """
        if overwrite:
            self.remove()

        headers = {
            "X-File-Name": self.filename,
            "Content-Type": self.mime_type,
            "Content-Length": str(len(self.file_bytes))
        }

        result = self.session.post(f"{config.API_ARTICLES}{self.page_name}/files", data=self._file_bytes,
                                   headers=headers)
        if result.status_code not in [200, 409]:
            text = f"Fail to upload image: {self.page_name}/{self.filename}"
            config.logger.error(text)
            raise Exception(text)
        else:
            return True

    def remove(self):
        result = self.session.delete(f"{config.API_ARTICLES}/files/{file_info.get('id')}", cookies=cookies)
        if result.status_code != 200:
            print(result.status_code, result.content)
        break

    def rename(self):
        pass

    def check(self):
        status_code = self.session.head(f"{config.FILES_URL}{self.page_name}/{self.filename}").status_code
        # if file already exist
        if status_code == 200:
            return True
        return False

    def check_hash(self):
        # TODO check checksum file on server and local
        pass

    @property
    def file_bytes(self):
        if self._file_bytes is bytes:
            return self._file_bytes
        self.session.get()
        pass

    @file_bytes.setter
    def file_bytes(self, new_file_bytes: bytes):
        self._file_bytes = new_file_bytes
