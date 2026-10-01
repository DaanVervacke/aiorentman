# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Before 1.0, breaking changes ship as minor bumps.

## [Unreleased]

## [0.1.0] - 2026-10-01

### Added

- Read-only client for the Rentman API covering equipment, serial numbers, actual content, assigned serials, set content, folders, stock locations, warehouse statuses, statuses, stock movements, repairs, projects, subprojects, and project equipment, including the linked collections between them.
- Cursor pagination with raw page access through `RentmanPage` and async generators for every collection.
- A typed query object for the field selection, sorting, filtering, expansion, and paging parameters the API documents, with relational operator helpers.
- Client-side request pacing against the documented limits of 10 requests per second and 20 concurrent requests, configurable and disableable.
- Typed linked fields that parse either as an API path link or as the expanded model.
- A pinned OpenAPI 1.16.0 document as a committed fixture, with contract tests validating every endpoint and every model field against it.
