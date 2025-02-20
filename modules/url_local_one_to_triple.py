import time
import uuid
import re
from math import atan2
from urllib.parse import urlparse

from config import site, BASE_URL
from typing import List

from utls.base_utils import Article, OutsideFile, ArticleFile
from utls.regex_parser import s_bracket_dual_regex, s_bracket_triple_regex, s_bracket_one_regex
from url_replace import link_tuple_handle


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    solo_brackets_items = re.findall(s_bracket_one_regex, article.source_code)
    for solo_item in solo_brackets_items:
        print(solo_item)

    return article
