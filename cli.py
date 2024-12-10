import argparse
from getpass import getpass
from utls.base_requests import login




def login_cli(args):
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")
    print(f"Logging in with username: {username}")
    login(username, password)


def command_cli(args):
    # Implement the patch functionality here
    print(f"Patching with file: {args.file}")


def main():
    parser = argparse.ArgumentParser(description="A CLI tool with subcommands.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available subcommands')

    # Login subcommand
    login_parser = subparsers.add_parser('login', help='Authenticate a user')
    login_parser.set_defaults(func=login_cli)

    # Command subcommand
    patch_parser = subparsers.add_parser('command', help='Apply a patch')
    patch_parser.add_argument('type', type=str, help='type to command')
    patch_parser.set_defaults(func=command_cli)

    # Parse the arguments
    args = parser.parse_args()

    # Call the appropriate function based on the subcommand
    args.func(args)


if __name__ == "__main__":
    main()
