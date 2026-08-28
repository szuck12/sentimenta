# Security Policy

## Scope

Sentimenta is a stateless emotion-analysis application. It receives text via
an HTTP request, runs inference through a locally loaded transformer model,
and returns structured results. **No user text is stored, logged to disk, or
persisted in any form.** There is no database, no user accounts, and no
authentication layer.

The application holds no secrets or API keys at runtime. All configuration is
sourced from environment variables that never leave the host.

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | Yes (current)      |
| < 0.1   | No                 |

## Reporting a Vulnerability

If you discover a security issue, please report it responsibly:

1. **GitHub Private Security Advisory** (preferred): Use the "Report a
   vulnerability" button on the Security tab of the repository.
2. **Email**: Contact the maintainers at the address listed in the repository
   owner's GitHub profile.

Please include:
- A description of the vulnerability and its potential impact.
- Steps to reproduce the issue.
- Any suggested fix, if applicable.

## Disclosure

We aim to acknowledge reports within 72 hours. Confirmed vulnerabilities will
be fixed in a patch release and disclosed through GitHub's advisory mechanism.
We request that reporters refrain from public disclosure until a fix is
available.

## Security Best Practices

- Run the application behind a reverse proxy in production.
- Restrict CORS origins to trusted domains.
- Keep dependencies updated (`pip-audit`, `npm audit`).
- Never expose the development server (port 8000) to an untrusted network.
