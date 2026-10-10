# Contributing

Changes go through pull requests. Every pull request carries exactly one label from the release categories: breaking-change, new-feature, enhancement, bugfix, maintenance, documentation, dependencies.

## Setup

Use Python >= 3.14 and uv >= 0.12.21 and < 0.13. `pyproject.toml` pins the uv range, so `uv sync` refuses other versions.

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
sphinx-build -W -q docs docs/_build/html
uv build
uv audit --locked --preview-features audit-command
```

Coverage measures branches in `src/` plus `scripts/generate.py` and `scripts/resources.py`, and requires `fail_under = 98`. `sphinx-build` runs with the `docs` dependency group through `uv run --group docs`. `uv audit` and the docs build need network access.

## Adding an endpoint

`models.py`, `parsers.py`, `_endpoints.py`, and `client.py` in `src/aiorentman/` are generated. Do not edit them by hand. The generator reads the pinned OpenAPI document in `tests/fixtures/rentman_oas_1.16.0.json` and the resource table in `scripts/resources.py`, and `tests/test_generated.py` fails when a committed module differs from its output. The hand-written plumbing lives in `_base.py`, `_fields.py`, `_endpoint_types.py`, and `_core.py`.

Add all of the following:

- An `EndpointSpec` row in `scripts/resources.py` with the endpoint constant name, the kind, the schema path, the client method name without its `async_` and verb prefix, its id parameter, and its docstrings. A new resource also needs a `ModelSpec` row, and a write endpoint with a new request schema needs a `PAYLOADS` entry and a payload class in `payloads.py`. Import every new model or payload class in `src/aiorentman/__init__.py` and add it to `__all__`, since that module is not generated.
- The regenerated modules from `uv run python -m scripts.generate`.
- The contract test passing against the pinned OpenAPI document, including the model field coverage for a new resource.
- A fixture under `tests/fixtures/` with a real payload, redacted. Do not guess fixture shapes: add the path to `COLLECTIONS` or `LINKED_COLLECTIONS` in `scripts/capture_data.py`, capture one from the live API with that script and redact it with `scripts/_redact.py` before committing. Register the redacted file in `PARSERS` or `WRITE_PARSERS` in `tests/test_real_payloads.py`, and in `EMPTY_CAPTURES` when it has no items. The test suite fails on any redacted file that is not registered.
- The new client methods in the README tables, and every new model or payload class in `docs/api.rst`. Neither is generated or tested.
- A conventional commit, whose subject becomes the changelog entry.

## Changelog

`CHANGELOG.md` is generated with git-cliff from conventional commit subjects. Never edit it by hand. `feat:`, `fix:`, `docs:`, and `chore:` subjects become the changelog entries and every other type is left out unless it is marked breaking. The changelog skips `chore: release`, `chore: regenerate the changelog`, and `chore: update the changelog` subjects. Mark a breaking change with `!` after the type, as in `feat!:`. Those commits land under Breaking Changes. The text `BREAKING CHANGE` inside the commit body also moves a commit of any type there. Do not rely on a `BREAKING CHANGE:` footer as the marker, since `cliff.toml` matches only the body. Regenerate with `git-cliff --output CHANGELOG.md` after committing.

At release, bump the version with `uv version X.Y.Z` and run `git-cliff --tag vX.Y.Z --output CHANGELOG.md`. That renders the Unreleased section under the new version heading with its compare link. Commit `pyproject.toml`, `uv.lock`, and `CHANGELOG.md` with a `chore: release X.Y.Z` subject, which the changelog skips, and tag that commit `vX.Y.Z`. Push the commit and the tag, then publish the GitHub release on that tag. Publishing triggers `.github/workflows/release.yml`, which runs the check gate, fails when the tag differs from the `pyproject.toml` version, and otherwise uploads to PyPI. Release Drafter proposes a version from the PR labels, so check that the draft uses the tag you pushed.

## Validating writes

The check gate never calls the live API. After changing the write surface, run `uv run python -m scripts.validate_writes` against a scratch account. It creates one task and one subtask, updates the task, deletes both, and probes one invalid body. It records the create and update responses into `captures/`. The token comes from a `RENTMAN_TOKEN` line in `.env` in the working directory, then in `.env` at the repository root, and only then from the environment, so a `.env` token wins over an exported one.

## Captures and confidential data

Raw captures stay in `captures/`, which is git-ignored. Only redacted fixtures are committed. Equipment names, serial numbers, QR and RFID codes, addresses, and free-text remarks are company data: the redaction pipeline replaces them with deterministic synthetic values so relationships inside one payload survive.

## Design decisions

The library is a pure API port. Domain logic such as the RFID tag index and availability windows belongs to the consuming application, not here. Request pacing lives in the client because the documented limits are easy to trip during a bulk sync. The pinned OpenAPI document is the only contract: there is no scheduled upstream check, so re-run the contract test and refresh the pin when Rentman deploys changes.

## Test and repository rules

- Pytest uses `asyncio_mode = auto`. Warnings are errors except the configured resource warnings.
- Ruff uses `select = ["ALL"]` with the documented ignore list in `pyproject.toml`. mypy runs in strict mode.
- Do not add narrative code comments. Docstrings document the public API.
- Never log tokens or Authorization headers.
- Run a text-quality pass over all user-facing text before committing: README, CHANGELOG entries, docstrings, and error messages. No em dashes, no semicolon-joined clauses, no filler transitions.
- Do not mention AI, agents, or tooling in commit messages.
