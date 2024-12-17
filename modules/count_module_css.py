from utls.base_utils import Article

import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex
from config import logger


def handle(article: Article) -> Article:
    dual_blocks_list = re.findall(s_bracket_dual_regex, article.source_code)
    dual_blocks_list = [block.lower() for block in dual_blocks_list]
    module_only_css = [block for block in dual_blocks_list if ("module" in block) and ("css" in block)]
    if len(module_only_css) > 1:
        logger.error(f"TO MANY module css {len(module_only_css)} on page {article.page_name}")

    return article
