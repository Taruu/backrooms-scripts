import logging
import sys
from inspect import currentframe

from dynaconf import Dynaconf
from loguru import logger

values = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
)

site = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[f"{values.get('base.current_site')}.toml"]
)

# Current wiki Base url
BASE_URL = site.get("host.BASE_URL")
LOGIN_URL = BASE_URL + site.get("host.login_url")

API_ARTICLES = BASE_URL + site.get("host.api_articles")
