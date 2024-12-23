"""
Fix url links
"""
import re
from typing import List

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex, s_bracket_triple_regex


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    brackets_items = re.findall(s_bracket_dual_regex, article.source_code)
    brackets_items.extend(re.findall(s_bracket_triple_regex, article.source_code))

    brackets_items: List[str] = [item for item in brackets_items if ("http" in item) and ("component" not in item)]

    return article
