"""
Fix page url CSS local--files ONLY!!!

Example:
    @import url("http://backrooms-wiki.wdfiles.com/local--files/component%3Atheme/normalize-archived.css");
    @import url("http://backrooms-wiki.wdfiles.com/local--files/component%3Atheme/bhl-archived.css");
    @import url("http://backrooms-wiki.wikidot.com/local--files/component:theme/sidebar.css");
    url("'http://backrooms-sandbox-2.wikidot.com/local--files/captaiin-part-4-diamond-is-unbreakable/amor incrementum");

Result:
    url("/local--files/component:theme/normalize-archived.css");
    url("/local--files/component:theme/bhl-archived.css");
    url("/local--files/component:theme/sidebar.css");
    url("/local--files/pagename/amor incrementum");

"""
import re

from utls.base_utils import Article, ArticleFile, OutsideFile
from utls.regex_parser import s_bracket_dual_regex, code_block_import_regex, get_module_css, css_url_regex
from config import logger
from urllib.parse import unquote, urlparse


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

    list_all_local_files_import = [link for link in re.findall(css_url_regex, module_css) if
                                   "local--files" in link]
    articles_cache = {}

    for link_str in list_all_local_files_import:
        link_obj = urlparse(link_str)
        temp_split = str(link_obj.path).split("/")
        page_name = unquote(temp_split[2])
        filename = unquote(temp_split[-1])

        # get article from cache
        article_target = articles_cache.get(page_name)
        if not article_target:
            try:
                article_target = Article(page_name)
            except Exception:
                pass
            # put into cache
            articles_cache.update({page_name: article_target})

        if not article_target:
            # if this page not exist
            file_obj = OutsideFile(file_url=link_str)
            file_obj.download()

            if not file_obj.file_bytes:
                continue

            article_file = ArticleFile(article.page_name, filename, file_bytes=file_obj.file_bytes,
                                       mime_type=file_obj.mime_type)
            article.add_file(article_file, overwrite=True)
            patched_source_page = patched_source_page.replace(link_str, article_file.relative_file_url)
            continue

        exist_article_file = None
        for article_file in article_target.files_list.values():
            if filename == article_file.filename:
                # if we found local file
                exist_article_file = article_file
                break

        if not exist_article_file:
            # if file not exist load local
            file_obj = OutsideFile(file_url=link_str)
            file_obj.download()
            exist_article_file = ArticleFile(article.page_name, filename, file_bytes=file_obj.file_bytes,
                                             mime_type=file_obj.mime_type)

            article.add_file(exist_article_file, overwrite=True)
        patched_source_page = patched_source_page.replace(link_str, exist_article_file.relative_file_url)
    article.source_code = patched_source_page
    return article
