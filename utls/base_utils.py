import json
import logging
import mimetypes
import time
from asyncio import timeout
from urllib.parse import urlparse, unquote
import xxhash

import os
import magic
import requests
from lxml import html

import config
from config import logger

import wayback

wayback_client = wayback.WaybackClient()


def login_auth(username: str, password):
    """Write session into file"""
    session = requests.Session()

    headers = {
        "User-Agent": config.values.get('requests.user_agent'),
        "Referer": config.LOGIN_URL,
        "Accept - Language": "ru - RU, ru; q = 0.8, en - US; q = 0.5, en;q = 0.3"
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


def token_auth(bot_token: str):
    # self._session.headers.add("Authorization", f"Bearer {self.token}")
    with open(config.values.get("requests.session_file"), "w") as file_session:
        file_session.write(json.dumps({"Authorization": f"Bearer {bot_token}"}))


# Normal Session
normal_session = requests.Session()
normal_session.headers.update({"User-Agent": config.values.get("requests.user_agent")})

# Session with proxy
proxy_session = requests.Session()

proxy_session.proxies.update(config.PROXY)
proxy_session.headers.update({"User-Agent": config.values.get("requests.user_agent")})

# Session with auth for target site
authorized_session = requests.Session()

if os.path.exists(config.values.get("requests.session_file")):
    with open(config.values.get("requests.session_file"), "r") as file_session:
        session_values = json.loads(file_session.read())

        if session_values.get("csrftoken"):
            authorized_session.cookies.update(session_values)
            authorized_session.headers.update(
                {"User-Agent": config.values.get('requests.user_agent')}
            )
        else:
            authorized_session.headers.update(session_values)
else:
    logger.error(f"session file not exist")


class ArticleFile:
    def __init__(self, page_name: str, filename: str,
                 file_id=0, file_bytes=None, mime_type=None,
                 session=authorized_session):
        """
        file_bytes = None : if we create new image for page we forse setup bytes
        """
        self.session = session

        self.is_file_new = False

        self.file_id: int = int(file_id)
        self.page_name: str = page_name
        if "/" in page_name:
            raise Exception("page_name cant has '/' symbol")

        self.filename: str = filename

        self._file_bytes: bytes = file_bytes

        self.mime_type: str = mime_type

        self._file_hash: str = None

        if file_bytes:
            self.is_file_new = True
            if not mime_type:
                self.mime_type: str = magic.from_buffer(file_bytes, mime=True)

            hash_obj = xxhash.xxh64()
            hash_obj.update(file_bytes)
            self._file_hash = hash_obj.hexdigest()

    def __hash__(self):
        return self.file_id

    def get_id_by_name(self):
        if self.file_id:
            return self.file_id

        file_json = requests.get(f"{config.API_ARTICLES}{self.page_name}/files").json()
        for file_info in file_json.get("files"):
            if self.filename == file_info.get("name"):
                self.file_id = file_info.get("id")
                return self.file_id
        self.file_id = None
        return None

    @property
    def absolute_file_url(self):
        return f"{config.FILES_URL}{self.page_name}/{self.filename}"

    @property
    def relative_file_url(self):
        return f"{urlparse(config.FILES_URL).path}{self.page_name}/{self.filename}"

    def upload(self, overwrite=False, check=False):
        """
        overwrite = False : status about overwrite file
        """
        if overwrite and self.is_file_new:
            self.remove()

        headers = {
            "X-File-Name": self.filename,
            "Content-Type": self.mime_type,
            "Content-Length": str(len(self._file_bytes))
        }

        result = self.session.post(f"{config.API_ARTICLES}{self.page_name}/files", data=self._file_bytes,
                                   headers=headers)

        if result.status_code not in [200, 409]:
            text = f"Fail to upload image: {self.page_name}/{self.filename}"
            config.logger.error(text)
            raise Exception(text)
        else:
            self.is_file_new = False
            self.file_id = None
            self.get_id_by_name()
            return True

    def remove(self):
        """Remove file"""
        if self.get_id_by_name() is None:
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
        if not self._file_bytes:
            return self._file_bytes
        result = self.session.get(self.absolute_file_url)

        if result.status_code == 429:
            logger.warning(f"To fast file requests! Calm down on file {self.filename} {self.page_name}")
            time.sleep(5)
            return self.file_bytes

        self._file_bytes = result.content
        hash_obj = xxhash.xxh64()
        hash_obj.update(self._file_bytes)
        self._file_hash = hash_obj.hexdigest()

        return self._file_bytes

    @file_bytes.setter
    def file_bytes(self, new_file_bytes: bytes):
        self._file_bytes = new_file_bytes


class Article:
    def __init__(self, page_name: str, session=authorized_session):
        self.session = session
        self.page_name = page_name

        self._file_list = {}
        self._page_source = self.session.get(f'{config.API_ARTICLES}{self.page_name}').json()

        if self._page_source.get("error"):
            raise Exception(self._page_source.get("error"))

        self._get_file_list()

    @property
    def source_code(self) -> str:
        return self._page_source.get("source")

    @source_code.setter
    def source_code(self, new_source_code):
        self._page_source['source'] = new_source_code

    def update_source_code(self, comment: str):
        dict_new_source = {
            "title": self._page_source.get("title"),
            "pageId": self._page_source.get("pageId"),
            "comment": comment,
            "source": self._page_source.get("source")
        }

        result = self.session.put(f"{config.API_ARTICLES}{self.page_name}", json=dict_new_source)
        result_json = result.json()
        return result_json.get("pageId") == self.page_name

    def _get_file_list(self):
        file_json = requests.get(f"{config.API_ARTICLES}{self.page_name}/files").json()
        for file_info in file_json.get("files"):
            article_file = ArticleFile(self.page_name, file_info.get("name"),
                                       mime_type=file_info.get("mimeType"), file_id=file_info.get("id"))
            self._file_list.update({int(file_info.get("id")): article_file})

    def file_list(self) -> dict[int: ArticleFile]:
        if not self._file_list:
            self._get_file_list()
        return self._file_list

    def remove_file(self, article_file: ArticleFile):
        self._file_list.pop(article_file.file_id)
        article_file.remove()

    def add_file(self, article_file: ArticleFile, overwrite=False):
        article_file.upload(overwrite=overwrite)
        self._file_list.update({article_file.file_id: article_file})

    @property
    def files_list(self):
        return self._file_list


class OutsideFile:
    def __init__(self, file_url: str, session=normal_session, proxy_session=proxy_session):
        self.file_url = file_url

        self.filename: str = None
        self.file_bytes: bytes = None
        self.file_hash: str = None
        self.mime_type: str = None

        self.session = session
        self.proxy_session = proxy_session

    def guess_type(self):
        if self.mime_type:
            return mimetypes.guess_extension(self.mime_type)

    def _check_url(self, session, url=None):
        if not url:
            url = self.file_url
        result = requests.get(url, stream=True, verify=True)
        if 200 <= result.status_code < 400:
            return True
        return False

    def download(self, force_type: str = None):
        content = None
        print(self.file_url)
        for downloader in [self._direct_download, self._proxy_download, self._webarchive_download]:
            time.sleep(0.1)
            if not content:
                try:
                    content = downloader()
                except Exception:
                    content = None

            if content:
                self.mime_type: str = magic.from_buffer(content, mime=True)
                if not (str(force_type) in str(self.mime_type)) and force_type and self.mime_type:
                    content = None

                if content:
                    break

        if not content:
            logger.error(f"Cant download image {self.file_url} force_type = {force_type}")
            return None

        self.file_bytes = content

        hash_obj = xxhash.xxh64()
        hash_obj.update(self.file_bytes)

        self.file_hash = hash_obj.hexdigest()

    def _direct_download(self, url=None) -> [None | bytes]:
        if not self._check_url(self.session, url=url):
            return None

        try:
            if url:
                result = self.session.get(url, timeout=3, allow_redirects=True)
            else:
                result = self.session.get(self.file_url, timeout=3, allow_redirects=True)
        except Exception:
            return None

        self.headers = result.headers
        return result.content

    def _proxy_download(self) -> [None | bytes]:
        if not self._check_url(self.proxy_session):
            return None

        result = self.proxy_session.get(self.file_url, timeout=3, allow_redirects=True)
        self.headers = result.headers

        return result.content

    def check_download(self):
        pass

    def _webarchive_download(self, force_type=None):
        # https://i.postimg.cc/TP3FFVTz/classpsi.png

        time.sleep(5)  # To many request webarchive not liked

        for record in wayback_client.search(str(self.file_url)):
            time.sleep(2)  # To fast download webarchive not liked
            result = self.session.get(record.raw_url, timeout=3)
            self.headers = result.headers
            if not result.content:
                continue
            mime_type: str = magic.from_buffer(result.content, mime=True)
            if force_type and (force_type in mime_type):
                return result.content
            elif not force_type and result.content:
                return result.content

        return None


if __name__ == "__main__":
    test = OutsideFile("http://backrooms-wiki.wikidot.com/local--files/component:theme/sidebar.css")

    print(test.download())
    print(test.mime_type)
