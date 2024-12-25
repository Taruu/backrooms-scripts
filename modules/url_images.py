"""
Fix url links
"""
import re
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

    for item in brackets_items:  # Bruh
        if not any([component in item for component in site.get("images.components")]):
            continue

        image_url = re.search(r"(?P<url>https?://[^\s]+)", item).group("url")

        if "|" in image_url:
            url_and_text = image_url.split(sep="|", maxsplit=1)
        else:
            url_and_text = image_url.split(maxsplit=1)

        image_url = url_and_text[0]
        image_url = image_url.strip("[]")
        image_url_obj = urlparse(image_url)

        file_obj = OutsideFile(image_url)
        file_obj.download()

        if "image" not in file_obj.mime_type:
            logger.error(f"Image on page {article.page_name}, by url {image_url} not image? Abort image")
            continue

        if not file_obj.file_bytes:
            logger.error(f"Image {image_url} in block {item} on page {article.page_name} not exist")
            continue

        if "local--files" in image_url:
            temp_split = image_url_obj.path.split('/')
            page_name_of_file = temp_split[1]
            filename_to_check = temp_split[-1]
            article_check = Article(page_name_of_file)



    return article
