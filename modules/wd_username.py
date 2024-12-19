import config
from utls.base_utils import Article

import re

from utls.base_utils import Article
from utls.regex_parser import s_bracket_dual_regex, get_module_css
from config import logger

if not config.WD_USERS:
    raise Exception("Not set wd users file list")


def handle(article: Article) -> Article:
    patched_source_page: str = article.source_code
    user_blocks: list[str] = re.findall(r"\[\[\s*\*?user\s+wd:[^\]]+\s*\]\]", article.source_code)

    for user_block_ex in user_blocks:
        user_block_wd_name = user_block_ex.split(":")[1].replace("]]", "").strip()
        patched_source_page = patched_source_page.replace(user_block_ex, f"wd:{user_block_wd_name.strip()}")

    for wd_user in config.WD_USERS:
        wd_user = wd_user.strip()
        user_block = f"[[user {wd_user}]]"

        wd_user_with_space = wd_user.replace("-", " ")
        # rint(wd_user, user_block)
        patched_source_page = patched_source_page.replace(wd_user_with_space, wd_user)
        patched_source_page = patched_source_page.replace(wd_user, user_block)

    article.source_code = patched_source_page

    return article
