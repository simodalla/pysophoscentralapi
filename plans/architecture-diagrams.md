# PySophosCentralApi - Architecture Diagrams

This document provides visual representations of the system architecture, data flows, and component interactions.

---

## 0. Dual Interface Architecture (Async + Sync)

```
┌─────────────────────────────────────────────────────────┐
│                    User Code                             │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Async Interface │         │  Sync Interface   │     │
│  │  (async/await)   │         │  (blocking)       │     │
│  └────────┬─────────┘         └────────┬─────────┘     │
│           │                             │               │
└───────────┼─────────────────────────────┼───────────────┘
            │                             │
            │                             │ asyncio.run()
            ▼                             ▼
┌───────────────────────────┐  ┌─────────────────────────┐
│   Async Implementation    │◄─│    Sync Wrappers        │
│   (Primary)               │  │    (Thin Layer)         │
│                           │  │                         │
│  ├─ HTTPClient (async)    │  │  ├─ HTTPClientSync      │
│  ├─ AuthProvider (async)  │  │  ├─ AuthProviderSync   │
│  ├─ Paginator (async)     │  │  ├─ PaginatorSync      │
│  └─ API Clients (async)   │  │  └─ API ClientsSync    │
└───────────┬───────────────┘  └─────────────────────────┘
            │
            │ All share same
            ▼
┌─────────────────────────────────────────────────────────┐
│              Shared Components                           │
│  - Configuration (pydantic models)                       │
│  - Exceptions (all sync)                                 │
│  - Data Models (pydantic - sync)                         │
└─────────────────────────────────────────────────────────┘

Usage Patterns:
───────────────
Async (concurrent):     Sync (sequential):
  async with client:      with client_sync:
    await client.get()      client.get()
    await client.post()     client.post()
```

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          End User / Developer                       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
        ┌───────▼────────┐     ┌───────▼────────┐
        │  CLI Interface │     │  Python Library│
        │   (click + rich)│     │  (direct import)│
        └───────┬────────┘     └───────┬────────┘
                │                       │
                └───────────┬───────────┘
                            │
                  ┌─────────▼──────────┐
                  │   API Client Layer  │
                  │  - Endpoint API     │
                  │  - Common API       │
                  └─────────┬──────────┘
                            │
                  ┌─────────▼──────────┐
                  │  Core Infrastructure│
                  │  - HTTP Client      │
                  │  - Auth Manager     │
                  │  - Config Loader    │
                  └─────────┬──────────┘
                            │
                            │ HTTPS
                            │
              ┌─────────────▼──────────────┐
              │   Sophos Central APIs      │
              │  - Endpoint API v1         │
              │  - Common API v1           │
              │  - OAuth2 Token Service    │
              └────────────────────────────┘
```

---

## 2. Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                          │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   CLI Commands        │      │   Export Formatters  │        │
│  │   - click groups      │      │   - JSON             │        │
│  │   - rich output       │      │   - CSV              │        │
│  │   - colorama          │      │   - Table            │        │
│  └──────────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                        │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   Command Handlers    │      │   Data Processors    │        │
│  │   - Validation        │      │   - Filtering        │        │
│  │   - Orchestration     │      │   - Sorting          │        │
│  │   - Error handling    │      │   - Aggregation      │        │
│  └──────────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     API Client Layer                            │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   Endpoint API        │      │   Common API         │        │
│  │   - Endpoints         │      │   - Alerts           │        │
│  │   - Scans             │      │   - Tenants          │        │
│  │   - Isolation         │      │   - Admins           │        │
│  │   - Tamper Protection │      │   - Roles            │        │
│  │   - Settings          │      │   - Users            │        │
│  └──────────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                  Core Infrastructure Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐           │
│  │ HTTPClient  │  │ AuthProvider│  │ Config Loader│           │
│  │ - httpx     │  │ - OAuth2    │  │ - TOML       │           │
│  │ - Retry     │  │ - Tokens    │  │ - Env Vars   │           │
│  │ - Rate Limit│  │ - Refresh   │  │ - Validation │           │
│  └─────────────┘  └─────────────┘  └──────────────┘           │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐           │
│  │ Pagination  │  │  Exceptions │  │ Data Models  │           │
│  │ - Cursor    │  │  - Hierarchy│  │  - Pydantic  │           │
│  │ - Iterator  │  │  - Context  │  │  - Validation│           │
│  └─────────────┘  └─────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Authentication Flow

```
┌──────────┐                                      ┌─────────────────┐
│  Client  │                                      │ Sophos ID OAuth2│
└────┬─────┘                                      └────────┬────────┘
     │                                                     │
     │ 1. Request token with credentials                  │
     │────────────────────────────────────────────────────>│
     │    POST /api/v2/oauth2/token                       │
     │    grant_type: client_credentials                  │
     │    client_id: xxx                                  │
     │    client_secret: xxx                              │
     │                                                     │
     │ 2. Return access token                             │
     │<────────────────────────────────────────────────────│
     │    {                                               │
     │      "access_token": "eyJ...",                     │
     │      "expires_in": 3600                            │
     │    }                                               │
     │                                                     │
     ▼                                                     ▼
┌─────────────┐                               ┌────────────────────┐
│TokenManager │                               │ Sophos Central API │
│- Store token│                               └──────────┬─────────┘
│- Check expiry│                                         │
└─────┬───────┘                                          │
      │                                                   │
      │ 3. Call whoami to get data region               │
      │───────────────────────────────────────────────────>│
      │   GET /whoami/v1                                 │
      │   Authorization: Bearer eyJ...                   │
      │                                                   │
      │ 4. Return API URLs                               │
      │<───────────────────────────────────────────────────│
      │   {                                              │
      │     "id": "tenant-id",                           │
      │     "apiHosts": {                                │
      │       "dataRegion": "https://api-us..."          │
      │     }                                            │
      │   }                                              │
      │                                                   │
      │ 5. Make API calls to data region                │
      │───────────────────────────────────────────────────>│
      │   GET /endpoint/v1/endpoints                     │
      │   Authorization: Bearer eyJ...                   │
      │   X-Tenant-ID: tenant-id                         │
      │                                                   │
      │ 6. Return data                                   │
      │<───────────────────────────────────────────────────│
      │                                                   │
      └───────────────────────────────────────────────────┘
```

---

## 4. Request/Response Flow

```
┌─────────┐                                              ┌─────────┐
│   CLI   │                                              │   API   │
└────┬────┘                                              └────┬────┘
     │                                                        │
     │ 1. User command: pysophos endpoint list --health good │
     │                                                        │
     ▼                                                        │
┌─────────────┐                                             │
│CLI Handler  │                                             │
│- Parse args │                                             │
│- Validate   │                                             │
└────┬────────┘                                             │
     │                                                        │
     │ 2. Create filter object                               │
     ▼                                                        │
┌─────────────┐                                             │
│Filter Builder│                                            │
│- health=good│                                             │
└────┬────────┘                                             │
     │                                                        │
     │ 3. Call API client                                    │
     ▼                                                        │
┌─────────────────┐                                         │
│Endpoint API     │                                         │
│- list_endpoints()│                                        │
└────┬────────────┘                                         │
     │                                                        │
     │ 4. Build HTTP request                                 │
     ▼                                                        │
┌─────────────────┐                                         │
│  HTTP Client    │                                         │
│- Add auth header│                                         │
│- Add params     │                                         │
└────┬────────────┘                                         │
     │                                                        │
     │ 5. HTTP GET /endpoint/v1/endpoints?healthStatus=good │
     │────────────────────────────────────────────────────────>│
     │                                                        │
     │ 6. JSON response                                      │
     │<────────────────────────────────────────────────────────│
     │   { "items": [...], "pages": {...} }                 │
     │                                                        │
     ▼                                                        │
┌─────────────────┐                                         │
│Response Parser  │                                         │
│- Validate JSON  │                                         │
│- Parse to models│                                         │
└────┬────────────┘                                         │
     │                                                        │
     │ 7. Pydantic models                                    │
     ▼                                                        │
┌─────────────────┐                                         │
│PaginatedResponse│                                         │
│- items: [...]   │                                         │
│- pages: {...}   │                                         │
└────┬────────────┘                                         │
     │                                                        │
     │ 8. Return to CLI                                      │
     ▼                                                        │
┌─────────────────┐                                         │
│Output Formatter │                                         │
│- Format as table│                                         │
│- Apply colors   │                                         │
└────┬────────────┘                                         │
     │                                                        │
     │ 9. Display to user                                    │
     ▼                                                        │
┌─────────────────┐                                         │
│   Terminal      │                                         │
│  (Rich Table)   │                                         │
└─────────────────┘                                         │
```

---

## 5. Pagination Flow

```
┌────────┐                                          ┌─────────┐
│ Client │                                          │   API   │
└───┬────┘                                          └────┬────┘
    │                                                    │
    │ 1. Request first page (no cursor)                 │
    │────────────────────────────────────────────────────>│
    │   GET /endpoints?pageSize=50                      │
    │                                                    │
    │ 2. Return page 1 + nextKey                        │
    │<────────────────────────────────────────────────────│
    │   {                                               │
    │     "items": [50 items],                          │
    │     "pages": {                                    │
    │       "nextKey": "abc123"                         │
    │     }                                             │
    │   }                                               │
    │                                                    │
    ▼                                                    │
┌──────────┐                                            │
│Paginator │                                            │
│- Store   │                                            │
│  nextKey │                                            │
└────┬─────┘                                            │
     │                                                    │
     │ 3. Request next page with cursor                  │
     │────────────────────────────────────────────────────>│
     │   GET /endpoints?pageSize=50&pageFromKey=abc123   │
     │                                                    │
     │ 4. Return page 2 + nextKey                        │
     │<────────────────────────────────────────────────────│
     │   {                                               │
     │     "items": [50 items],                          │
     │     "pages": {                                    │
     │       "nextKey": "def456"                         │
     │     }                                             │
     │   }                                               │
     │                                                    │
     │ 5. Repeat until nextKey is null                   │
     │────────────────────────────────────────────────────>│
     │                                                    │
     │ 6. Last page (no nextKey)                         │
     │<────────────────────────────────────────────────────│
     │   {                                               │
     │     "items": [25 items],                          │
     │     "pages": {                                    │
     │       "nextKey": null                             │
     │     }                                             │
     │   }                                               │
     │                                                    │
     ▼                                                    │
┌──────────┐                                            │
│Complete! │                                            │
│125 items │                                            │
└──────────┘                                            │
```

---

## 6. Error Handling Flow

```
┌────────┐                                      ┌─────────────┐
│ Client │                                      │     API     │
└───┬────┘                                      └──────┬──────┘
    │                                                  │
    │ 1. API Request                                  │
    │──────────────────────────────────────────────────>│
    │                                                  │
    │ 2. Error Response (e.g., 401)                   │
    │<──────────────────────────────────────────────────│
    │   {                                             │
    │     "error": "invalid_token",                   │
    │     "message": "Token expired"                  │
    │   }                                             │
    │                                                  │
    ▼                                                  │
┌────────────────┐                                    │
│  HTTP Client   │                                    │
│  - Detect 401  │                                    │
│  - Raise error │                                    │
└───────┬────────┘                                    │
        │                                              │
        │ 3. Catch exception                          │
        ▼                                              │
┌────────────────┐                                    │
│ Error Handler  │                                    │
│ - Check type   │                                    │
└───────┬────────┘                                    │
        │                                              │
        ├─── If Auth Error ───>┌──────────────┐      │
        │                       │Auth Provider │      │
        │                       │- Refresh token│     │
        │                       └──────┬───────┘      │
        │                              │              │
        │                              │ 4. Get new token
        │                              │──────────────────>│
        │                              │              │
        │                              │ 5. New token │
        │                              │<──────────────────│
        │                              │              │
        │                       ┌──────▼───────┐      │
        │                       │ Retry Request│      │
        │                       └──────┬───────┘      │
        │                              │              │
        │                              │ 6. Retry     │
        │                              │──────────────────>│
        │                              │              │
        │                              │ 7. Success   │
        │                              │<──────────────────│
        │                              │              │
        │                              ▼              │
        │                       ┌──────────────┐      │
        │                       │Return Data   │      │
        │                       └──────────────┘      │
        │                                              │
        ├─── If Rate Limit ───>┌──────────────┐      │
        │                       │Wait & Retry  │      │
        │                       │- Exponential │      │
        │                       │  backoff     │      │
        │                       └──────────────┘      │
        │                                              │
        └─── If Fatal Error ──>┌──────────────┐      │
                                │ Raise to CLI │      │
                                │ - Format msg │      │
                                │ - Exit code  │      │
                                └──────────────┘      │
```

---

## 7. Configuration Loading Hierarchy

```
                    ┌───────────────────────┐
                    │  Load Configuration   │
                    └───────────┬───────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼────────┐ ┌───▼───────┐ ┌─────▼──────┐
        │  Default Values│ │Config File│ │   ENV Vars │
        │   - Built-in   │ │  - TOML   │ │  - OS env  │
        └───────┬────────┘ └───┬───────┘ └─────┬──────┘
                │               │               │
                │    Priority:  │               │
                │    Lowest ────┼───────> Highest
                │               │               │
                └───────────────┼───────────────┘
                                │
                        ┌───────▼────────┐
                        │ CLI Arguments  │
                        │  (Override all)│
                        └───────┬────────┘
                                │
                        ┌───────▼────────┐
                        │ Pydantic Model │
                        │   Validation   │
                        └───────┬────────┘
                                │
                                ▼
                        ┌────────────────┐
                        │ Final Config   │
                        │   - auth       │
                        │   - api        │
                        │   - output     │
                        │   - export     │
                        └────────────────┘

Priority Example:
─────────────────
default region = "us"
config file region = "eu"  ← Overrides default
ENV var SOPHOS_REGION = "ap" ← Overrides config file
CLI arg --region="us" ← Overrides everything
Final: region = "us"
```

---

## 8. Export System Architecture

```
┌─────────────┐
│  API Data   │
│ (Pydantic)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Export Manager │
│  - Select format│
│  - Field select │
│  - Destination  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│  JSON  │ │  CSV   │
│Exporter│ │Exporter│
└───┬────┘ └───┬────┘
    │          │
    │          ├──>┌──────────────┐
    │          │   │Flatten Nested│
    │          │   │  Objects     │
    │          │   └──────┬───────┘
    │          │          │
    │          │   ┌──────▼───────┐
    │          └──>│  Write CSV   │
    │              │  - Headers   │
    │              │  - Delimiter │
    │              └──────┬───────┘
    │                     │
    ├──>┌─────────────────▼──┐
    │   │  Pretty Print JSON │
    │   │  - Indentation     │
    │   │  - Sorting         │
    │   └─────────────┬──────┘
    │                 │
    └─────────────────┘
                      │
              ┌───────┴────────┐
              │                │
         ┌────▼────┐     ┌─────▼──────┐
         │  File   │     │   stdout   │
         │ System  │     │  (console) │
         └─────────┘     └────────────┘
```

---

## 9. CLI Command Tree

```
pysophos
├── config
│   ├── init        [Create config file]
│   ├── show        [Display current config]
│   ├── set         [Update config value]
│   └── test        [Test API connection]
│
├── endpoint
│   ├── list        [List endpoints]
│   ├── get         [Get endpoint details]
│   ├── scan        [Scan endpoint]
│   ├── isolate     [Isolate endpoint]
│   ├── unisolate   [Remove isolation]
│   ├── tamper
│   │   ├── get     [Get tamper status]
│   │   ├── update  [Update tamper protection]
│   │   └── password[Get tamper password]
│   └── settings
│       ├── allowed-items
│       ├── blocked-items
│       ├── web-control
│       └── tamper-protection
│
├── alerts
│   ├── list        [List alerts]
│   ├── get         [Get alert details]
│   ├── action      [Perform alert action]
│   └── search      [Search alerts]
│
├── tenants
│   ├── list        [List tenants]
│   └── get         [Get tenant details]
│
├── admins
│   ├── list        [List admins]
│   ├── get         [Get admin]
│   ├── create      [Create admin]
│   ├── update      [Update admin]
│   └── delete      [Delete admin]
│
└── roles
    ├── list        [List roles]
    ├── get         [Get role]
    ├── create      [Create role]
    ├── update      [Update role]
    └── delete      [Delete role]
```

---

## 10. Data Model Relationships

```
┌──────────────┐
│   Tenant     │
│  - id        │
│  - name      │
│  - region    │
└──────┬───────┘
       │
       │ has many
       │
       ├────────────────────────────────────┐
       │                                    │
       ▼                                    ▼
┌──────────────┐                    ┌──────────────┐
│  Endpoint    │                    │    Admin     │
│  - id        │                    │  - id        │
│  - hostname  │                    │  - email     │
│  - health    │                    │  - firstName │
│  - os        │                    │  - lastName  │
└──────┬───────┘                    └──────┬───────┘
       │                                    │
       │ has many                           │ has one
       │                                    │
       ▼                                    ▼
┌──────────────┐                    ┌──────────────┐
│    Alert     │                    │     Role     │
│  - id        │                    │  - id        │
│  - severity  │                    │  - name      │
│  - category  │                    │  - permissions│
│  - product   │                    └──────────────┘
└──────────────┘

┌──────────────┐
│  Endpoint    │
└──────┬───────┘
       │
       │ can have
       │
       ├─────────────────────────────┐
       │                             │
       ▼                             ▼
┌──────────────┐            ┌────────────────┐
│IsolationStatus│            │TamperProtection│
│  - enabled   │            │  - enabled     │
│  - comment   │            │  - password    │
└──────────────┘            └────────────────┘
```

---

## 11. Deployment Architecture

```
┌──────────────────────────────────────────────────┐
│              Development Machine                 │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │        Virtual Environment              │    │
│  │  ┌───────────────────────────────────┐  │    │
│  │  │     pysophoscentralapi            │  │    │
│  │  │     - Source code                 │  │    │
│  │  │     - Dependencies                │  │    │
│  │  │     - Tests                       │  │    │
│  │  └───────────────────────────────────┘  │    │
│  └─────────────────────────────────────────┘    │
│                      │                           │
│                      │ Package                   │
│                      ▼                           │
│  ┌─────────────────────────────────────────┐    │
│  │        Distribution Package             │    │
│  │  - pysophoscentralapi-1.0.0.tar.gz     │    │
│  │  - pysophoscentralapi-1.0.0-py3-none...│    │
│  └─────────────────────────────────────────┘    │
└──────────────────┬───────────────────────────────┘
                   │
                   │ Upload
                   ▼
┌──────────────────────────────────────────────────┐
│                    PyPI                          │
│  - Package hosting                              │
│  - Version management                           │
│  - Download statistics                          │
└──────────────────┬───────────────────────────────┘
                   │
                   │ pip install
                   ▼
┌──────────────────────────────────────────────────┐
│               End User Machine                   │
│                                                  │
│  $ pip install pysophoscentralapi               │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │  Installed Package                      │    │
│  │  - CLI available globally               │    │
│  │  - Python library importable            │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  Usage:                                         │
│  $ pysophos endpoint list                       │
│                                                  │
│  Or:                                            │
│  >>> from pysophoscentralapi import ...         │
└──────────────────────────────────────────────────┘
```

---

## 12. Testing Pyramid

```
                    ┌──────────┐
                    │   E2E    │  ← Few, Slow, Expensive
                    │  Tests   │    (Full integration)
                    └────┬─────┘
                         │
                ┌────────▼────────┐
                │  Integration    │  ← Some, Medium
                │     Tests       │    (Multiple components)
                └────────┬────────┘
                         │
           ┌─────────────▼─────────────┐
           │      Unit Tests           │  ← Many, Fast, Cheap
           │   (Individual functions)  │    (Single components)
           └───────────────────────────┘

Distribution:
─────────────
E2E Tests:           ~5%   (10-20 tests)
Integration Tests:   ~15%  (50-80 tests)
Unit Tests:          ~80%  (300-500 tests)
```

---

## 13. CI/CD Pipeline

```
┌────────────┐
│   Push     │
│  to repo   │
└─────┬──────┘
      │
      ▼
┌─────────────────┐
│  GitHub Actions │
└─────┬───────────┘
      │
      ├──> Lint Check (ruff)
      │      │
      │      ├─ Pass ──┐
      │      └─ Fail ──> ❌ Stop
      │                 │
      ├──> Type Check (mypy)
      │      │
      │      ├─ Pass ──┐
      │      └─ Fail ──> ❌ Stop
      │                 │
      ├──> Unit Tests
      │      │
      │      ├─ Pass ──┐
      │      └─ Fail ──> ❌ Stop
      │                 │
      ├──> Integration Tests
      │      │
      │      ├─ Pass ──┐
      │      └─ Fail ──> ❌ Stop
      │                 │
      ├──> Coverage Check
      │      │
      │      ├─ >90% ──┐
      │      └─ <90% ──> ❌ Stop
      │                 │
      └────────────────┐│
                       ││
                       ▼▼
              ┌──────────────┐
              │  All Pass ✅ │
              └───────┬──────┘
                      │
          ┌───────────┼───────────┐
          │                       │
          ▼                       ▼
    ┌───────────┐         ┌─────────────┐
    │   Merge   │         │Create Build │
    │     PR    │         │ (if tag)    │
    └───────────┘         └──────┬──────┘
                                 │
                                 ▼
                          ┌─────────────┐
                          │Publish PyPI │
                          └─────────────┘
```

---

These architecture diagrams provide visual representations of the system design and should be referenced during implementation to ensure consistency with the planned architecture.

