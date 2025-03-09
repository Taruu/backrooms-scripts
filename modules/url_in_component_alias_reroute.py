# alias-reroute

# https://www.backroomswiki.ru/api/articles/new

# {"pageId":"alias-reroute:obicnie-urovni","title":"Obicnie Urovni","source":"template","comment":""}
# https://www.backroomswiki.ru/alias-reroute:obicnie-urovni

# Cтраница перенаправление на
# [[[normal-levels|Обычные уровни]]]
# Пример использования:
# [[code]]
# [[[Обычные уровни]]]
# [[/code]]
# [[module Redirect destination="normal-levels"]]
import re
import time
import uuid
from math import atan2
from urllib.parse import urlparse
from venv import logger

from config import site, BASE_URL
from typing import List

from utls.base_utils import Article, OutsideFile, ArticleFile
from utls.regex_parser import s_bracket_dual_regex, s_bracket_triple_regex, s_bracket_one_regex
from url_replace import link_tuple_handle


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    solo_brackets_items = re.findall(s_bracket_one_regex, patched_source_page)
    triple_brackets_items = re.findall(s_bracket_triple_regex, article.source_code)

    images_blocks_list = []
    images_cache = {}

    images_links = []

    triple_brackets_links = {}

    for triple_item in triple_brackets_items:
        uuid_template = uuid.uuid4().__str__()
        triple_brackets_links.update({uuid_template: {"meta": link_tuple_handle(triple_item), "original": triple_item}})
        patched_source_page = patched_source_page.replace(triple_item, uuid_template)

    for solo_item in solo_brackets_items:
        pass

    dual_brackets_items = re.findall(s_bracket_dual_regex, patched_source_page)

    for dual_item in dual_brackets_items:
        link_in_dual = False
        for uuid_link in triple_brackets_links.keys():
            if uuid_link in dual_item:
                link_in_dual = True
        if link_in_dual:
            logger.error(f"Has link in dual component")
            print(dual_item)

    return article
