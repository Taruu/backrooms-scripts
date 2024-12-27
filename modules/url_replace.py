"""
Fix url links
"""
import re
from urllib.parse import urlparse

from config import site, BASE_URL
from typing import List

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex, s_bracket_triple_regex, s_bracket_one_regex

replace_blacklist_in = site.get("replace.in")
base_url_obj = urlparse(BASE_URL)


def link_handle(source_link: str):
    link_text = source_link.strip('[]')

    if "|" in link_text:
        url_and_text = link_text.split(sep="|", maxsplit=1)
    else:
        url_and_text = link_text.split(maxsplit=1)

    if len(url_and_text) == 2:
        url, text = url_and_text[0], url_and_text[1]
    else:
        url = url_and_text[0]
        text = None

    if not any([inner_part in url for inner_part in replace_blacklist_in]):
        return None

    open_page = False

    if url[0] == "*":
        open_page = True
        url_obj = urlparse(url[1:])
    else:
        url_obj = urlparse(url)

    patch_link = None
    for key, value in site.get('patch').items():
        value_obj = urlparse(value)
        if (key in url_obj) and (value_obj == base_url_obj):
            patch_link = None
            break
        if url_obj.hostname == key:
            patch_link = value_obj
            break

    if patch_link:
        new_url = f"{patch_link.geturl()}{url_obj.path}"
    else:
        new_url = f"{url_obj.path}"
    if text:
        return f"[[[{'*' * int(open_page)}{new_url}|{text}]]]"
    return f"[[[{'*' * int(open_page)}{new_url}|{text}]]]"


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    brackets_items = re.findall(s_bracket_one_regex, article.source_code)
    brackets_items.extend(re.findall(s_bracket_triple_regex, article.source_code))

    brackets_items: List[str] = [item for item in brackets_items if
                                 ("http" in item) and ("component" not in item)]

    for source_link in brackets_items:
        new_link = link_handle(source_link)
        if not new_link:
            continue
        patched_source_page = patched_source_page.replace(source_link, new_link)

    article.source_code = patched_source_page
    return article
