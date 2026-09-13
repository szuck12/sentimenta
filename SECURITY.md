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
| 1.0.x   | Yes (current)      |
| < 1.0   | No                 |

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
