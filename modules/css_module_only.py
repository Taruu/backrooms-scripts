"""
Fix themes code

Save only component:interwiki-style and module CSS for theme

"""
from utls.base_utils import Article

import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex, get_module_css
from config import logger


def handle(article: Article) -> Article:
    dual_blocks_list = re.findall(s_bracket_dual_regex, article.source_code)
    dual_blocks_list = [block.lower() for block in dual_blocks_list]
    module_only_css = [block for block in dual_blocks_list if ("module" in block) and ("css" in block)]
    print(list(filter(lambda item: "component:interwiki-style" in item, dual_blocks_list)))
    if len(module_only_css) > 1:
        logger.error(f"TO MANY CSS BLOCKS {article.page_name}")
        return article
    list_css_modules = get_module_css(article.source_code)
    # article.source_code = list_css_modules[0]
    return article
