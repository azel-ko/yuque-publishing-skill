# Yuque Publishing Skill

English | [中文](README.zh-CN.md)

Codex skill for preparing, dry-running, publishing, and updating Yuque articles with safe token handling.

## What It Does

- Turns drafts, notes, and technical articles into structured Yuque pages.
- Uses Yuque Open API with `X-Auth-Token` authentication.
- Supports browser-session and explicit cookie/session fallback modes for users who cannot create API tokens.
- Keeps credentials out of the repository and out of skill files.
- Runs write operations as dry-runs by default.
- Requires explicit `--execute` before creating or updating Yuque documents.

## Install

### Install from GitHub

Use Codex's skill installer:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo azel-ko/yuque-publishing-skill \
  --path skills/yuque-publishing
```

Restart Codex after installation so the new skill is discovered.

### Manual Local Install

If you already cloned this repository:

```bash
cp -a skills/yuque-publishing ~/.codex/skills/yuque-publishing
```

Then restart Codex.

## Authentication Choices

Choose one authentication mode before publishing:

| Mode | Who should use it | Permission level | Notes |
|---|---|---:|---|
| Official OAuth / app authorization or Open API token | Users who can use Yuque's official developer auth, often paid or Super Member accounts | Scoped when Yuque supports scopes | Preferred and most stable. The included helper currently implements the Open API token path with `X-Auth-Token`. |
| Browser session automation | Non-Super Member users who can log in in a browser but cannot create an API token | Same as the logged-in browser session | Safer fallback than extracting cookies. Uses an isolated browser profile and operates the Yuque UI without exporting cookies. |
| Cookie/session extraction | Non-Super Member users who explicitly accept the risk | Maximum account-level permission | Highest risk. Cookies usually act like full login credentials. Uses only the isolated skill profile and requires `--i-understand-session-risk` for live writes. |

The repository ships separate helpers for each path:

- `yuque_auth.py`: choose an auth mode and print the right next commands.
- `yuque_publish.py`: Open API token mode.
- `yuque_browser.py`: browser-session UI mode; does not export cookies.
- `yuque_session.py`: cookie/session mode; explicit advanced fallback.

Run the selector before publishing:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_auth.py select
```

Non-interactive example:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_auth.py select \
  --mode browser \
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

Do not commit the token. Do not paste it into Codex chat.

If your account cannot create a token, choose either Browser session automation or Cookie/session extraction from the authentication choices above. Prefer Browser session automation because it can avoid exporting raw session credentials.

## Configure Authentication

Set the token in your shell:

```bash
export YUQUE_TOKEN="your-yuque-token"
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

## Browser Session Usage

Use this mode when you cannot create a Yuque API token but can log in in a browser.
It has the full Yuque permissions of the logged-in account. The dedicated profile only limits local exposure to this skill's profile directory.

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

## Cookie/Session Usage

Use this only when browser-session automation is not enough and you explicitly accept that session credentials usually have full account permissions.
The dedicated profile reduces local blast radius only; it does not reduce Yuque-side permissions.

Log in with the same isolated profile:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py login \
  --space-url https://www.yuque.com/azel/zob9yu
```

Inspect login state without printing cookies:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_session.py preflight \
  --space-url https://www.yuque.com/azel/zob9yu
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
  --execute \
  --i-understand-session-risk
```

The default session endpoint is `/api/docs`. It is a Yuque web endpoint and may change; use `--endpoint` and `--book-id` if needed.

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
- Cookie/session mode has the broadest permissions and should never be the default.
- Dedicated browser profiles do not reduce Yuque account permissions; they only reduce local exposure compared with reading your main browser profile.
- Browser session automation should use an isolated browser profile and should not export cookies unless the user explicitly asks for that risk.
- The default isolated browser profile is `~/.local/share/yuque-publishing/browser-profile`.
