import re

import config
from utls.base_utils import Article, ArticleFile, OutsideFile
from utls.regex_parser import s_bracket_dual_regex, code_block_import_regex, get_module_css, css_url_regex
from config import logger
from urllib.parse import unquote, urlparse, quote

font_content_regex = r"^\s*@font-face\s*\{[\s\S]*?\}\s*(\/\*[\s\S]*?\*\/)?\s*$|^\s*$|\/\*[\s\S]*?\*\/\n"
css_comments_regex = r"\/\*[^*]*\*+([^\/*][^*]*\*+)*\/"

font_page_css_a = Article(config.site.get("host.css_fonts_url"))
font_page_data_a = Article(config.site.get("host.woff2_fonts_url"))


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    modules_css = get_module_css(article.source_code)

    if not modules_css:
        logger.warning(f"Article {article.page_name} not has any css module")
    elif len(modules_css) > 1:
        logger.error(f"To many module CSS please use `css_module_multiple` before this patch")
        logger.warning(f"Skip current patch for {article.page_name}")
        return article
    else:
        module_css = modules_css[0]
        patched_source_page.replace(module_css, "")

    if ">" in patched_source_page:
        logger.error(f"Page {article.page_name} contain '>' = {patched_source_page.count('>')}")

    return article
