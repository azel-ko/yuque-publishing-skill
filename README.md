# Yuque Publishing Skill

English | [中文](README.zh-CN.md)

Codex skill for preparing, dry-running, publishing, and updating Yuque articles with safe token handling.

## What It Does

- Turns drafts, notes, and technical articles into structured Yuque pages.
- Uses Yuque Open API with `X-Auth-Token` authentication.
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
| Browser session automation | Non-Super Member users who can log in in a browser but cannot create an API token | Same as the logged-in browser session | Safer fallback than extracting cookies. The automation should use an isolated browser profile and operate the Yuque UI without exporting cookies. |
| Cookie/session extraction | Non-Super Member users who explicitly accept the risk | Maximum account-level permission | Highest risk. Cookies usually act like full login credentials. Use only as an explicit advanced fallback; never print, commit, or share session values. |

This repository currently documents all three choices, but the shipped helper script implements only the Open API token mode. Browser-based modes should be added as separate explicit commands so users can opt in intentionally.

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

## Usage

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

Update an existing document:

```bash
python3 ~/.codex/skills/yuque-publishing/scripts/yuque_publish.py \
  update-doc \
  --namespace azel/zob9yu \
  --doc article-title \
  --title "Article Title" \
  --file article.md \
  --execute
```

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
- Browser session automation should use an isolated browser profile and should not export cookies unless the user explicitly asks for that risk.
