"""
Fix component theme CSS codeblock use
"""
import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex

false_import_regex = r"@import\s+url\(\s*[\'\"]?[^\'\")]*local--code[^\'\")]*[\'\"]?\s*\);"


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    blocks_list = re.findall(s_bracket_dual_regex, article.source_code)
    split_listed = [block.split() for block in blocks_list]
    only_code = [block for block in split_listed if "code" in block[0]]
    only_module = [block for block in split_listed if "module" in block[0]]

    print(only_code, only_module)

    return article
