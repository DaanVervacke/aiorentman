# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Before 1.0, breaking changes ship as minor bumps.

## [Unreleased]

### Breaking Changes

- Name single-item task and file getters in the singular

### Bug Fixes

- Degrade on unconvertible id strings in the parser
- Reject reserved and generated names on filters and sorts
- Fail closed on malformed and repeated collection cursors
- Carry the request target and Retry-After in transport errors
- Accept null location details on invitations
- Make result models hashable
- Create no session when the pacing arguments are invalid
- Drop objects without a usable id instead of numbering them 0
- Name partial parsers in the drop log

### Documentation

- Match the shipped write surface and changelog groups
- Document client options, the error hierarchy, and retry_after
- Correct the scope, validation, and token claims in the guides
- Align the release procedure and token scope with the tooling
- Describe dropped objects, item_count, and pacing errors
- Document the generator and mark the generated modules
- Point the PR checklist at the resource table

### Features

- List files, invoice lines, and tasks of one contract

### Maintenance

- Prune dead fixtures and tighten tooling pins
- Skip legacy changelog regen commits
- Align the changelog tooling with the library family
- Group breaking changes in the changelog
- Build the docs in the check gate
- Generate the models and parsers from the pinned schema
- Generate the endpoint catalog and client from the table
- Validate the resource table and test the generator

## [0.2.1] - 2026-10-02

### Maintenance

- Complete the uv toolchain migration
- Let the label verifier read pull requests
- Drop the malformed release drafter category
- Sync repository labels and migrate the release drafter config
- Render documentation and maintenance entries in the changelog

## [0.2.0] - 2026-10-02

### Features

- Validate against the live API and add redacted fixtures
- Add the equipment adjacent resources
- Add the project planning resources
- Add the financial resources
- Add the subrental and purchase order resources
- Add the crew, time, and contact resources
- Add the task, file, and rate resources
- Add the write surface

### Maintenance

- Generate the changelog with git-cliff

## [0.1.0] - 2026-10-01

### Features

- Create the aiorentman library

[Unreleased]: https://github.com/DaanVervacke/aiorentman/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/DaanVervacke/aiorentman/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/DaanVervacke/aiorentman/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/DaanVervacke/aiorentman/releases/tag/v0.1.0

