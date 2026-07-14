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
DEFAULT_SKILL_DIR = Path(__file__).resolve().parents[1]

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
        "best_for": "Users who cannot create a token and are willing to use a visible guided Yuque browser window.",
    },
    "session": {
        "label": "Cookie/session background publishing",
        "yuque_permission": "Full permissions of the logged-in Yuque account.",
        "local_exposure": "Only the dedicated skill browser profile is exposed, but session values are used programmatically.",
        "best_for": "Background/headless publishing after the isolated browser profile is already logged in.",
    },
}


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def skill_dir() -> Path:
    configured = os.environ.get("CLAUDE_SKILL_DIR") or os.environ.get("YUQUE_SKILL_DIR")
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_SKILL_DIR


def script_cmd(script_name: str) -> str:
    return f"python3 {quote_shell(str(skill_dir() / 'scripts' / script_name))}"


def token_commands(args: argparse.Namespace) -> list[str]:
    title = args.title or "Article Title"
    file_arg = args.file or "article.md"
    publish = script_cmd("yuque_publish.py")
    return [
        f"export YUQUE_TOKEN=\"...\"",
        f"{publish} preflight --namespace {args.namespace}",
        (
            f"{publish} create-doc "
            f"--namespace {args.namespace} --title {quote_shell(title)} --file {quote_shell(file_arg)}"
        ),
        (
            f"{publish} create-doc "
            f"--namespace {args.namespace} --title {quote_shell(title)} --file {quote_shell(file_arg)} --execute"
        ),
    ]


def browser_commands(args: argparse.Namespace) -> list[str]:
    title = args.title or "Article Title"
    file_arg = args.file or "article.md"
    browser = script_cmd("yuque_browser.py")
    return [
        f"{browser} login --space-url {quote_shell(args.space_url)}",
        (
            f"{browser} create-doc "
            f"--space-url {quote_shell(args.space_url)} --title {quote_shell(title)} --file {quote_shell(file_arg)}"
        ),
        (
            f"{browser} create-doc "
            f"--space-url {quote_shell(args.space_url)} --title {quote_shell(title)} --file {quote_shell(file_arg)} --execute"
        ),
    ]


def session_commands(args: argparse.Namespace) -> list[str]:
    title = args.title or "Article Title"
    file_arg = args.file or "article.md"
    session = script_cmd("yuque_session.py")
    return [
        f"{session} login --space-url {quote_shell(args.space_url)}",
        f"{session} preflight --space-url {quote_shell(args.space_url)} --headless",
        (
            f"{session} create-doc "
            f"--space-url {quote_shell(args.space_url)} --title {quote_shell(title)} --file {quote_shell(file_arg)}"
        ),
        (
            f"{session} create-doc "
            f"--space-url {quote_shell(args.space_url)} --title {quote_shell(title)} --file {quote_shell(file_arg)} "
            "--headless --execute --i-understand-session-risk"
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
        "skill_dir": str(skill_dir()),
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
