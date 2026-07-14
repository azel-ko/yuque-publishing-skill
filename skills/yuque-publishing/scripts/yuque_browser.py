#!/usr/bin/env python3
"""Browser-session Yuque publishing helper.

This helper uses an isolated Playwright browser profile. It does not export or
print cookies. The create-doc command is deliberately guided because Yuque's
web editor is a private UI surface that may change.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_PROFILE_DIR = Path("~/.local/share/yuque-publishing/browser-profile").expanduser()
DEFAULT_SPACE_URL = "https://www.yuque.com/azel/zob9yu"
DEFAULT_LOGIN_URL = "https://www.yuque.com/login"
DEFAULT_BROWSER_PATHS = (
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
)


class YuqueBrowserError(RuntimeError):
    pass


def ensure_playwright() -> Any:
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise YuqueBrowserError(
            "Playwright is required for browser-session mode. Install it with: "
            "python3 -m pip install playwright && python3 -m playwright install chromium"
        ) from exc
    return sync_playwright, PlaywrightTimeoutError


def profile_dir(path: str | None) -> Path:
    return Path(path).expanduser() if path else DEFAULT_PROFILE_DIR


def load_body(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise YuqueBrowserError(f"failed to read body file: {exc}") from exc


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    try:
        path.chmod(0o700)
    except OSError:
        pass


def browser_executable() -> str | None:
    configured = os.environ.get("YUQUE_BROWSER_EXECUTABLE")
    if configured and Path(configured).exists():
        return configured
    for candidate in DEFAULT_BROWSER_PATHS:
        if Path(candidate).exists():
            return candidate
    return None


def launch_context(playwright: Any, path: Path, *, headless: bool = False) -> Any:
    ensure_private_dir(path)
    executable_path = browser_executable()
    kwargs = {"executable_path": executable_path} if executable_path else {}
    context = playwright.chromium.launch_persistent_context(
        str(path),
        headless=headless,
        viewport={"width": 1440, "height": 1000},
        accept_downloads=False,
        **kwargs,
    )
    context.grant_permissions(["clipboard-read", "clipboard-write"], origin="https://www.yuque.com")
    return context


def wait_for_enter_or_hold(prompt: str, keep_open_seconds: int) -> None:
    if sys.stdin.isatty():
        input(prompt)
        return

    print(prompt)
    if keep_open_seconds <= 0:
        print("stdin is not interactive; keeping the browser open until this command is stopped.")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            return

    print(
        "stdin is not interactive; keeping the browser open for "
        f"{keep_open_seconds} seconds. Stop the command after login if needed."
    )
    try:
        time.sleep(keep_open_seconds)
    except KeyboardInterrupt:
        return


def require_interactive_stdin(command: str) -> None:
    if not sys.stdin.isatty():
        raise YuqueBrowserError(
            f"{command} requires an interactive terminal because it waits for manual browser steps. "
            "Run it from a terminal/TTY, or use cookie/session mode for programmatic creation."
        )


def command_login(args: argparse.Namespace) -> int:
    sync_playwright, _ = ensure_playwright()
    path = profile_dir(args.profile_dir)
    target = args.goto or args.space_url or DEFAULT_SPACE_URL
    login_url = f"{DEFAULT_LOGIN_URL}?goto={target}"
    print(f"Opening isolated Yuque browser profile: {path}")
    print("Log in in the opened browser window. Cookies stay inside this profile.")
    print("This still grants the full Yuque permissions of the logged-in account.")
    with sync_playwright() as p:
        context = launch_context(p, path, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(login_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
        wait_for_enter_or_hold(
            "After Yuque login finishes in the browser, press Enter here to close it...",
            args.keep_open_seconds,
        )
        context.close()
    print("Login profile saved locally. No cookies were exported.")
    return 0


def command_status(args: argparse.Namespace) -> int:
    sync_playwright, _ = ensure_playwright()
    path = profile_dir(args.profile_dir)
    if not path.exists():
        raise YuqueBrowserError(f"profile does not exist: {path}. Run login first.")
    with sync_playwright() as p:
        context = launch_context(p, path, headless=args.headless)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(args.space_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
        current_url = page.url
        title = page.title()
        context.close()
    print_json(
        {
            "profile_dir": str(path),
            "space_url": args.space_url,
            "current_url": current_url,
            "title": title,
            "login_required_heuristic": "/login" in current_url,
        }
    )
    return 0


def copy_to_clipboard(page: Any, text: str) -> bool:
    try:
        page.evaluate(
            """async value => {
                await navigator.clipboard.writeText(value);
                return true;
            }""",
            text,
        )
        return True
    except Exception:
        return False


def command_create_doc(args: argparse.Namespace) -> int:
    body = load_body(args.file)
    path = profile_dir(args.profile_dir)
    plan = {
        "mode": "browser-session",
        "dry_run": not args.execute,
        "profile_dir": str(path),
        "space_url": args.space_url,
        "title": args.title,
        "file": args.file,
        "body_chars": len(body),
        "exports_cookies": False,
        "yuque_permission": "full logged-in account permissions",
        "local_exposure": "dedicated skill browser profile only",
    }
    if not args.execute:
        print_json(plan)
        return 0
    require_interactive_stdin("browser-session create-doc")
    if not path.exists():
        raise YuqueBrowserError(f"profile does not exist: {path}. Run login first.")

    sync_playwright, _ = ensure_playwright()
    with sync_playwright() as p:
        context = launch_context(p, path, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(args.space_url, wait_until="domcontentloaded", timeout=args.timeout_ms)

        print("Browser opened with the isolated Yuque profile.")
        print("In the browser, create a new Yuque document or open a blank editor.")
        print("When the title field is focused, return here and press Enter.")
        input()
        page.keyboard.insert_text(args.title)

        print("Now focus the document body/editor area in the browser, then press Enter here.")
        input()
        if args.clipboard and copy_to_clipboard(page, body):
            print("Article body was copied to the browser clipboard. Press Ctrl+V in the editor.")
            if args.auto_paste:
                page.keyboard.press("Control+V")
        else:
            print("Clipboard write was unavailable; inserting text through keyboard automation.")
            page.keyboard.insert_text(body)

        print("Review and save/publish in Yuque manually. Press Enter here after verification.")
        input()
        context.close()
    print_json({"mode": "browser-session", "completed": True, "profile_dir": str(path)})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Yuque browser-session helper")
    parser.add_argument(
        "--profile-dir",
        help=f"isolated browser profile directory (default: {DEFAULT_PROFILE_DIR})",
    )
    parser.add_argument("--timeout-ms", type=int, default=60000)
    subparsers = parser.add_subparsers(dest="command", required=True)

    login = subparsers.add_parser("login", help="open Yuque login in an isolated browser profile")
    login.add_argument("--space-url", default=DEFAULT_SPACE_URL)
    login.add_argument("--goto", help="login redirect target")
    login.add_argument(
        "--keep-open-seconds",
        type=int,
        default=1800,
        help="when stdin is not interactive, keep the browser open for this many seconds; use 0 to wait forever",
    )
    login.set_defaults(func=command_login)

    status = subparsers.add_parser("status", help="open the profile and check a Yuque URL")
    status.add_argument("--space-url", default=DEFAULT_SPACE_URL)
    status.add_argument("--headless", action="store_true")
    status.set_defaults(func=command_status)

    create = subparsers.add_parser("create-doc", help="guided UI creation using the browser session")
    create.add_argument("--space-url", default=DEFAULT_SPACE_URL)
    create.add_argument("--title", required=True)
    create.add_argument("--file", required=True)
    create.add_argument("--execute", action="store_true", help="open the browser and perform guided steps")
    create.add_argument(
        "--clipboard",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="copy body to browser clipboard when possible",
    )
    create.add_argument("--auto-paste", action="store_true", help="press Ctrl+V after clipboard write")
    create.set_defaults(func=command_create_doc)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except YuqueBrowserError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
