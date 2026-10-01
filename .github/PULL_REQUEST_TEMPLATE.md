- [ ] `uv run python -m scripts.check` passes completely.
- [ ] The PR carries one of the seven labels: `breaking-change`, `new-feature`, `enhancement`, `bugfix`, `maintenance`, `documentation`, `dependencies`.
- [ ] There is a `[Unreleased]` entry in `CHANGELOG.md`.

For endpoint changes, all of the following are present:

- [ ] A frozen `Endpoint` row in `src/aiorentman/_endpoints.py` with the complete wire contract and its response schema name.
- [ ] A typed `RentmanClient` method.
- [ ] The contract test passes against the pinned OpenAPI document in `tests/fixtures/rentman_oas_1.16.0.json`.
- [ ] A captured real payload under `tests/fixtures/`, redacted with `scripts/_redact.py`.
- [ ] An entry under `[Unreleased]` in `CHANGELOG.md`.
