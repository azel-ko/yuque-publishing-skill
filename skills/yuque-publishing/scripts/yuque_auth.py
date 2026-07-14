#!/usr/bin/env python3
"""Auth-mode selector for the Yuque publishing skill."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_SPACE_URL = "https://www.yuque.com/azel/zob9yu"
DEFAULT_NAMESPACE = "azel/zob9yu"
DEFAULT_PROFILE_DIR = Path("~/.local/share/yuque-publishing/browser-profile").expanduser()

MODES = {
    "token": {
        "label": "Open API Token",
        "yuque_permission": "Depends on the token; prefer least privilege.",
        "local_exposure": "Only the token value is exposed to the runtime environment.",
        "best_for": "Users who can create a Yuque Open API token or use official app auth.",
    },
    "browser": {
        "label": "Browser session automation",
        "yuque_permission": "Full permissions of the logged-in Yuque account.",
        "local_exposure": "Only the dedicated skill browser profile is exposed.",
        "best_for": "Users who cannot create a token but can log in in a browser.",
    },
    "session": {
        "label": "Cookie/session fallback",
        "yuque_permission": "Full permissions of the logged-in Yuque account.",
        "local_exposure": "Only the dedicated skill browser profile is exposed, but session values are used programmatically.",
        "best_for": "Advanced fallback when browser UI automation is insufficient.",
    },
}


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def token_commands(args: argparse.Namespace) -> list[str]:
    title = args.title or "Article Title"
    file_arg = args.file or "article.md"
    return [
        f"export YUQUE_TOKEN=\"...\"",
        f"python3 scripts/yuque_publish.py preflight --namespace {args.namespace}",
        (
            "python3 scripts/yuque_publish.py create-doc "
            f"--namespace {args.namespace} --title {quote_shell(title)} --file {quote_shell(file_arg)}"
        ),
        (
            "python3 scripts/yuque_publish.py create-doc "
            f"--namespace {args.namespace} --title {quote_shell(title)} --file {quote_shell(file_arg)} --execute"
        ),
    ]


def browser_commands(args: argparse.Namespace) -> list[str]:
    title = args.title or "Article Title"
    file_arg = args.file or "article.md"
    return [
        f"python3 scripts/yuque_browser.py login --space-url {quote_shell(args.space_url)}",
        (
            "python3 scripts/yuque_browser.py create-doc "
            f"--space-url {quote_shell(args.space_url)} --title {quote_shell(title)} --file {quote_shell(file_arg)}"
        ),
        (
            "python3 scripts/yuque_browser.py create-doc "
            f"--space-url {quote_shell(args.space_url)} --title {quote_shell(title)} --file {quote_shell(file_arg)} --execute"
        ),
    ]


def session_commands(args: argparse.Namespace) -> list[str]:
    title = args.title or "Article Title"
    file_arg = args.file or "article.md"
    return [
        f"python3 scripts/yuque_session.py login --space-url {quote_shell(args.space_url)}",
        f"python3 scripts/yuque_session.py preflight --space-url {quote_shell(args.space_url)}",
        (
            "python3 scripts/yuque_session.py create-doc "
            f"--space-url {quote_shell(args.space_url)} --title {quote_shell(title)} --file {quote_shell(file_arg)}"
        ),
        (
            "python3 scripts/yuque_session.py create-doc "
            f"--space-url {quote_shell(args.space_url)} --title {quote_shell(title)} --file {quote_shell(file_arg)} "
            "--execute --i-understand-session-risk"
        ),
    ]


def quote_shell(value: str) -> str:
    if value.replace("/", "").replace(".", "").replace("-", "").replace("_", "").isalnum():
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"


def select_mode_interactively() -> str:
    print("Choose Yuque authentication mode:")
    print("1. Open API Token / official auth")
    print("2. Browser session automation")
    print("3. Cookie/session fallback")
    while True:
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice == "1":
            return "token"
        if choice == "2":
            return "browser"
        if choice == "3":
            return "session"
        print("Invalid choice.")


def command_select(args: argparse.Namespace) -> int:
    mode = args.mode or select_mode_interactively()
    command_map = {
        "token": token_commands,
        "browser": browser_commands,
        "session": session_commands,
    }
    result = {
        "mode": mode,
        "label": MODES[mode]["label"],
        "best_for": MODES[mode]["best_for"],
        "yuque_permission": MODES[mode]["yuque_permission"],
        "local_exposure": MODES[mode]["local_exposure"],
        "space_url": args.space_url,
        "namespace": args.namespace,
        "dedicated_profile_dir": str(DEFAULT_PROFILE_DIR),
        "token_present": bool(os.environ.get("YUQUE_TOKEN")),
        "commands": command_map[mode](args),
    }
    if mode == "session":
        result["risk_ack_required"] = "--i-understand-session-risk"
        result["warning"] = (
            "Dedicated profile reduces local blast radius only; it does not reduce Yuque account permissions."
        )
    if args.json:
        print_json(result)
        return 0
    print(f"Selected: {result['label']}")
    print(f"Best for: {result['best_for']}")
    print(f"Yuque permission: {result['yuque_permission']}")
    print(f"Local exposure: {result['local_exposure']}")
    if "warning" in result:
        print(f"Warning: {result['warning']}")
    print("\nNext commands:")
    for command in result["commands"]:
        print(f"  {command}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Choose a Yuque publishing authentication mode")
    subparsers = parser.add_subparsers(dest="command", required=True)

    select = subparsers.add_parser("select", help="choose and explain a Yuque auth mode")
    select.add_argument("--mode", choices=sorted(MODES), help="skip the interactive prompt")
    select.add_argument("--space-url", default=DEFAULT_SPACE_URL)
    select.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    select.add_argument("--title")
    select.add_argument("--file")
    select.add_argument("--json", action="store_true")
    select.set_defaults(func=command_select)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
