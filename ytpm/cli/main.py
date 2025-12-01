from __future__ import annotations

import argparse
import os
import sys
from typing import NoReturn

from ytpm.core.manager import Manager


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ytpm",
        description="YTPM – Yaron's tmux project manager (session-level CLI).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ytpm ls
    subparsers.add_parser(
        "ls",
        help="List existing tmux sessions.",
    )

    # ytpm new NAME [--path PATH]
    new_parser = subparsers.add_parser(
        "new",
        help="Create a new session.",
    )
    new_parser.add_argument("name", help="Name of the session to create.")
    new_parser.add_argument(
        "--path",
        "-p",
        dest="path",
        help="Working directory for the new session (default: current directory).",
    )

    # ytpm goto NAME [--path PATH]
    goto_parser = subparsers.add_parser(
        "goto",
        help="Create (if needed) and attach/switch to a session.",
    )
    goto_parser.add_argument("name", help="Name of the session to go to.")
    goto_parser.add_argument(
        "--path",
        "-p",
        dest="path",
        help="Working directory if session needs to be created (default: current directory).",
    )

    # ytpm kill NAME
    kill_parser = subparsers.add_parser(
        "kill",
        help="Kill a session if it exists.",
    )
    kill_parser.add_argument("name", help="Name of the session to kill.")

    return parser


def main(argv: list[str] | None = None) -> NoReturn:
    if argv is None:
        argv = sys.argv[1:]

    parser = _build_parser()
    args = parser.parse_args(argv)

    manager = Manager()  # uses real TmuxAdapter under the hood

    try:
        if args.command == "ls":
            sessions = manager.list_sessions()
            # Print one per line; simple and script-friendly
            for name in sessions:
                print(name)

        elif args.command == "new":
            cwd = args.path or os.getcwd()
            manager.create_session(args.name, cwd)

        elif args.command == "goto":
            cwd = args.path or os.getcwd()
            manager.goto_session(args.name, cwd)

        elif args.command == "kill":
            manager.kill_session(args.name)

        else:
            # Should never happen due to required=True, but just in case:
            parser.print_help()
            sys.exit(1)

    except Exception as exc:
        # For now: simple error reporting.
        # Later, you can refine error types and messages.
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
