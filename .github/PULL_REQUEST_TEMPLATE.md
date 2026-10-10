- [ ] `uv run python -m scripts.check` passes completely.
- [ ] The PR carries one of the seven labels: `breaking-change`, `new-feature`, `enhancement`, `bugfix`, `maintenance`, `documentation`, `dependencies`.
- [ ] Every commit subject is a conventional commit, with `!` after the type for a breaking change.

For endpoint changes, all of the following are present:

- [ ] An `EndpointSpec` row in `scripts/resources.py`, plus a `ModelSpec` row for a new resource and a `PAYLOADS` entry plus a payload class in `src/aiorentman/payloads.py` for a new request schema.
- [ ] The modules regenerated with `uv run python -m scripts.generate`, with no hand edits to the generated files.
- [ ] The contract test passes against the pinned OpenAPI document in `tests/fixtures/rentman_oas_1.16.0.json`.
- [ ] A captured real payload under `tests/fixtures/`, redacted with `scripts/_redact.py` and registered in `tests/test_real_payloads.py`.
- [ ] Every new model or payload class imported in `src/aiorentman/__init__.py` and listed in `__all__`.
- [ ] The new client methods in the README tables, and every new model or payload class in `docs/api.rst`.
- [ ] A conventional commit subject, which git-cliff renders into `CHANGELOG.md`.
