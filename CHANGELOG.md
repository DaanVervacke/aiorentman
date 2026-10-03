# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Before 1.0, breaking changes ship as minor bumps.

## [Unreleased]

### Bug Fixes

- Degrade on unconvertible id strings in the parser
- Reject reserved and generated names on filters and sorts
- Fail closed on malformed and repeated collection cursors
- Carry the request target and Retry-After in transport errors
- Accept null location details on invitations

### Documentation

- Match the shipped write surface and changelog groups

### Maintenance

- Prune dead fixtures and tighten tooling pins

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
- Update the changelog
- Update the changelog
- Update the changelog
- Update the changelog
- Update the changelog
- Update the changelog

## [0.1.0] - 2026-10-01

### Features

- Create the aiorentman library

