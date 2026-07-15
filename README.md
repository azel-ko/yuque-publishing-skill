# Yuque Publishing Skill

English | [中文](README.zh-CN.md)

> Yuque/语雀 publishing Agent Skill for OpenAI Codex, Claude Code, and Agent Skills CLI. Publish Markdown articles to Yuque with Open API token, browser-session automation, or cookie/session fallback.

**Keywords:** Yuque skill, 语雀 skill, Yuque API, OpenAI Codex skill, Claude Code skill, Agent Skills CLI, Markdown to Yuque, knowledge base publishing, browser session automation, cookie session publishing.

Codex and Claude Code skill for preparing, dry-running, publishing, and updating Yuque articles with safe token handling. It is designed for both official Yuque Open API token users and non-Super Member users who need browser-session based publishing.

## What It Does

- Turns drafts, notes, and technical articles into structured Yuque pages.
- Uses Yuque Open API with `X-Auth-Token` authentication.
- Supports browser-session and explicit cookie/session fallback modes for users who cannot create API tokens.
- Recommends cookie/session mode for the most complete current feature set.
- Can add documents to the Yuque left catalog/sidebar in browser-session and cookie/session modes through Yuque's internal web API.
- Keeps credentials out of the repository and out of skill files.
- Runs write operations as dry-runs by default.
- Requires explicit `--execute` before creating or updating Yuque documents.

## Quick Start

1. Install the skill for the agent you use:

```bash
# Agent Skills CLI
npx skills add https://github.com/azel-ko/yuque-publishing-skill

# Codex
mkdir -p ~/.codex/skills/yuque-publishing
cp -a skills/yuque-publishing/. ~/.codex/skills/yuque-publishing/

# Claude Code
mkdir -p ~/.claude/skills/yuque-publishing
cp -a skills/yuque-publishing/. ~/.claude/skills/yuque-publishing/
```

2. Restart Codex or Claude Code.

3. In chat, ask the agent to use the skill. For Claude Code, you can invoke it directly:

```text
/yuque-publishing
```

4. Provide the article content or file path in chat, plus the target Yuque space if it is not the default. The skill will choose the auth flow, run a dry-run first, and only write after you confirm the create/update action.

## Install

### Codex: Install from GitHub

Use Codex's skill installer:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo azel-ko/yuque-publishing-skill \
  --path skills/yuque-publishing
```

Restart Codex after installation so the new skill is discovered.

### Agent Skills CLI

For Claude Code, Cursor, and other compatible Agent Skills clients:

```bash
npx skills add https://github.com/azel-ko/yuque-publishing-skill
```

### Codex: Manual Local Install

If you already cloned this repository:

```bash
mkdir -p ~/.codex/skills/yuque-publishing
cp -a skills/yuque-publishing/. ~/.codex/skills/yuque-publishing/
```

Then restart Codex.

### Claude Code CLI: Personal Install

Claude Code skills live at `~/.claude/skills/<skill-name>/SKILL.md` for personal use. Official docs: https://code.claude.com/docs/en/skills

If you already cloned this repository:

```bash
mkdir -p ~/.claude/skills/yuque-publishing
cp -a skills/yuque-publishing/. ~/.claude/skills/yuque-publishing/
```

Start or restart Claude Code, then invoke the skill directly:

```text
/yuque-publishing
```

Inside Claude Code, the skill can reference bundled scripts through `${CLAUDE_SKILL_DIR}`. The included `yuque_auth.py select` helper also prints resolved script paths for the current installation, so the generated commands work even when Claude is running from another project directory.

The examples below use the Codex install path. In Claude Code, either run the selector first or replace `~/.codex/skills/yuque-publishing` with `${CLAUDE_SKILL_DIR}` inside an invoked skill.

Project-level install is also supported:

```bash
mkdir -p .claude/skills/yuque-publishing
cp -a skills/yuque-publishing/. .claude/skills/yuque-publishing/
```

## Authentication Choices

Choose one authentication mode before publishing. Current feature recommendation: choose cookie/session mode when you need the most complete workflow, including headless/background publishing and left-catalog insertion. Choose Open API Token when you want the most conservative official route and can accept the current catalog-placement limitation.

| Mode | Who should use it | Permission level | Notes |
|---|---|---:|---|
| Official OAuth / app authorization or Open API token | Users who can use Yuque's official developer auth, often paid or Super Member accounts | Scoped when Yuque supports scopes | Official and stable, but currently not the most complete route because catalog placement is not confirmed in the public Open API path used here. |
| Browser session automation | Non-Super Member users who can log in in a browser and accept a visible guided UI flow | Same as the logged-in browser session | Uses an isolated browser profile and operates the Yuque UI without exporting cookies. It can also call Yuque's internal catalog API after login. |
| Cookie/session background publishing **(Recommended: full feature set)** | Non-Super Member users who explicitly accept the risk and want silent writes after login | Maximum account-level permission | Most complete current route: headless/background publishing plus left-catalog insertion. Highest risk: session credentials usually act like full login credentials. Uses only the isolated skill profile, runs create/preflight headless by default, and requires `--i-understand-session-risk` for live writes. |

The repository ships separate helpers for each path:

- `yuque_auth.py`: choose an auth mode and print the right next commands.
- `yuque_publish.py`: Open API token mode.
- `yuque_browser.py`: browser-session UI mode; does not export cookies.
- `yuque_session.py`: cookie/session mode for explicit background/headless publishing.

Run the selector before publishing:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_auth.py select
```

Non-interactive example:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_auth.py select \
  --mode session \
  --title "Article Title" \
  --file article.md
```

## Get a Yuque Token or Official Auth

Yuque Open API requires token authentication. The token is sent in the `X-Auth-Token` HTTP header. Official docs:

- https://www.yuque.com/yuque/developer/api
- https://www.yuque.com/yuque/developer/openapi

If your account can create tokens:

1. Log in to Yuque.
2. Open the token settings page: https://www.yuque.com/settings/tokens
3. Create a new token.
4. Grant the token the minimum permissions needed to read/write the target knowledge base.
5. Copy the token once and store it in your local shell or secret manager.
6. If a token is ever pasted into chat, logs, or a repository, revoke it and create a new one.

Do not commit the token. Do not paste it into Codex or Claude Code chat.

If your account cannot create a token, choose either Browser session automation or Cookie/session extraction from the authentication choices above. Cookie/session is the recommended route for the most complete current feature set; choose Browser session automation when you prefer a visible guided flow and do not need silent/headless publishing.

## Configure Authentication

Set the token in your shell:

```bash
export YUQUE_TOKEN="REDACTED"
```

Optional settings:

```bash
export YUQUE_BASE_URL="https://www.yuque.com/api/v2"
export YUQUE_USER_AGENT="codex-yuque-publishing-skill/0.1"
```

## Browser Dependencies

Browser-based modes require Playwright:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

If system Chrome is already installed, the helpers will try it before Playwright's bundled Chromium. You can also set:

```bash
export YUQUE_BROWSER_EXECUTABLE="/usr/bin/google-chrome"
```

If the Google Chrome window opens and immediately closes, the command is probably running without an interactive stdin. In that case the login helper now keeps the browser open for 30 minutes by default. Use `--keep-open-seconds 0` to keep it open until the command is stopped:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py login \
  --space-url https://www.yuque.com/azel/zob9yu \
  --keep-open-seconds 0
```

## Open API Token Usage

Run a preflight check:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  preflight \
  --namespace azel/zob9yu
```

Create a dry-run payload:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  create-doc \
  --namespace azel/zob9yu \
  --title "Article Title" \
  --slug article-title \
  --file article.md
```

Publish after inspecting the dry-run:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  create-doc \
  --namespace azel/zob9yu \
  --title "Article Title" \
  --slug article-title \
  --file article.md \
  --execute
```

Update an existing document through the Open API token mode:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  update-doc \
  --namespace azel/zob9yu \
  --doc article-title \
  --title "Article Title" \
  --file article.md \
  --execute
```

Open API token mode intentionally stays on Yuque's documented Open API path. The current helper does not use private web routes in token mode, and the public Open API surface used here has no confirmed supported endpoint for placing a document into the left catalog/sidebar. If a token-created document does not appear in the left catalog, place it manually in Yuque or use the browser-session/cookie-session `add-to-catalog` command after explicitly accepting the internal web API risk.

## Browser Session Usage

Use this mode when you cannot create a Yuque API token but can log in in a browser.
It has the full Yuque permissions of the logged-in account. The dedicated profile only limits local exposure to this skill's profile directory.
This mode is visible UI automation. Use it when you are willing to see and operate the Yuque browser window.

Log in with an isolated profile:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py login \
  --space-url https://www.yuque.com/azel/zob9yu
```

If Yuque verification fails in the new profile, switch to another official login path in the same browser window, such as WeChat or DingTalk app QR-code login. The session still stays inside the dedicated profile, and the skill does not need to read passwords, cookies, or session values.

Dry-run a guided UI publish:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "Article Title" \
  --file article.md
```

Run the guided UI flow:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "Article Title" \
  --file article.md \
  --execute
```

The script opens Yuque, asks you to create/open a blank editor, then fills the title and body. You still review and save/publish in the browser.

After login, browser-session mode can also add an existing document id to the left catalog without exporting cookies. This uses Yuque's internal web API (`/api/docs/add_to_catalog`), not the official Open API, so it may change when Yuque changes its frontend:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py add-to-catalog \
  --space-url https://www.yuque.com/azel/zob9yu \
  --doc-id 123456
```

Execute only after inspecting the dry-run:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_browser.py add-to-catalog \
  --space-url https://www.yuque.com/azel/zob9yu \
  --doc-id 123456 \
  --headless \
  --execute \
  --i-understand-session-risk
```

By default the command uses `action=prependChild` and `target_node_uuid=null`, which asks Yuque to insert the document into the default/root catalog location. Pass `--target-node-uuid` only after you have identified the intended catalog node.

## Cookie/Session Usage

Use this when you want background publishing after the isolated profile is already logged in and you explicitly accept that session credentials usually have full account permissions.
The dedicated profile reduces local blast radius only; it does not reduce Yuque-side permissions.
Document creation runs headless by default, so it does not open a Google Chrome window. Pass `--no-headless` only when debugging.

Log in with the same isolated profile:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py login \
  --space-url https://www.yuque.com/azel/zob9yu
```

Inspect login state without printing cookies:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py preflight \
  --space-url https://www.yuque.com/azel/zob9yu \
  --headless
```

Dry-run the web-session create request:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "Article Title" \
  --slug article-title \
  --file article.md
```

Execute only with explicit risk acknowledgement:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "Article Title" \
  --slug article-title \
  --file article.md \
  --headless \
  --execute \
  --i-understand-session-risk
```

Create and add the new document to the left catalog in one session flow:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py create-doc \
  --space-url https://www.yuque.com/azel/zob9yu \
  --title "Article Title" \
  --slug article-title \
  --file article.md \
  --add-to-catalog \
  --headless \
  --execute \
  --i-understand-session-risk
```

Add an existing document id to the left catalog:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py add-to-catalog \
  --space-url https://www.yuque.com/azel/zob9yu \
  --doc-id 123456
```

Then execute after inspecting the dry-run:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py add-to-catalog \
  --space-url https://www.yuque.com/azel/zob9yu \
  --doc-id 123456 \
  --headless \
  --execute \
  --i-understand-session-risk
```

The default document endpoint is `/api/docs`; the default catalog endpoint is `/api/docs/add_to_catalog`. Both are Yuque web endpoints and may change; use `--endpoint`, `--catalog-endpoint`, and `--book-id` if needed.

## Default Destination

The skill includes Azel's default Yuque publishing preference:

- Knowledge base: `AI Native Engineering`
- Namespace: `azel/zob9yu`
- URL: https://www.yuque.com/azel/zob9yu

Directory mapping is documented in `skills/yuque-publishing/references/publishing-policy.md`.

## Security Notes

- `YUQUE_TOKEN` is read only from the runtime environment.
- Write commands are dry-run by default.
- `--execute` is required for live writes.
- Tokens are redacted from helper-script error output.
- `.env` files are ignored by this repository.
- CI should inject `YUQUE_TOKEN` as a protected secret.
- Cookie/session mode has the broadest permissions. It is the recommended full-feature route, but it should never run live writes without explicit `--execute` and `--i-understand-session-risk`.
- Dedicated browser profiles do not reduce Yuque account permissions; they only reduce local exposure compared with reading your main browser profile.
- Browser session automation should use an isolated browser profile and should not export cookies unless the user explicitly asks for that risk.
- Catalog insertion uses Yuque's internal web endpoint in session modes only; it is not a guaranteed official Open API feature.
- The default isolated browser profile is `~/.local/share/yuque-publishing/browser-profile`.
