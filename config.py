import logging
import sys
from inspect import currentframe

from dynaconf import Dynaconf
from loguru import logger

values = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
)

# Current wiki Base url
BASE_URL = values.get("hosts.BASE_URL")
# use checks in hostname
REPLACE_HOSTS_PATTERN_LIST = values("hosts.replace_hosts_pattern_list")

