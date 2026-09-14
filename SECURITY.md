# Security Policy

## Scope

Sentimenta is a stateless emotion-analysis application. It receives text via
an HTTP request, runs inference through a locally loaded transformer model,
and returns structured results. **No user text is stored, logged to disk, or
persisted in any form.** There is no database, no user accounts, and no
authentication layer.

The application holds no secrets or API keys at runtime. All configuration is
sourced from environment variables that never leave the host. The model
weights are downloaded once from the official Hugging Face Hub
(`SamLowe/roberta-base-go_emotions`) and cached locally; no third-party or
downloaded code is executed at runtime.

Input is bounded on two axes — a character limit (`SENTIMENTA_MAX_TEXT_CHARS`,
default 2000) enforced by the request schema, and a token budget (256 tokens)
applied before inference — which also limits resource-exhaustion and
denial-of-service attempts through oversized requests.

## Supported Versions

Only the latest release receives security fixes:

| Version | Supported          |
|---------|--------------------|
| 1.3.x   | Yes (current)      |
| < 1.3   | No                 |

## Reporting a Vulnerability

If you discover a security issue, please report it responsibly and privately:

1. **GitHub Private Security Advisory** (preferred): Use the "Report a
   vulnerability" button on the Security tab of the repository.
2. **Email**: Contact the maintainers at the address listed in the repository
   owner's GitHub profile.

Please include:
- A description of the vulnerability and its potential impact.
- Steps to reproduce the issue.
- Any suggested fix, if applicable.

What happens next:
- We aim to acknowledge reports within 72 hours.
- We assess the report and, where applicable, ship a fix in the next patch
  release.
- Public disclosure follows once a fix is available.

## Disclosure

We discuss security topics in general terms only across public artifacts
(documentation, changelog, and commit messages). Specific technical details
are handled privately between the reporter and the maintainer until a fix is
available. Please refrain from public disclosure before a fix ships.

## Security Best Practices

- Run the application behind a reverse proxy with TLS in production.
- Restrict CORS origins to trusted domains; never use a wildcard in
  production.
- Keep dependencies updated and scanned (`pip-audit` for Python,
  `npm audit` for Node). Weekly Dependabot checks are enabled.
- Pin dependency versions to avoid silently pulling compromised releases.
- Validate and bound all request bodies (character and token limits are
  enforced, but downstream proxies should also apply rate limits).
- Never expose the development server (port 8000) to an untrusted network.
- Return only sanitized error envelopes; internal exceptions must never
  reach clients (stack traces, file paths, or library messages).
- Run the backend container as a non-root user where the platform allows.
- Keep the `/api/health` endpoint available for monitoring but do not expose
  additional diagnostics publicly.
- Treat model outputs as estimates, not facts: adversarial or ambiguous
  input can produce misleading readings, and the application makes no
  security or factual guarantees about them.

## Dependency & Supply Chain

- Direct dependencies are **pinned to exact versions**, and both trees are
  scanned in CI on every push and pull request: `pip-audit` for Python and
  `npm audit --audit-level=high` for Node. The project currently reports
  **zero known vulnerabilities**.
- Weekly **Dependabot** updates cover pip, npm, and GitHub Actions.
- CI runs with a **read-only** `GITHUB_TOKEN`, actions are pinned to commit
  SHAs, and checkout credentials are not persisted.
- The model is loaded from an **immutable commit revision**
  (`SENTIMENTA_MODEL_REVISION`), only through **safetensors**, never
  through pickle-based weights or remote code (`trust_remote_code` is not
  enabled), and the weights are **SHA-256 verified** against
  `SENTIMENTA_MODEL_SHA256` on load.
- The API exposes no file-serving, form-upload, or static-file routes, which
  keeps large classes of framework advisories unreachable.

## Production Recommendations

- Set `SENTIMENTA_ENABLE_DOCS=false` to hide `/docs`, `/redoc`, and
  `/openapi.json` (the default).
- The app ships an in-process per-client rate limiter
  (`SENTIMENTA_RATE_LIMIT`) and a concurrency cap
  (`SENTIMENTA_MAX_CONCURRENT_REQUESTS`) as defense in depth, but you should
  still enforce rate limiting at the reverse proxy or hosting platform:
  model inference (especially token attribution) is CPU-intensive, and the
  API is intentionally unauthenticated.
- When running behind a reverse proxy, set `SENTIMENTA_TRUST_PROXY=true`
  **only** if the proxy overwrites `X-Forwarded-For`/`X-Real-IP`; otherwise
  clients can spoof their address and defeat rate limiting. Never enable it
  when the app is directly reachable.
- Keep `SENTIMENTA_MAX_BODY_BYTES` set so oversized bodies are rejected
  before they are buffered; also cap the body size at the proxy.
- Terminate TLS at a trusted proxy and forward only the required headers.
- Avoid logging request bodies; the application logs only aggregate
  metadata.
