"""
Fix component theme CSS codeblock use
"""
import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex, code_block_import_regex
from config import logger


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    blocks_list = re.findall(s_bracket_dual_regex, article.source_code)
    split_listed = [block.split() for block in blocks_list]
    only_code = [block for block in split_listed if "code" in block[0]]
    only_module = [block for block in split_listed if "module" in block[0]]

    code_block_import_css = re.findall(code_block_import_regex, article.source_code)
    if len(code_block_import_css) > 0:
        if len(code_block_import_css) > 1:
            logger.error("TO MANY")
        print(article.page_name, code_block_import_css)

    return article
