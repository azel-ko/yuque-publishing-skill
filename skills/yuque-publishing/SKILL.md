---
name: yuque-publishing
description: Publish, update, or prepare articles for Yuque knowledge bases. Use when Codex needs to turn drafts, notes, research, implementation reports, or technical articles into structured Yuque pages; choose a Yuque destination, run a dry-run, handle Yuque Open API token authentication safely, and publish or update documents only after the target and side effect are clear.
---

# Yuque Publishing

Prepare and publish structured documents to Yuque while keeping credentials out of the skill, repository, command output, and conversation history.

## Quick Start

1. Identify the source content, title, intended audience, and whether the request is a new page or an update.
2. Choose the Yuque knowledge base and directory. For Azel's default setup, use:
   - Knowledge base: `AI Native Engineering`
   - URL namespace: `azel/zob9yu`
   - Default URL: `https://www.yuque.com/azel/zob9yu`
3. Choose the closest directory by content:
   - `Agent 架构`
   - `Prompt 工程`
   - `RAG 与知识库`
   - `工具调用与工作流`
   - `评测与可观测性`
   - `安全与权限`
   - `项目案例`
   - `文章草稿`
4. Read `references/authentication.md` before using credentials. Ask the user to choose official OAuth/app authorization or Open API token, browser session automation, or cookie/session extraction. Use `scripts/yuque_auth.py select` when the user has not already chosen. Default to official auth/token when available.
5. Run the relevant helper in dry-run mode and inspect the payload or browser plan.
6. Confirm the final target and operation before a non-dry-run create/update.
7. Verify the returned Yuque URL or fetch the page after publishing.

## Workflow

### 1. Scope the publish

Clarify only what blocks a safe publish:

- Target knowledge base or namespace, if not using `azel/zob9yu`.
- New page vs. update existing page.
- Title, slug, directory, visibility, and source material.
- Whether the user expects a final live publish now or only a prepared payload.

If directory placement cannot be controlled by the confirmed API path, publish to the correct knowledge base and state that catalog placement remains manual or requires a separate supported API step.

### 2. Prepare content

Convert the source into clean Markdown unless the user or existing page requires HTML.

- Keep the title outside the body when the API has a dedicated `title` field.
- Preserve source links, decisions, dates, and owners.
- Add a short summary near the top for long articles.
- Avoid hidden credentials, cookies, internal tokens, or raw logs in the body.
- Use a stable slug if the user provides one; otherwise derive a short lowercase slug from the title when appropriate.

### 3. Authenticate safely

Follow `references/authentication.md`.

Use official auth or Open API token by default when available:

```bash
export YUQUE_TOKEN="..."
python3 scripts/yuque_publish.py preflight --namespace azel/zob9yu
```

Do not ask the user to paste a token into chat. If a token has already appeared in chat, tell the user to rotate it before use.

For non-Super Member accounts that cannot create tokens, offer browser session automation first. Offer cookie/session extraction only after explicitly stating that it has the broadest permissions and should be treated like a password.

Selection helper:

```bash
python3 scripts/yuque_auth.py select
python3 scripts/yuque_auth.py select --mode browser --title "Article Title" --file article.md
```

Dedicated browser profiles do not reduce Yuque account permissions; they only reduce local exposure compared with reading the user's main browser profile.

Browser-session helper:

```bash
python3 scripts/yuque_browser.py login --space-url https://www.yuque.com/azel/zob9yu
python3 scripts/yuque_browser.py create-doc --space-url https://www.yuque.com/azel/zob9yu --title "Article Title" --file article.md
```

Use browser-session mode only when a visible guided UI flow is acceptable. For background publishing after the isolated profile is logged in, use the cookie/session helper in headless mode instead.

Cookie/session helper:

```bash
python3 scripts/yuque_session.py login --space-url https://www.yuque.com/azel/zob9yu
python3 scripts/yuque_session.py preflight --space-url https://www.yuque.com/azel/zob9yu --headless
python3 scripts/yuque_session.py create-doc --space-url https://www.yuque.com/azel/zob9yu --title "Article Title" --file article.md
python3 scripts/yuque_session.py create-doc --space-url https://www.yuque.com/azel/zob9yu --title "Article Title" --file article.md --headless --execute --i-understand-session-risk
```

### 4. Dry-run first

Generate a payload without network side effects:

```bash
python3 scripts/yuque_publish.py create-doc \
  --namespace azel/zob9yu \
  --title "Article Title" \
  --slug article-title \
  --file article.md
```

The command above is a dry-run by default. It prints the target endpoint and JSON payload without printing credentials.

### 5. Publish or update

After the user confirms the exact target and side effect, run with `--execute`:

```bash
python3 scripts/yuque_publish.py create-doc \
  --namespace azel/zob9yu \
  --title "Article Title" \
  --slug article-title \
  --file article.md \
  --execute
```

For updates, use `update-doc` with the known document id or slug supported by the current API contract:

```bash
python3 scripts/yuque_publish.py update-doc \
  --namespace azel/zob9yu \
  --doc article-title \
  --title "Article Title" \
  --file article.md \
  --execute
```

### 6. Verify and report

Report:

- Created or updated page title.
- Yuque URL or returned document id.
- Directory chosen and any catalog placement limitation.
- Verification command or API response summary.

Never include token values, cookies, or full raw HTTP headers in the final answer.

## Resources

- `references/authentication.md`: credential handling, auth mode selection, token/session boundaries, redaction, and CI guidance.
- `references/api-contract.md`: Yuque Open API assumptions, endpoints, and update caveats.
- `references/publishing-policy.md`: default destination, directory mapping, and publication safety rules.
- `scripts/yuque_auth.py`: auth mode selector that explains permission and local exposure.
- `scripts/yuque_publish.py`: standard-library helper for preflight, dry-run payload rendering, create, and update.
- `scripts/yuque_browser.py`: Playwright browser-session helper that does not export cookies.
- `scripts/yuque_session.py`: explicit cookie/session fallback using the isolated skill profile.
