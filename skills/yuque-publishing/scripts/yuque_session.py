#!/usr/bin/env python3
"""Cookie/session Yuque helper for explicit advanced use.

This script only uses the isolated Playwright profile created for this skill.
It does not read the user's normal browser profile and does not print cookies.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


DEFAULT_PROFILE_DIR = Path("~/.local/share/yuque-publishing/browser-profile").expanduser()
DEFAULT_SPACE_URL = "https://www.yuque.com/azel/zob9yu"
DEFAULT_WEB_BASE_URL = "https://www.yuque.com"
DEFAULT_DOC_ENDPOINT = "/api/docs"
DEFAULT_BROWSER_PATHS = (
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
)

SENSITIVE_HEADER_RE = re.compile(
    r"((?:cookie|set-cookie|x-csrf-token|x-auth-token)\s*[:=]\s*)[^\n\r]+",
    re.I,
)


class YuqueSessionError(RuntimeError):
    pass


def ensure_playwright() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise YuqueSessionError(
            "Playwright is required for cookie/session mode. Install it with: "
            "python3 -m pip install playwright && python3 -m playwright install chromium"
        ) from exc
    return sync_playwright


def redact(text: str) -> str:
    return SENSITIVE_HEADER_RE.sub(r"\1[REDACTED]", text)


def profile_dir(path: str | None) -> Path:
    return Path(path).expanduser() if path else DEFAULT_PROFILE_DIR


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


def load_body(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise YuqueSessionError(f"failed to read body file: {exc}") from exc


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def launch_context(playwright: Any, path: Path, *, headless: bool = True) -> Any:
    ensure_private_dir(path)
    executable_path = browser_executable()
    kwargs = {"executable_path": executable_path} if executable_path else {}
    return playwright.chromium.launch_persistent_context(
        str(path),
        headless=headless,
        viewport={"width": 1440, "height": 1000},
        accept_downloads=False,
        **kwargs,
    )


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


def require_risk_ack(args: argparse.Namespace) -> None:
    if not args.i_understand_session_risk:
        raise YuqueSessionError(
            "cookie/session mode has maximum account-level permission. "
            "Pass --i-understand-session-risk to execute."
        )


def cookie_value(context: Any, name: str) -> str | None:
    for cookie in context.cookies(DEFAULT_WEB_BASE_URL):
        if cookie.get("name") == name:
            value = cookie.get("value")
            return str(value) if value else None
    return None


def safe_response_summary(response: Any, text: str) -> dict[str, Any]:
    safe_text = redact(text[:2000])
    result: dict[str, Any] = {
        "status": response.status,
        "ok": response.ok,
        "url": response.url,
    }
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        result["body_preview"] = safe_text
        return result
    if isinstance(payload, dict):
        node = payload.get("data", payload)
        summary: dict[str, Any] = {}
        if isinstance(node, dict):
            for key in ("id", "title", "slug", "login", "name", "book_id", "url"):
                if key in node:
                    summary[key] = node[key]
        result["data"] = summary or {"keys": sorted(str(k) for k in payload.keys())[:20]}
    return result


def parse_app_data(html: str) -> dict[str, Any] | None:
    match = re.search(r'window\.appData = JSON\.parse\(decodeURIComponent\("([\s\S]*?)"\)\);', html)
    if not match:
        return None
    from urllib.parse import unquote

    try:
        return json.loads(unquote(match.group(1)))
    except json.JSONDecodeError:
        return None


def extract_book_id(app_data: dict[str, Any] | None) -> int | None:
    if not isinstance(app_data, dict):
        return None
    book = app_data.get("book")
    if isinstance(book, dict) and isinstance(book.get("id"), int):
        return int(book["id"])
    return None


def command_login(args: argparse.Namespace) -> int:
    sync_playwright = ensure_playwright()
    path = profile_dir(args.profile_dir)
    ensure_private_dir(path)
    print(f"Opening isolated Yuque browser profile: {path}")
    print("Log in in the opened browser. Session values stay in this isolated profile.")
    print("This still grants the full Yuque permissions of the logged-in account.")
    with sync_playwright() as p:
        context = launch_context(p, path, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(args.space_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
        wait_for_enter_or_hold(
            "After login succeeds in the browser, press Enter here to close it...",
            args.keep_open_seconds,
        )
        context.close()
    return 0


def command_preflight(args: argparse.Namespace) -> int:
    path = profile_dir(args.profile_dir)
    if not path.exists():
        raise YuqueSessionError(f"profile does not exist: {path}. Run login first.")
    sync_playwright = ensure_playwright()
    with sync_playwright() as p:
        context = launch_context(p, path, headless=args.headless)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(args.space_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
        html = page.content()
        app_data = parse_app_data(html)
        book_id = extract_book_id(app_data)
        csrf_present = bool(cookie_value(context, "yuque_ctoken"))
        current_url = page.url
        title = page.title()
        context.close()
    print_json(
        {
            "mode": "cookie-session",
            "headless": args.headless,
            "profile_dir": str(path),
            "space_url": args.space_url,
            "current_url": current_url,
            "title": title,
            "login_required_heuristic": "/login" in current_url,
            "csrf_cookie_present": csrf_present,
            "book_id": book_id,
            "cookies_exported": False,
            "yuque_permission": "full logged-in account permissions",
            "local_exposure": "dedicated skill browser profile only",
        }
    )
    return 0


def build_doc_payload(args: argparse.Namespace, book_id: int | None) -> dict[str, Any]:
    if book_id is None:
        raise YuqueSessionError("book id is required; pass --book-id or use a readable --space-url")
    payload: dict[str, Any] = {
        "book_id": book_id,
        "title": args.title,
        "body": load_body(args.file),
        "format": args.format,
    }
    if args.slug:
        payload["slug"] = args.slug
    if args.public is not None:
        payload["public"] = 1 if args.public else 0
    return payload


def command_create_doc(args: argparse.Namespace) -> int:
    path = profile_dir(args.profile_dir)
    body = load_body(args.file)
    dry_run_plan = {
        "mode": "cookie-session",
        "dry_run": not args.execute,
        "profile_dir": str(path),
        "space_url": args.space_url,
        "endpoint": args.endpoint,
        "title": args.title,
        "slug": args.slug,
        "format": args.format,
        "headless": args.headless,
        "body_chars": len(body),
        "exports_cookies": False,
        "requires_risk_ack": True,
        "yuque_permission": "full logged-in account permissions",
        "local_exposure": "dedicated skill browser profile only; session values are used programmatically",
    }
    if not args.execute:
        print_json(dry_run_plan)
        return 0
    require_risk_ack(args)
    if not path.exists():
        raise YuqueSessionError(f"profile does not exist: {path}. Run login first.")

    sync_playwright = ensure_playwright()
    with sync_playwright() as p:
        context = launch_context(p, path, headless=args.headless)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(args.space_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
        app_data = parse_app_data(page.content())
        book_id = args.book_id or extract_book_id(app_data)
        payload = build_doc_payload(args, book_id)
        csrf = cookie_value(context, "yuque_ctoken")
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-requested-with": "XMLHttpRequest",
        }
        if csrf:
            headers["x-csrf-token"] = csrf
        if args.login:
            headers["x-login"] = args.login

        url = urljoin(args.base_url.rstrip("/") + "/", args.endpoint.lstrip("/"))
        response = context.request.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False))
        text = response.text()
        summary = safe_response_summary(response, text)
        context.close()
    print_json(summary)
    return 0 if summary.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Yuque cookie/session helper")
    parser.add_argument(
        "--profile-dir",
        help=f"isolated browser profile directory (default: {DEFAULT_PROFILE_DIR})",
    )
    parser.add_argument("--timeout-ms", type=int, default=60000)
    subparsers = parser.add_subparsers(dest="command", required=True)

    login = subparsers.add_parser("login", help="open Yuque login in the isolated profile")
    login.add_argument("--space-url", default=DEFAULT_SPACE_URL)
    login.add_argument(
        "--keep-open-seconds",
        type=int,
        default=1800,
        help="when stdin is not interactive, keep the browser open for this many seconds; use 0 to wait forever",
    )
    login.set_defaults(func=command_login)

    preflight = subparsers.add_parser("preflight", help="inspect isolated profile login state")
    preflight.add_argument("--space-url", default=DEFAULT_SPACE_URL)
    preflight.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="run without opening a browser window (default); pass --no-headless for debugging",
    )
    preflight.set_defaults(func=command_preflight)

    create = subparsers.add_parser("create-doc", help="create a document through Yuque web session API")
    create.add_argument("--space-url", default=DEFAULT_SPACE_URL)
    create.add_argument("--base-url", default=DEFAULT_WEB_BASE_URL)
    create.add_argument("--endpoint", default=DEFAULT_DOC_ENDPOINT)
    create.add_argument("--book-id", type=int, help="Yuque book id; auto-detected from --space-url when possible")
    create.add_argument("--login", help="optional Yuque login value for x-login header")
    create.add_argument("--title", required=True)
    create.add_argument("--slug")
    create.add_argument("--file", required=True)
    create.add_argument("--format", default="markdown", choices=("markdown", "html", "lake"))
    visibility = create.add_mutually_exclusive_group()
    visibility.add_argument("--public", dest="public", action="store_true", default=None)
    visibility.add_argument("--private", dest="public", action="store_false")
    create.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="run without opening a browser window (default); pass --no-headless for debugging",
    )
    create.add_argument("--execute", action="store_true", help="perform the session request")
    create.add_argument(
        "--i-understand-session-risk",
        action="store_true",
        help="required with --execute; session cookies usually have full account permissions",
    )
    create.set_defaults(func=command_create_doc)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except YuqueSessionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
