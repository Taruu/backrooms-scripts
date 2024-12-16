"""
Fix component url CSS @import url

Example:
    @import url("http://backrooms-wiki.wdfiles.com/local--files/component%3Atheme/normalize-archived.css");
    @import url("http://backrooms-wiki.wdfiles.com/local--files/component%3Atheme/bhl-archived.css");
    @import url("http://backrooms-wiki.wikidot.com/local--files/component:theme/sidebar.css");

Result:
@import url("/local--files/component:theme/normalize-archived.css");
@import url("/local--files/component:theme/bhl-archived.css");
@import url("/local--files/component:theme/sidebar.css");


"""
import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex, code_block_import_regex
from config import logger


def handle(article: Article) -> Article:

    pass
