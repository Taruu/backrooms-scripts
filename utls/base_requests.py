import json
from urllib.parse import urlparse
import xxhash

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


# Normal Session
normal_session = requests.Session()

# Session with proxy
proxy_session = requests.Session()
proxy_session.proxies = config.PROXY

# Session with auth for target site
authorized_session = requests.Session()

authorized_session.headers.update(
    {"User-Agent": config.values.get('requests.user_agent')}
)
with open(config.values.get("requests.session_file"), "r") as file_session:
    authorized_session.cookies.update({json.loads(file_session.read())})


class Article:
    def __init__(self, page_name: str, session=authorized_session):
        self.session = session
        self.page_name = page_name

        self.page_source = self.session.get(f'{config.API_ARTICLES}{self.page_name}').json()

        self.files_list()

    def get_source(self) -> dict:
        pass

    def files_list(self):
        pass


class ArticleFile:
    def __init__(self, page_name: str, filename: str,
                 file_id=None, file_bytes=None, mime_type=None,
                 session=authorized_session):
        """
        file_bytes = None : if we create new image for page we forse setup bytes
        """

        self.is_file_new = False

        self.file_id: int = file_id
        self.session = session
        self.page_name: str = page_name
        self.filename: str = filename

        self._file_bytes: bytes = file_bytes
        self.mime_type: str = mime_type

        self._file_hash: str = None

        if file_bytes:
            self.is_file_new = True
            self.mime_type: str = magic.from_buffer(file_bytes, mime=True)

            hash_obj = xxhash.xxh64()
            hash_obj.update(file_bytes)
            self._file_hash = hash_obj.hexdigest()

    def _get_id_by_name(self):
        if self.file_id:
            return self.file_id
        file_json = requests.get(f"{config.API_ARTICLES}{self.page_name}/files").json()
        for file_info in file_json.get("files"):
            if self.filename == file_info.get("name"):
                self.file_id = file_info.get("id")
                return self.file_id
        return None

    @property
    def file_url(self):
        return f"{config.FILES_URL}{self.page_name}/{self.filename}"

    def upload(self, overwrite=False, check=False):
        """
        overwrite = False : status about overwrite file
        """
        if overwrite and not self.is_file_new:
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
            self.is_file_new = False
            return True

    def remove(self):
        """Remove file"""
        if self._get_id_by_name() is None:
            # File already not exist?
            return True

        result = self.session.delete(f"{config.API_FILES}{self.file_id}")
        if result.status_code != 200:
            text = f"Fail to remove file: {self.page_name} {self.filename} {self.file_id}"
            raise Exception(text)
        return True

    def rename(self, name: str):
        result = self.session.put(f"{config.API_ARTICLES}/{self.file_id}", data={"name": name})
        if result.status_code == 200:
            self.filename = name
            return True
        return False

    def check(self):
        """Check file exist on server"""
        status_code = self.session.head(f"{config.FILES_URL}{self.page_name}/{self.filename}").status_code
        # if file already exist
        if status_code == 200:
            return True
        return False

    def check_hash(self):
        # TODO check checksum file on server and local
        pass

    @property
    def file_hash(self) -> str:
        if not self._file_hash:
            _ = self.file_bytes
        return self._file_hash

    @property
    def file_bytes(self) -> bytes:
        if self._file_bytes is bytes:
            return self._file_bytes

        self._file_bytes = self.session.get(self.file_url).content
        hash_obj = xxhash.xxh64()
        hash_obj.update(self._file_bytes)
        self._file_hash = hash_obj.hexdigest()

        return self._file_bytes

    @file_bytes.setter
    def file_bytes(self, new_file_bytes: bytes):
        self._file_bytes = new_file_bytes


class OutsideFIle:
    def __init__(self, file_url: str, session=normal_session, proxy_session=proxy_session):
        self.file_url = file_url

        self.filename: str = None
        self.file_bytes: bytes = None
        self.file_hash: str = None
        self.mime_type: str = None

        self.session = normal_session
        self.proxy_session = proxy_session

    def check_url(self, session):
        status_code = session.head(self.file_url).status_code
        # if file already exist
        if status_code == 200:
            return True
        return False

    def download(self):
        pass

    def _direct_download(self):
        if not self.check_url(self.session):
            return None

        pass

    def _proxy_download(self):
        if not self.check_url(self.proxy_session):
            return None

    def _webarchive_download(self):
        pass
