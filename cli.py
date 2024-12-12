import argparse
import sys
from getpass import getpass
from urllib.parse import urlparse

import config
from utls.base_utils import login, Article
import importlib
from config import logger

sys.path.append("modules")


def login_cli(args):
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    logger.info(f"Logging in with username: {username}")
    login(username, password)


def command_cli(args):
    file = open(args.pages_lists_file, 'r')
    modules = [importlib.import_module(module_name) for module_name in args.patch_names]

    for link in file.readlines():
        url_obj = urlparse(link)
        if f"{url_obj.scheme}://{url_obj.netloc}" != config.BASE_URL:
            logger.error(f"This not current target site! {url_obj.geturl()} not in {config.BASE_URL}")
            continue
        page_name = url_obj.path[1:]
        logger.info(f"Load {page_name}")
        article_to_fix = Article(page_name)
        print(article_to_fix.source_code())


#


def main():
    parser = argparse.ArgumentParser(description="A CLI tool with subcommands.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available subcommands')

    # Login subcommand
    login_parser = subparsers.add_parser('login', help='Authenticate a user')
    login_parser.set_defaults(func=login_cli)

    # Command subcommand
    patch_parser = subparsers.add_parser('patch', help='Apply a patch')
    patch_parser.add_argument("pages_lists_file", type=str, help="File containing pages to patch")
    patch_parser.add_argument('patch_names', nargs='+', type=str, help='List of patch names to apply')
    patch_parser.set_defaults(func=command_cli)

    # Parse the arguments
    args = parser.parse_args()

    # Call the appropriate function based on the subcommand
    args.func(args)


if __name__ == "__main__":
    main()
