import re

from modules.component_name_fix import handle
from utls.base_utils import Article
from utls.regex_parser import *

page = Article("theme:amor-incrementum")

handle(page.source_code())

# brackets_items = re.findall(s_bracket_dual_regex, page.source_code())
# print(brackets_items)
