#!/usr/bin/env python3
"""Small Yuque Open API helper for Codex skill workflows.

The script is intentionally dependency-free. It defaults to dry-run for writes
and reads credentials only from environment variables.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://www.yuque.com/api/v2"
DEFAULT_USER_AGENT = "codex-yuque-publishing-skill/0.1"


class YuqueError(RuntimeError):
    pass


def env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value else default


def redact(text: str, token: str | None) -> str:
    if token:
        text = text.replace(token, "[REDACTED]")
    return re.sub(r"(X-Auth-Token\s*[:=]\s*)\S+", r"\1[REDACTED]", text, flags=re.I)


def namespace_path(namespace: str) -> str:
    parts = [p for p in namespace.strip("/").split("/") if p]
    if len(parts) != 2:
        raise YuqueError("namespace must look like 'group/book' or 'user/book'")
    return "/".join(quote(part, safe="") for part in parts)


def doc_path(doc: str) -> str:
    doc = doc.strip("/")
    if not doc:
        raise YuqueError("doc id or slug is required")
    return quote(doc, safe="")


def load_body(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise YuqueError(f"failed to read body file: {exc}") from exc


def clean_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    public = None
    if args.public is not None:
        public = 1 if args.public else 0
    return clean_payload(
        {
            "title": args.title,
            "slug": getattr(args, "slug", None),
            "body": load_body(args.file),
            "format": args.format,
            "public": public,
        }
    )


def request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    require_token: bool = True,
) -> dict[str, Any]:
    token = env("YUQUE_TOKEN")
    if require_token and not token:
        raise YuqueError("YUQUE_TOKEN is required for network requests")

    base_url = env("YUQUE_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    url = f"{base_url}/{path.lstrip('/')}"
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": env("YUQUE_USER_AGENT", DEFAULT_USER_AGENT) or DEFAULT_USER_AGENT,
    }
    if token:
        headers["X-Auth-Token"] = token

    req = Request(url, data=data, method=method.upper(), headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            if not raw:
                return {"status": resp.status, "data": None}
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {"raw": raw[:1000]}
            return {"status": resp.status, "data": body}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        safe = redact(raw[:2000], token)
        raise YuqueError(f"HTTP {exc.code}: {safe}") from exc
    except URLError as exc:
        raise YuqueError(f"network error: {redact(str(exc), token)}") from exc


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def command_preflight(args: argparse.Namespace) -> int:
    token = env("YUQUE_TOKEN")
    base_url = env("YUQUE_BASE_URL", DEFAULT_BASE_URL)
    print_json(
        {
            "base_url": base_url,
            "namespace": args.namespace,
            "token_present": bool(token),
            "token_preview": "[REDACTED]" if token else None,
        }
    )
    if args.offline:
        return 0
    if not token:
        raise YuqueError("YUQUE_TOKEN is required for online preflight")
    user = request_json("GET", "/user")
    repo = request_json("GET", f"/repos/{namespace_path(args.namespace)}")
    print_json({"user_check": safe_summary(user), "repo_check": safe_summary(repo)})
    return 0


def safe_summary(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data")
    result: dict[str, Any] = {"status": response.get("status")}
    if isinstance(data, dict):
        node = data.get("data", data)
        if isinstance(node, dict):
            for key in ("id", "login", "name", "title", "slug", "namespace"):
                if key in node:
                    result[key] = node[key]
    return result


def command_create_doc(args: argparse.Namespace) -> int:
    payload = build_payload(args)
    path = f"/repos/{namespace_path(args.namespace)}/docs"
    if not args.execute:
        print_json({"dry_run": True, "method": "POST", "path": path, "payload": payload})
        return 0
    result = request_json("POST", path, payload)
    print_json(safe_summary(result))
    return 0


def command_update_doc(args: argparse.Namespace) -> int:
    payload = build_payload(args)
    path = f"/repos/{namespace_path(args.namespace)}/docs/{doc_path(args.doc)}"
    if not args.execute:
        print_json({"dry_run": True, "method": "PUT", "path": path, "payload": payload})
        return 0
    result = request_json("PUT", path, payload)
    print_json(safe_summary(result))
    return 0


def add_content_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--namespace", required=True, help="Yuque namespace, e.g. azel/zob9yu")
    parser.add_argument("--title", required=True, help="Yuque document title")
    parser.add_argument("--file", required=True, help="Markdown or HTML body file")
    parser.add_argument("--format", default="markdown", choices=("markdown", "html", "lake"))
    visibility = parser.add_mutually_exclusive_group()
    visibility.add_argument("--public", dest="public", action="store_true", default=None)
    visibility.add_argument("--private", dest="public", action="store_false")
    parser.add_argument("--execute", action="store_true", help="Perform the write request")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Yuque publishing helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight", help="Check configuration and optional API access")
    preflight.add_argument("--namespace", required=True, help="Yuque namespace, e.g. azel/zob9yu")
    preflight.add_argument("--offline", action="store_true", help="Do not make network requests")
    preflight.set_defaults(func=command_preflight)

    create = subparsers.add_parser("create-doc", help="Create a Yuque document")
    add_content_args(create)
    create.add_argument("--slug", help="Optional Yuque document slug")
    create.set_defaults(func=command_create_doc)

    update = subparsers.add_parser("update-doc", help="Update a Yuque document")
    add_content_args(update)
    update.add_argument("--doc", required=True, help="Document id or slug")
    update.add_argument("--slug", help="Optional new slug")
    update.set_defaults(func=command_update_doc)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except YuqueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
