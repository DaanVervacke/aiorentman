# Security policy

## Supported versions

Only the latest release line receives security fixes.

## Reporting a vulnerability

Report vulnerabilities privately through [GitHub security advisories](https://github.com/DaanVervacke/aiorentman/security/advisories/new).
Do not open a public issue for a vulnerability.

You will get a response within a week. Include reproduction steps and affected versions where you can.

## Scope

This library talks to the Rentman API with a token you own. Treat the token as a secret: it grants read access to your entire inventory, planning, and pricing data.

Never commit tokens or captured response payloads that contain real asset identifiers, customer references, or addresses. The `.env` file and the `captures/` directory are git-ignored for exactly this reason.
