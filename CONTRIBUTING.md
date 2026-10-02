# Contributing

Changes go through pull requests. Every pull request carries exactly one label from the release categories: breaking-change, new-feature, enhancement, bugfix, maintenance, documentation, dependencies.

## Setup

```bash
uv sync
uv run python -m scripts.check
```

`uv run python -m scripts.check` is the canonical gate. It stops at the first failure and runs exactly:

```text
ruff format --check .
ruff check .
mypy src tests scripts
coverage run -m pytest
coverage report
uv build
uv audit
```

Coverage measures branches in `src/` and requires `fail_under = 98`. `uv audit` needs network access.

## Adding an endpoint

Add all of the following:

- A frozen `Endpoint` row in `src/aiorentman/_endpoints.py` with the complete wire contract and its response schema name.
- A typed `RentmanClient` method.
- The contract test passing against the pinned OpenAPI document in `tests/fixtures/rentman_oas_1.16.0.json`, including the model field coverage for a new resource.
- A fixture under `tests/fixtures/` with a real or redacted payload. Do not guess fixture shapes: capture one from the live API with `scripts/capture_data.py` and redact it with `scripts/_redact.py` before committing.
- A conventional commit, whose subject becomes the changelog entry.

## Changelog

`CHANGELOG.md` is generated with git-cliff from conventional commit subjects. Never edit it by hand. `feat:` and `fix:` subjects become the changelog entries and every other type is left out. Regenerate with `git-cliff --output CHANGELOG.md` after committing.

## Captures and confidential data

Raw captures stay in `captures/`, which is git-ignored. Only redacted fixtures are committed. Equipment names, serial numbers, QR and RFID codes, addresses, and free-text remarks are company data: the redaction pipeline replaces them with deterministic synthetic values so relationships inside one payload survive.

## Design decisions

The library is a pure API port. Domain logic such as the RFID tag index and availability windows belongs to the consuming application, not here. Request pacing lives in the transport because the documented limits are easy to trip during a bulk sync. The pinned OpenAPI document is the only contract: there is no scheduled upstream check, so re-run the contract test and refresh the pin when Rentman deploys changes.

## Test and repository rules

- Pytest uses `asyncio_mode = auto`. Warnings are errors except the configured resource warnings.
- Ruff uses `select = ["ALL"]` with the documented ignore list in `pyproject.toml`. mypy runs in strict mode.
- Do not add narrative code comments. Docstrings document the public API.
- Never log tokens or Authorization headers.
- Run a text-quality pass over all user-facing text before committing: README, CHANGELOG entries, docstrings, and error messages. No em dashes, no semicolon-joined clauses, no filler transitions.
- Do not mention AI, agents, or tooling in commit messages.
