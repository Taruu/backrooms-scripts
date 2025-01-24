from utls.base_utils import Article

import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex, get_module_css
from config import logger


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    dual_blocks_list = re.findall(s_bracket_dual_regex, article.source_code)
    dual_blocks_list = [block.lower() for block in dual_blocks_list]
    module_only_css = [block for block in dual_blocks_list if ("module" in block) and ("css" in block)]
    if len(module_only_css) <= 1:
        return article

    logger.error(f"TO MANY module css {len(module_only_css)} on page {article.page_name}")
    list_css_modules = get_module_css(article.source_code)
    print(list_css_modules)

    if len(list_css_modules) <= 1:
        return article

    list_css_modules.sort(key=lambda text: len(text))

    list_css_modules_replace = list_css_modules.copy()
    main_module_css_to_replace = list_css_modules_replace.pop(-1)
    for module_css_to_remove in list_css_modules_replace:
        patched_source_page = patched_source_page.replace(module_css_to_remove, "")

    # Clear css modules form start and end
    list_css_modules_clean = []

    for css_module in list_css_modules:
        dual_blocks_list = re.findall(s_bracket_dual_regex, css_module)
        result_temp = css_module
        for block in dual_blocks_list:
            result_temp = result_temp.replace(block, "")
        list_css_modules_clean.append(result_temp)

    result_css = "\n".join(list_css_modules_clean)
    result_css = f"[[module css]]\n{result_css}\n[[/module]]"
    patched_source_page = patched_source_page.replace(main_module_css_to_replace, result_css)
    article.source_code = patched_source_page
    return article
