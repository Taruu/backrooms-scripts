import csv
import mimetypes
import re
import time
from builtins import Exception
from hashlib import md5
from typing import List
from urllib.parse import urlparse
import wayback
import magic
import requests
from lxml import html
from lxml import etree
from io import StringIO, BytesIO
import xml.etree.ElementTree as ET

from lxml.html import HtmlElement

CSRF_TOKEN = ""
SESSION_ID = ""

BASE_URL = 'https://www.backroomswiki.ru/'
ORIGINAL_URL = "http://backrooms-wiki.wikidot.com"

DOMAINS_TO_PROXY = ["wikidot.com", "wdfiles.com"]

PROXY = {
    "http": 'socks5://',
    "https": 'socks5://',
}

# only old links format
# [https://www.backrooms-wiki.ru/level-0 Forward]
# [*https://www.backrooms-wiki.ru/level-0 New page]
solo_regex = r"(?<!\[)\[[^\[\]]*\](?!\[)"
# solo_regex = r"\[[^\[\]]*\]"

# component:level-class             https://backrooms-dev.dentrado.art/component:level-class
# component:image-block             https://backrooms-dev.dentrado.art/image-block
# component:forum-block             https://backrooms-dev.dentrado.art/forum-block
# component:image-block-spoiler     https://backrooms-dev.dentrado.art/image-block-spoiler
# component:photocard-block-base    http://ru-backrooms-wiki.wikidot.com/component:photocard-block
# component:hinc                    https://backrooms-dev.dentrado.art/component:hinc
# component:level-card              https://backrooms-dev.dentrado.art/component:level-card
dual_regex = r"\[\[(?:.|\n)*?\]\]"  #
image_component_list = ["component:level-class", "component:image-block", "component:forum-block",
                        "component:image-block-spoiler", "component:photocard-block-base", "component:hinc",
                        "component:level-card", "image ", "Image"]
# only new links
# [[[http://ru-backrooms-wiki.wikidot.com/level-0|desc]]]
# [[[*http://ru-backrooms-wiki.wikidot.com/level-0|desc]]]
thiple_regex = r"\[\[\[[^\[\]\n]*\]\]\]"

wayback_client = wayback.WaybackClient()


class Link:
    def __init__(self, original_string, url, text, new_page=False):
        self.original_string = original_string
        self.url = urlparse(url)
        self.text = text
        self.new_page = new_page

    def __repr__(self):
        return f"Link({str(self.__dict__)})"

    def replace_in_source(self, source_text: str):
        new_link_block = f"[[[{'*' * int(self.new_page)}{self.url.path[1:]}|{self.text}]]]"

        if "en.backrooms-wiki.ru" in str(self.url.hostname):
            new_link_block = f"[[[{'*' * int(self.new_page)}{ORIGINAL_URL}{self.url.path}|{self.text}]]]"

        new_source_text = source_text.replace(self.original_string, new_link_block)
        return new_source_text


class ImageLink:
    """{page_id}-{md5}.{filetype}"""

    def __init__(self, original_url, page_id="image"):
        self.original_url = urlparse(original_url)
        self.current_url = None
        self.page_id = page_id

        self.filename = None
        self.file_bytes = b""
        self.file_md5 = None
        self.file_mimetype = None
        self._download_image()

    def is_valid(self):
        return "image" in self.file_mimetype

    def __repr__(self):
        return f"ImageLink({str(self.__dict__)})"

    def __hash__(self):
        if not self.file_md5:
            return None
        return self.file_md5

    def _download_image(self, overwrite_url=None):

        download_url = self.original_url if not overwrite_url else overwrite_url

        print(f"download image\n{download_url.geturl()}\nfor {self.page_id}")
        proxy = PROXY if any([domain in download_url.hostname for domain in DOMAINS_TO_PROXY]) else None
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        proxy = None
        try:
            req_tmp = requests.get(download_url.geturl(), proxies=proxy, allow_redirects=True,
                                   headers=headers, timeout=10)
            print(req_tmp.status_code, proxy)
            self.file_bytes = req_tmp.content
        except Exception as error:
            print(error)
            self.file_bytes = b""

        self.file_mimetype = magic.from_buffer(self.file_bytes, mime=True)
        self.file_md5 = md5(self.file_bytes, usedforsecurity=False).hexdigest()[:9]
        self.filename = f"{self.page_id}-{self.file_md5}{mimetypes.guess_extension(self.file_mimetype)}"
        if self.is_valid():
            print(f"successful download image from:\n{download_url.geturl()}\nto {self.filename}")
            print()
        else:
            print(f"error download image from:\n{download_url.geturl()}\nto {self.filename}")

    def get_webarchive(self):
        print(f"get image form webarhive {self.original_url.geturl()}")
        for record in wayback_client.search(str(self.original_url.geturl())):
            print(f"try record: {record}")
            try:
                memento = wayback_client.get_memento(record)
            except Exception:
                continue
            for key, value in memento.links.items():
                if key == "original":
                    continue
                time.sleep(5)
                archive_url = value.get('url')
                print(key, archive_url)

                url_obj = urlparse(archive_url)
                self._download_image(overwrite_url=url_obj)

                if self.is_valid():
                    print(f"successful download image form webarchive {self.original_url.geturl()}")
                    return

        if not self.is_valid():
            with open("failed_url.csv", "a") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(["image", self.page_id, self.original_url.geturl()])

    def upload_image(self):
        if not self.is_valid():
            return False

        status_code = requests.head(f"{BASE_URL}/local--files/{self.page_id}/{self.filename}").status_code
        # if file already exist
        if status_code == 200:
            return True

        cookies = {'csrftoken': BASE_URL, 'sessionid': SESSION_ID}
        headers = {
            "X-File-Name": self.filename,
            "Content-Type": self.file_mimetype,
            "Content-Length": str(len(self.file_bytes))
        }
        print(f"upload image {self.filename} to {self.page_id}")

        result = requests.post(f"{BASE_URL}/api/articles/{self.page_id}/files", data=self.file_bytes,
                               cookies=cookies, headers=headers)

        if result.status_code not in [200, 409]:
            print(self.original_url.geturl())
            print(f"Error to upload {self.filename}")
            print(result.status_code, result.text)
        else:
            print(f"successful upload {self.filename} image")
            print()
            return True

    def replace_in_source(self, source_text: str):
        new_source_text = source_text.replace(str(self.original_url.geturl()),
                                              f"/local--files/{self.page_id}/{self.filename}")
        return new_source_text


def get_article(lever_url: str) -> dict:
    """Like https://backrooms-dev.dentrado.art/level-0 link"""
    url_path = urlparse(lever_url)
    return requests.get(f'https://{url_path.hostname}/api/articles/{url_path.path}').json()


def get_links(source: dict) -> List[Link]:
    """Get links obj"""
    # TODO remove hadcode of backrooms
    list_links = []

    brackets_items = re.findall(thiple_regex, source.get("source"))
    brackets_items.extend(re.findall(solo_regex, source.get("source")))

    brackets_items: List[str] = [item for item in brackets_items if
                                 "http" in item and "component" not in item]

    for brackets_link in brackets_items:
        solo_link: str = brackets_link.strip("[]")

        if "|" in solo_link:
            url_and_text = solo_link.split(sep="|", maxsplit=1)
        else:
            url_and_text = solo_link.split(maxsplit=1)

        if len(url_and_text) == 2:
            url, text = url_and_text[0], url_and_text[1]
        else:
            url = url_and_text[0]
        # check backrooms or not
        print(url)
        if "backrooms" not in url:
            continue
        # Open on new page
        if url[0] == "*":
            list_links.append(Link(brackets_link, url[1:], text, new_page=True))
        else:
            list_links.append(Link(brackets_link, url, text))
    # print(list_links)
    list_links = list(filter(lambda link_obj: "ru-backrooms-wiki.wikidot.com" in link_obj.url.hostname \
                                              or "backrooms-wiki.ru" in link_obj.url.hostname \
                                              or "backroomswiki.ru" in link_obj.url.hostname \
                                              and "include" not in link_obj.url.hostname, list_links))
    print(list_links)

    return list_links


def get_images(source: dict) -> List[ImageLink]:
    list_links = []

    brackets_items = re.findall(dual_regex, source.get("source"))
    brackets_items: List[str] = [item for item in brackets_items if
                                 "http" in item]
    for item in brackets_items:
        image_url = re.search(r"(?P<url>https?://[^\s]+)", item).group("url")
        if not any([component in item for component in image_component_list]):
            continue

        if "|" in image_url:
            url_and_text = image_url.split(sep="|", maxsplit=1)
        else:
            url_and_text = image_url.split(maxsplit=1)
        image_url = url_and_text[0]
        # if image_url[-1] == "|":
        #     image_url = image_url[:-1]
        image_url = image_url.strip("[]")
        list_links.append(ImageLink(image_url, source.get("pageId")))

    return list_links


def get_files(page_id: str):
    result = requests.get(f"{BASE_URL}/api/articles/{page_id}/files")
    return [item.get('name') for item in result.json().get("files")]


def post_new_source(title: str, page_id: str, new_source_text, comment: str):
    print(f"upload fix page {title} ({page_id})")
    cookies = {'csrftoken': BASE_URL, 'sessionid': SESSION_ID}
    dict_new_source = {
        "title": title,
        "pageId": page_id,
        "comment": comment,
        "source": new_source_text
    }

    result = requests.put(f"{BASE_URL}/api/articles/{page_id}", json=dict_new_source,
                          cookies=cookies)
    result_json = result.json()
    return result_json.get("status") == "ok"


def fix_article(level_url: str):
    if BASE_URL not in level_url:
        return
    dict_source = get_article(level_url)
    if not dict_source.get('pageId'):
        return False
    page_links = get_links(dict_source)
    image_links = get_images(dict_source)
    new_source = dict_source.get('source')

    fix_links_count = 0
    for page_link in page_links:
        fix_links_count += 1
        new_source = page_link.replace_in_source(new_source)

    fix_images_count = 0
    for image_link in image_links:
        if not image_link.is_valid():
            image_link.get_webarchive()

        status = image_link.upload_image()
        if status:
            fix_images_count += 1
            new_source = image_link.replace_in_source(new_source)

    comment = f"""
    Автоматическое исправление.
    Изменено:
    {fix_links_count}-link
    {fix_images_count}-images
    """
    print()
    post_new_source(dict_source.get('title'), dict_source.get("pageId"), new_source, comment)


# https://backrooms-dev.dentrado.art/level-114
# https://backrooms-dev.dentrado.art/level-123
# https://backrooms-dev.dentrado.art/test-mx-4
# https://backrooms-dev.dentrado.art/the-platform
# https://backrooms-dev.dentrado.art/level-193


#
list_url = """
https://www.backroomswiki.ru/level-699
"""

for url in list_url.split("\n"):
    fix_article(url)
    time.sleep(1)
