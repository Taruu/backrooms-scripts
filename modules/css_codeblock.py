"""
Fix component theme CSS codeblock use
"""
import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex, code_block_import_regex, get_code_blocks, PEARTextHighlighter
from config import logger


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    blocks_list = re.findall(s_bracket_dual_regex, article.source_code)
    split_listed = [block.split() for block in blocks_list]
    only_code = [block for block in split_listed if "code" in block[0]]
    only_module = [block for block in split_listed if "module" in block[0]]

    code_block_import_css = re.findall(code_block_import_regex, article.source_code)
    if not code_block_import_css:
        return article

    if len(code_block_import_css) > 0:
        if len(code_block_import_css) > 1:
            logger.error("To many code_block_import_css in module CSS skip page")
            return article

    codeblock_css = get_code_blocks(article.source_code, PEARTextHighlighter.CSS)
    if codeblock_css:
        codeblock_css = codeblock_css[0]
    else:
        return article

    blocks_to_remove = re.findall(s_bracket_dual_regex, codeblock_css)
    only_css = codeblock_css
    for block_to_remove in blocks_to_remove:
        only_css = only_css.replace(block_to_remove, "")

    patched_source_page = patched_source_page.replace(code_block_import_css[0], only_css)

    article.source_code = patched_source_page

    return article
