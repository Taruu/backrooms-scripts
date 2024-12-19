import argparse
import sys
import time
from getpass import getpass
from urllib.parse import urlparse

import config
from utls.base_utils import login_auth, Article, token_auth
import importlib
from config import logger

sys.path.append("modules")


def login_cli(args):
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    logger.info(f"Logging in with username: {username}")
    login_auth(username, password)


def token_cli(args):
    token_value = getpass("Enter your token: ")
    logger.info(f"Logging in with token")
    token_auth(token_value)


def command_cli(args):
    file = open(args.pages_lists_file, 'r')
    modules = [importlib.import_module(module_name) for module_name in args.patch_names]

    for link in file.readlines():
        time.sleep(0.1)
        if not link:
            continue

        url_obj = urlparse(link)
        if f"{url_obj.scheme}://{url_obj.netloc}" != config.BASE_URL:
            logger.error(f"This not current target site! {url_obj.geturl()} not in {config.BASE_URL}")
            continue
        page_name = url_obj.path[1:]

        logger.info(f"Load {page_name}")
        article = Article(page_name)

        before_patches = article.source_code
        applied_patches = []

        for module in modules:
            before_patch = article.source_code
            logger.info(f"Applied patch {module.__name__} for page {article.page_name}")
            article = module.handle(article)

            if before_patch != article.source_code:
                applied_patches.append(module.__name__)

        comment = f"Automated edit. Applied next patches:\n" \
                  f" {','.join([str(module_name) for module_name in applied_patches])}"
        logger.info(f"Start Upload patch for page {article.page_name}")
        # status = True
        if before_patches != article.source_code:
            status = article.update_source_code(comment)

            if not status:
                logger.error(f"Not update page {article.page_name}")
                break
            else:
                logger.success(f"Upload patch for page {article.page_name}")
        else:
            logger.warning(f"Nothing to change for page {article.page_name}")


def main():
    parser = argparse.ArgumentParser(description="A CLI tool with subcommands.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available subcommands')

    # Login subcommand
    login_parser = subparsers.add_parser('login', help='Authenticate a user')
    login_parser.set_defaults(func=login_cli)

    # Token subcommand
    login_parser = subparsers.add_parser('token', help='Authenticate a bot')
    login_parser.set_defaults(func=token_cli)

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
