# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure (Phase 1)
- Core infrastructure modules (Phase 1)
  - HTTP client with retry logic and rate limiting
  - OAuth2 authentication with token caching
  - Configuration management (TOML, env vars)
  - Exception hierarchy (15+ custom exceptions)
  - Base models and utilities (Pydantic)
  - Pagination utilities for cursor-based pagination
- Testing framework setup (Phase 1)
  - 20 core infrastructure unit tests
- **Endpoint API implementation (Phase 2)**
  - Complete data models for endpoints (15+ Pydantic models)
  - EndpointAPI client with 12 methods
  - Endpoint management (list, get, update, delete)
  - Advanced filtering with EndpointFilters
  - Endpoint actions (scan, isolate, unisolate)
  - Tamper protection operations (get, update, get password)
  - Pagination support with async iterators
  - 26 comprehensive unit tests for Endpoint API
  - Test coverage: 87-92% for Endpoint API modules

### Documentation
- Comprehensive planning documents
- Technical specification with dual interface (async+sync) architecture
- Architecture diagrams
- API coverage matrix
- Sync implementation guide
- Development workflow guide

[Unreleased]: https://github.com/yourusername/pysophoscentralapi/commits/main

