# Yuque API Contract

The helper script uses conservative Yuque Open API assumptions that must be verified against the current official docs before production automation.

## Base URL

Default:

```text
https://www.yuque.com/api/v2
```

Override with `YUQUE_BASE_URL` for enterprise deployments or API changes.

## Headers

Use:

```text
X-Auth-Token: <token>
Content-Type: application/json
User-Agent: codex-yuque-publishing-skill/0.1
```

Never print the token header.

## Common endpoints

The script assumes these common Open API shapes:

- `GET /user`: authenticate and identify the current user.
- `GET /repos/{namespace}`: fetch a knowledge base.
- `POST /repos/{namespace}/docs`: create a document.
- `PUT /repos/{namespace}/docs/{doc}`: update a document by id or slug, depending on API support.

Where `namespace` is a user/group plus book slug, for example `azel/zob9yu`.

## Payload

Create/update payload fields:

```json
{
  "title": "Article title",
  "slug": "optional-slug",
  "body": "Markdown or HTML body",
  "format": "markdown",
  "public": 1
}
```

Use `format=markdown` unless the user explicitly requests HTML or the existing page requires another format.

## Catalog placement

Directory or catalog placement may require a separate API from document creation.

The Open API token helper must stay conservative:

1. Publish to the correct knowledge base.
2. Report the intended directory.
3. State that the current official Open API path used by this helper has no confirmed supported catalog-placement endpoint.
4. Ask whether to place the page manually or use the session-based internal web API path.

## Session internal catalog API

Browser-session and cookie/session helpers may use Yuque's web endpoint only when the user explicitly chooses a session route:

```text
POST /api/docs/add_to_catalog
```

Observed payload shape:

```json
{
  "ids": [123456],
  "book_id": 123,
  "target_node_uuid": null,
  "action": "prependChild"
}
```

Treat this as an internal frontend API, not a stable Open API contract. Keep it dry-run first, require explicit `--execute`, and require `--i-understand-session-risk` for live writes. Omit `target_node_uuid` to insert at Yuque's default/root catalog location; pass it only after the target catalog node is known.

## Failure handling

- `401` or `403`: token missing, invalid, expired, or lacks permission.
- `404`: namespace or document does not exist, or token lacks visibility.
- `409` or validation error: slug conflict or invalid payload.
- `429`: back off and do not retry aggressively.

On errors, show status code and safe response summary only. Do not show raw request headers.
