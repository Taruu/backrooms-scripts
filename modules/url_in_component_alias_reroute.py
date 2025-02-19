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

    for item in brackets_items:
        print(item)