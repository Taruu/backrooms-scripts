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
FILES_URL = BASE_URL + site.get("host.files_url")
API_ARTICLES = BASE_URL + site.get("host.api_articles")
API_FILES = BASE_URL + site.get("host.api_files")

if site.get("users.wd_file"):
    with open(site.get("users.wd_file", 'r')) as file:
        WD_USERS: list = list(dict.fromkeys([line for line in file.readlines()]))
else:
    WD_USERS: list = None

PROXY = {
    "http": values.get("proxy.http"),
    "https": values.get("proxy.https"),
}


# Remove the existing logger
logger.remove()
# Add a new logger with the given settings
logger.add(
    sys.stdout,
    colorize=values.get("logging.colorize"),
    level=values.get("logging.level"),
    format=values.get("logging.format"),
)
# Add logging to file
logger.add(
    values.get("logging.file_path"),
    level=values.get("logging.level"),
    format=values.get("logging.format"),
    rotation=values.get("logging.rotation"),
    enqueue=values.get("logging.enqueue"),
)
logger.level("INFO", color="<blue>")

logger.info("Config load successful!")
