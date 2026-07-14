# Authentication

Use Yuque Open API token authentication. The public Yuque developer page states that Open API access requires token verification and that requests pass the token in the `X-Auth-Token` HTTP header.

Official source to re-check when behavior changes:

- `https://www.yuque.com/yuque/developer/api`
- `https://www.yuque.com/yuque/developer/openapi`

## Supported credential model

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
- Avoid browser cookies and private web endpoints for open-source automation.
- Prefer official Open API endpoints over scraped web routes.
- Ask the user to rotate any token pasted into chat before using it.
- Treat external publishing as a side effect: confirm target namespace, title, and create/update intent before passing `--execute`.

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

Do not implement OAuth unless the user explicitly chooses that product path and the official Yuque docs for OAuth are available. For this skill's first version, token authentication is simpler, auditable, and compatible with non-interactive Codex sessions.
