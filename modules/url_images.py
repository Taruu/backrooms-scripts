"""
Fix url links
"""
import re
import time
from math import atan2
from urllib.parse import urlparse
from venv import logger

from config import site, BASE_URL
from typing import List

from utls.base_utils import Article, OutsideFile, ArticleFile
from utls.regex_parser import s_bracket_dual_regex, s_bracket_triple_regex, s_bracket_one_regex


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    brackets_items = re.findall(s_bracket_dual_regex, article.source_code)

    images_blocks_list = []
    images_cache = {}

    images_links = []

    for item in brackets_items:  # Bruh
        if not any([component in item for component in site.get("images.components")]):
            continue

        image_url = re.search(r"(?P<url>https?://[^\s]+)", item)
        if not image_url:
            continue
        image_url = image_url.group("url")

        if "|" in image_url:
            url_and_text = image_url.split(sep="|", maxsplit=1)
        else:
            url_and_text = image_url.split(maxsplit=1)

        image_url = url_and_text[0]
        image_url = image_url.strip("[]")

        images_links.append(image_url)

    images_links = list(dict.fromkeys(images_links))

    for image_url in images_links:
        image_url_obj = urlparse(image_url)

        file_obj = OutsideFile(image_url_obj.geturl())
        file_obj.download(force_type="image")

        if file_obj.mime_type and ("image" not in file_obj.mime_type):
            logger.error(
                f"Image on page {article.page_name}, by url {image_url} not image? Abort image {file_obj.mime_type}")
            continue

        if not file_obj.file_bytes:
            logger.error(f"Image {image_url} in on page {article.page_name} not exist")
            continue

        new_url = None

        if "local--files" in image_url:
            temp_split = image_url_obj.path.split('/')
            page_name_of_file = temp_split[2]
            filename_to_check = temp_split[-1]

            try:
                article_check = Article(page_name_of_file)
            except Exception:
                article_check = None

            if article_check:
                for article_file_to_check in article_check.file_list().values():
                    if article_file_to_check.filename == filename_to_check:
                        new_url = article_file_to_check.relative_file_url
                    elif article_file_to_check.file_hash == file_obj.file_hash:
                        new_url = article_file_to_check.relative_file_url

        if not new_url:
            new_filename = f"{article.page_name}-{file_obj.file_hash}"
            if file_obj.guess_type():
                new_filename += f"{file_obj.guess_type()}"
            new_article_file_obj = ArticleFile(article.page_name, new_filename, file_bytes=file_obj.file_bytes,
                                               mime_type=file_obj.mime_type)
            article.add_file(new_article_file_obj, overwrite=False)
            new_url = new_article_file_obj.relative_file_url

        patched_source_page = patched_source_page.replace(image_url, new_url)
    article.source_code = patched_source_page
    return article
