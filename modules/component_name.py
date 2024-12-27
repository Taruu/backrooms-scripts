"""
Fix component name

:backrooms-wiki-cn:component:interwiki-style -> :component:interwiki-style

"""
import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    blocks_list = re.findall(s_bracket_dual_regex, article.source_code)
    split_listed = [block.split() for block in blocks_list]
    only_components = [block for block in split_listed if "include" in block[0]]
    only_components = [block for block in only_components if len(block) > 1]
    only_to_patch = [block for block in only_components if block[1].count(':') > 2]

    for split_block in only_to_patch:
        old_component_name = split_block[1]
        component_name = old_component_name.split(":")
        component_name.pop(1)
        new_component_name = ":".join(component_name)
        patched_source_page = patched_source_page.replace(old_component_name, new_component_name[1:])

    article.source_code = patched_source_page

    return article
