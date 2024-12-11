import argparse
import sys
from getpass import getpass
from utls.base_utils import login
import importlib

def login_cli(args):
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    print(f"Logging in with username: {username}")
    login(username, password)


def command_cli(args):
    sys.path.append("modules")
    print(args.patch_names)
    #module = importlib.import_module(args.patch_name)


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
