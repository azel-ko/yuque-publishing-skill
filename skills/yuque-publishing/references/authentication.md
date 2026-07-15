# Authentication

Use Yuque Open API token authentication. The public Yuque developer page states that Open API access requires token verification and that requests pass the token in the `X-Auth-Token` HTTP header.

Official source to re-check when behavior changes:

- `https://www.yuque.com/yuque/developer/api`
- `https://www.yuque.com/yuque/developer/openapi`

## Authentication modes

Let the user choose one mode before publishing:

| Mode | Intended users | Permission level | Implementation rule |
|---|---|---:|---|
| Official OAuth / app authorization or Open API token | Users who can use Yuque developer auth, often paid or Super Member accounts | Prefer scoped credentials when available | Use official APIs. The current helper supports `X-Auth-Token`. |
| Browser session automation | Non-Super Member users who can log in through the browser and accept a visible guided UI flow | Same as browser login | Use an isolated browser profile and UI automation. Do not export cookies by default. It may call Yuque's internal catalog API only after login and dry-run. |
| Cookie/session background publishing | Non-Super Member users who explicitly accept the risk and want silent writes after login | Maximum account-level permission | Treat as full account credentials. Run create/preflight headless by default, never print values, and require explicit consent each time. It may call Yuque's internal catalog API when the user explicitly chooses this route. |

If official OAuth docs are available, prefer OAuth/app authorization over raw tokens. If official OAuth is not available, the Open API token mode remains the stable API path.

Dedicated browser profiles do not reduce Yuque account permissions. They only reduce local exposure compared with reading the user's main browser profile.

## Supported token model

Use a runtime environment variable:

```bash
export YUQUE_TOKEN="..."
```

The helper script reads:

- `YUQUE_TOKEN`: required for network requests.
- `YUQUE_BASE_URL`: optional, defaults to `https://www.yuque.com/api/v2`.
- `YUQUE_USER_AGENT`: optional, defaults to `codex-yuque-publishing-skill/0.1`.

## Rules

- Never commit, persist, or generate token files.
- Never add tokens to `SKILL.md`, references, examples, README files, shell history snippets, or test fixtures.
- Never print tokens. Redact tokens in errors and logs.
- Avoid browser cookies and private web endpoints for default Open API token automation.
- Prefer official Open API endpoints over scraped web routes.
- Use Yuque internal web endpoints only in browser-session or cookie/session mode, after dry-run, with explicit `--execute` and session-risk acknowledgement.
- Ask the user to rotate any token pasted into chat before using it.
- Treat external publishing as a side effect: confirm target namespace, title, and create/update intent before passing `--execute`.
- When the user explicitly chooses cookie/session mode, state that it has the broadest permissions and must be handled like a password.

## Local use

Recommended local flow:

```bash
export YUQUE_TOKEN="..."
python3 scripts/yuque_publish.py preflight --namespace azel/zob9yu
python3 scripts/yuque_publish.py create-doc --namespace azel/zob9yu --title "Title" --file article.md
python3 scripts/yuque_publish.py create-doc --namespace azel/zob9yu --title "Title" --file article.md --execute
```

Do not store the token in `.env` unless the user explicitly asks and the file is ignored. Even then, do not create or print the file contents.

## CI use

For GitHub Actions or other CI:

- Store `YUQUE_TOKEN` as a secret in the CI provider.
- Inject it only into the publish job environment.
- Keep pull-request jobs dry-run only unless the workflow is protected.
- Add secret scanning and block publishing from forks.

## OAuth and app-based auth

Do not implement OAuth unless the user explicitly chooses that product path and the official Yuque docs for OAuth are available. OAuth or app authorization is the preferred official path when Yuque supports it.

## Browser-based auth

Browser-based auth has two variants:

- Browser session automation: open a browser profile, let the user log in, and operate Yuque's UI without exporting raw cookies. Use this when visible browser work is acceptable.
- Cookie/session extraction: use only when the user explicitly chooses it and understands that the session usually has maximum account permissions. Use this for background/headless publishing after the isolated profile is already logged in. Do not print or export raw session values.

## Helper commands

Browser-session mode uses Playwright and stores login state in:

```text
~/.local/share/yuque-publishing/browser-profile
```

Install Playwright before using browser-based modes:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

If system Chrome is installed, the helpers try it before Playwright's bundled Chromium. Override with:

```bash
export YUQUE_BROWSER_EXECUTABLE="/usr/bin/google-chrome"
```

If the Chrome window opens and immediately closes, the helper is probably running without an interactive stdin. Login commands keep the browser open for 30 minutes by default in non-interactive runs; pass `--keep-open-seconds 0` to keep it open until the command is stopped. Guided `browser-session create-doc --execute` still requires an interactive terminal because it waits for manual editor focus steps. For silent background publishing, use `yuque_session.py create-doc --headless --execute --i-understand-session-risk`.

If Yuque verification fails in the new isolated profile, ask the user to try another official login path in the same browser window, such as WeChat or DingTalk app QR-code login. The session remains scoped to the dedicated profile, and the skill should still avoid reading passwords, cookies, or session values unless the user explicitly chooses cookie/session mode.

Choose a mode first:

```bash
python3 scripts/yuque_auth.py select
python3 "${CLAUDE_SKILL_DIR}/scripts/yuque_auth.py" select
python3 scripts/yuque_auth.py select --mode token
python3 scripts/yuque_auth.py select --mode browser
python3 scripts/yuque_auth.py select --mode session
```

In Claude Code CLI, prefer `${CLAUDE_SKILL_DIR}` when running bundled scripts. The selector prints resolved script paths for the active installation, so follow the generated commands after choosing a mode.

Browser-session flow:

```bash
python3 scripts/yuque_browser.py login --space-url https://www.yuque.com/azel/zob9yu
python3 scripts/yuque_browser.py create-doc --space-url https://www.yuque.com/azel/zob9yu --title "Title" --file article.md
python3 scripts/yuque_browser.py create-doc --space-url https://www.yuque.com/azel/zob9yu --title "Title" --file article.md --execute
python3 scripts/yuque_browser.py add-to-catalog --space-url https://www.yuque.com/azel/zob9yu --doc-id 123456
```

Cookie/session flow:

```bash
python3 scripts/yuque_session.py login --space-url https://www.yuque.com/azel/zob9yu
python3 scripts/yuque_session.py preflight --space-url https://www.yuque.com/azel/zob9yu --headless
python3 scripts/yuque_session.py create-doc --space-url https://www.yuque.com/azel/zob9yu --title "Title" --file article.md
python3 scripts/yuque_session.py create-doc --space-url https://www.yuque.com/azel/zob9yu --title "Title" --file article.md --headless --execute --i-understand-session-risk
python3 scripts/yuque_session.py create-doc --space-url https://www.yuque.com/azel/zob9yu --title "Title" --file article.md --add-to-catalog --headless --execute --i-understand-session-risk
python3 scripts/yuque_session.py add-to-catalog --space-url https://www.yuque.com/azel/zob9yu --doc-id 123456
```

The cookie/session helper defaults to `/api/docs` for document creation and `/api/docs/add_to_catalog` for catalog insertion. These are Yuque web endpoints that may change. If Yuque changes them, pass `--endpoint`, `--catalog-endpoint`, and `--book-id` explicitly after validating the current web request shape.
