"""
Download image content to local--files of page
"""

import mimetypes
import re

from utls.base_utils import Article, ArticleFile, OutsideFile
from utls.regex_parser import s_bracket_dual_regex, code_block_import_regex, get_module_css, css_url_regex
from config import logger
from urllib.parse import unquote, urlparse, quote_plus


def handle(article: Article) -> Article:
    patched_source_page = article.source_code

    modules_css = get_module_css(article.source_code)
    if not modules_css:
        logger.warning(f"Article {article.page_name} not has any css module")
        return article
    elif len(modules_css) > 1:
        logger.error(f"To many module CSS please use `css_module_multiple` before this patch")
        logger.warning(f"Skip current patch for {article.page_name}")
        return article

    module_css = modules_css[0]
    patched_module_css = module_css

    list_all_local_files_import = [link for link in re.findall(css_url_regex, module_css) if "local--files" not in link]

    for link_str in list_all_local_files_import:
        file_obj = OutsideFile(link_str)
        file_obj.download(force_type="image")
        if not file_obj.file_hash:
            continue

        if "image" in file_obj.mime_type:
            filename = f"{article.page_name}-{file_obj.file_hash}{mimetypes.guess_extension(file_obj.mime_type)}"
            file_to_upload = ArticleFile(article.page_name,
                                         filename, file_bytes=file_obj.file_bytes, mime_type=file_obj.mime_type)
            article.add_file(file_to_upload)
            patched_module_css = patched_module_css.replace(link_str, quote_plus(file_to_upload.relative_file_url))

    patched_source_page = patched_source_page.replace(module_css, patched_module_css)
    article.source_code = patched_source_page

    return article
