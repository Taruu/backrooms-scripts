# long links first
# if ling link has base link form another we dont broke any think on short link

"""
This replace
@import url("http://backrooms-wiki.wdfiles.com/local--files/component%3Atheme/normalize-archived.css");
@import url("http://backrooms-wiki.wdfiles.com/local--files/component%3Atheme/bhl-archived.css");
@import url("http://backrooms-wiki.wikidot.com/local--files/component:theme/sidebar.css");


@import url("http://backrooms-wiki.wdfiles.com/local--files/component%3Atheme/normalize-archived.css");
@import url("http://backrooms-wiki.wdfiles.com/local--files/component%3Atheme/bhl-archived.css");
@import url("http://backrooms-wiki.wikidot.com/local--files/component:theme/sidebar.css");


To this:

@import url('/local--files/system:fonts/css2_family=Old+Standard+TT&display=swap.css');
@import url('/local--files/system:fonts/css2_family=Lora&display=swap.css');
@import url('/local--files/system:fonts/css2_family=Forum&display=swap.css');
@import url('/local--files/system:fonts/css2_family=Caveat&display=swap.css');

@import url("/local--files/component:theme/normalize-archived.css");
@import url("/local--files/component:theme/bhl-archived.css");
@import url("/local--files/component:theme/sidebar.css");

"""

import mimetypes
import re

import config
from utls.base_utils import Article, ArticleFile, OutsideFile
from utls.regex_parser import s_bracket_dual_regex, code_block_import_regex, get_module_css, css_url_regex
from config import logger
from urllib.parse import unquote, urlparse, quote

font_content_regex = r"^\s*@font-face\s*\{[\s\S]*?\}\s*(\/\*[\s\S]*?\*\/)?\s*$|^\s*$|\/\*[\s\S]*?\*\/\n"

font_page_css_a = Article(config.site.get("host.css_fonts_url"))
font_page_data_a = Article(config.site.get("host.woff2_fonts_url"))

font_page_css_values = [article_file.filename for article_file in font_page_css_a.file_list().values()]
font_page_data_values = [article_file.filename for article_file in font_page_data_a.file_list().values()]

logger.info("Load fonts list")


def is_css_font_file(source: str):
    """check source is there only @font-face and comments"""
    to_check = source
    matches = re.finditer(font_content_regex, source, re.MULTILINE)

    for block in list(matches):
        to_check = to_check.replace(block.string, "")

    to_check = to_check.strip()

    if to_check:
        return False
    return True


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

    list_all_url = [link for link in re.findall(css_url_regex, module_css) if
                    "local--files" not in link]

    for link_str in list_all_url:

        file_obj = OutsideFile(link_str)
        file_obj.download()

        if not file_obj.file_bytes or not file_obj.mime_type:
            continue

        if "text" not in file_obj.mime_type:
            continue
        print("is css font file check", file_obj.file_url)
        if not is_css_font_file(file_obj.file_bytes.decode()):
            logger.warning(f"File on url {link_str} is not font-css only")
            continue

        css_file = file_obj
        font_css = css_file.file_bytes.decode()

        list_all_font_url = [OutsideFile(link) for link in re.findall(css_url_regex, font_css)]

        link_obj = urlparse(link_str)

        css_filename = f"{str(link_obj.path)[1:]}?{link_obj.query}.css".replace('?', '_')

        for font_file_remote in list_all_font_url:

            font_file_remote.download()
            font_file_local = ArticleFile(font_page_data_a.page_name,
                                          f"{css_filename.replace('.css', '')}_{font_file_remote.file_hash}",
                                          file_bytes=font_file_remote.file_bytes)
            if font_file_local.filename not in font_page_data_values:
                font_page_data_a.add_file(font_file_local)
                font_page_data_values.append(font_file_local.filename)

            font_css = font_css.replace(font_file_remote.file_url, font_file_local.relative_file_url)

        css_file_local = ArticleFile(font_page_css_a.page_name, css_filename, file_bytes=font_css.encode(),
                                     mime_type="text/css")
        if css_file_local.filename not in font_page_css_values:
            font_page_data_a.add_file(css_file_local)
            font_page_css_values.append(css_file_local.filename)

        patched_module_css = patched_module_css.replace(link_str, css_file_local.relative_file_url)

    patched_source_page = patched_source_page.replace(module_css, patched_module_css)
    # article.source_code = patched_source_page
    return article
