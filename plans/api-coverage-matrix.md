# PySophosCentralApi - API Coverage Matrix

This document provides a comprehensive list of all Sophos Central API endpoints that will be implemented, organized by API and category. Use this as a checklist during development.

## Legend

- ✅ Implemented
- 🚧 In Progress
- ⏳ Planned
- ❌ Not Planned
- 🔄 Needs Update

## Interface Support

**All API endpoints support both interfaces:**
- **Async (Primary)**: `await client.endpoint.list_endpoints()`
- **Sync (Wrapper)**: `client_sync.endpoint.list_endpoints()` (no await)

Implementation priority: Async first, then sync wrapper.

---

## Endpoint API v1

Base URL: `{dataRegion}/endpoint/v1`

### Endpoints Management

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/endpoints` | List all endpoints | ⏳ | High |
| GET | `/endpoints/{endpointId}` | Get endpoint by ID | ⏳ | High |
| PATCH | `/endpoints/{endpointId}` | Update endpoint | ⏳ | Medium |
| DELETE | `/endpoints/{endpointId}` | Delete endpoint | ⏳ | Medium |

**Supported Query Parameters for List:**
- `pageSize`: Results per page (1-1000, default 50)
- `pageFromKey`: Pagination cursor
- `view`: Detail level (basic/summary/full)
- `healthStatus`: Filter by health status
- `type`: Filter by endpoint type
- `tamperProtectionEnabled`: Filter by tamper protection
- `lockdownStatus`: Filter by lockdown status
- `lastSeenBefore`: Filter by last seen date
- `lastSeenAfter`: Filter by last seen date
- `ids`: Filter by specific IDs
- `hostnameContains`: Filter by hostname
- `ipAddresses`: Filter by IP address
- `macAddresses`: Filter by MAC address
- `search`: Full-text search
- `searchFields`: Fields to search

### Endpoint Actions - Scans

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| POST | `/endpoints/{endpointId}/scans` | Start endpoint scan | ⏳ | High |
| GET | `/endpoints/scans` | List all scans | ⏳ | Medium |
| GET | `/endpoints/{endpointId}/scans` | List endpoint scans | ⏳ | Medium |
| DELETE | `/endpoints/{endpointId}/scans` | Cancel endpoint scan | ⏳ | Low |

### Endpoint Actions - Isolation

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| POST | `/endpoints/{endpointId}/isolation` | Isolate endpoint | ⏳ | High |
| DELETE | `/endpoints/{endpointId}/isolation` | Un-isolate endpoint | ⏳ | High |
| GET | `/endpoints/{endpointId}/isolation` | Get isolation status | ⏳ | Medium |

### Endpoint Actions - Tamper Protection

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/endpoints/{endpointId}/tamper-protection` | Get tamper protection status | ⏳ | High |
| POST | `/endpoints/{endpointId}/tamper-protection` | Update tamper protection | ⏳ | High |
| GET | `/endpoints/{endpointId}/tamper-protection/password` | Get tamper protection password | ⏳ | Medium |

### Endpoint Migration

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| POST | `/migrations/endpoints` | Create migration job | ⏳ | Low |
| GET | `/migrations/endpoints` | List migration jobs | ⏳ | Low |
| GET | `/migrations/endpoints/{migrationJobId}` | Get migration job | ⏳ | Low |
| DELETE | `/migrations/endpoints/{migrationJobId}` | Cancel migration job | ⏳ | Low |

### Settings - General

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings` | Get all settings | ⏳ | Medium |

### Settings - Allowed Items

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings/allowed-items` | Get allowed items | ⏳ | Medium |
| POST | `/settings/allowed-items` | Add allowed item | ⏳ | Medium |
| GET | `/settings/allowed-items/{itemId}` | Get allowed item | ⏳ | Low |
| DELETE | `/settings/allowed-items/{itemId}` | Delete allowed item | ⏳ | Low |

### Settings - Blocked Items

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings/blocked-items` | Get blocked items | ⏳ | Medium |
| POST | `/settings/blocked-items` | Add blocked item | ⏳ | Medium |
| GET | `/settings/blocked-items/{itemId}` | Get blocked item | ⏳ | Low |
| DELETE | `/settings/blocked-items/{itemId}` | Delete blocked item | ⏳ | Low |

### Settings - Exploit Mitigation

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings/exploit-mitigation` | Get exploit mitigation settings | ⏳ | Low |
| PATCH | `/settings/exploit-mitigation` | Update exploit mitigation | ⏳ | Low |
| GET | `/settings/exploit-mitigation/applications` | Get protected applications | ⏳ | Low |

### Settings - Web Control

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings/web-control` | Get web control settings | ⏳ | Medium |
| PATCH | `/settings/web-control` | Update web control settings | ⏳ | Medium |
| GET | `/settings/web-control/local-sites` | Get local sites list | ⏳ | Low |
| POST | `/settings/web-control/local-sites` | Add local site | ⏳ | Low |
| DELETE | `/settings/web-control/local-sites/{siteId}` | Delete local site | ⏳ | Low |

### Settings - Tamper Protection

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings/tamper-protection` | Get global tamper protection | ⏳ | High |
| PATCH | `/settings/tamper-protection` | Update global tamper protection | ⏳ | High |

### Settings - Exclusions

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings/exclusions` | Get scanning exclusions | ⏳ | Medium |
| POST | `/settings/exclusions` | Add exclusion | ⏳ | Medium |
| GET | `/settings/exclusions/{exclusionId}` | Get exclusion | ⏳ | Low |
| PATCH | `/settings/exclusions/{exclusionId}` | Update exclusion | ⏳ | Low |
| DELETE | `/settings/exclusions/{exclusionId}` | Delete exclusion | ⏳ | Low |

### Settings - Update Policies

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings/update-policies` | Get update policies | ⏳ | Low |
| PATCH | `/settings/update-policies` | Update policies | ⏳ | Low |

---

## Common API v1

Base URL: `{dataRegion}/common/v1`

### Alerts

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/alerts` | List alerts | ⏳ | High |
| GET | `/alerts/{alertId}` | Get alert by ID | ⏳ | High |
| POST | `/alerts/{alertId}/actions` | Perform alert action | ⏳ | High |
| POST | `/alerts/search` | Search alerts | ⏳ | Medium |

**Supported Query Parameters for List:**
- `pageSize`: Results per page
- `pageFromKey`: Pagination cursor
- `product`: Filter by product
- `category`: Filter by category
- `groupKey`: Filter by group
- `severity`: Filter by severity
- `ids`: Filter by specific IDs
- `fields`: Fields to return
- `from`: Start date
- `to`: End date

**Supported Alert Actions:**
- `acknowledge`: Acknowledge alert
- `clearThreat`: Clear threat
- `clearPua`: Clear PUA
- `clearHmpa`: Clear HMPA
- `clearBehavior`: Clear behavioral detection
- `authPua`: Authorize PUA
- `cleanPua`: Clean PUA
- `cleanBehavior`: Clean behavioral detection

### Directory - Tenants

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/tenants` | List tenants | ⏳ | High |
| GET | `/tenants/{tenantId}` | Get tenant by ID | ⏳ | High |
| POST | `/tenants` | Create tenant | ⏳ | Medium |
| PATCH | `/tenants/{tenantId}` | Update tenant | ⏳ | Medium |
| DELETE | `/tenants/{tenantId}` | Delete tenant | ⏳ | Low |

**Supported Query Parameters for List:**
- `pageSize`: Results per page
- `pageFromKey`: Pagination cursor
- `dataRegion`: Filter by region
- `ids`: Filter by specific IDs
- `showCounts`: Include entity counts

### Directory - Admins

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/admins` | List admins | ⏳ | High |
| GET | `/admins/{adminId}` | Get admin by ID | ⏳ | High |
| POST | `/admins` | Create admin | ⏳ | High |
| PATCH | `/admins/{adminId}` | Update admin | ⏳ | High |
| DELETE | `/admins/{adminId}` | Delete admin | ⏳ | Medium |

### Directory - Roles

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/roles` | List roles | ⏳ | High |
| GET | `/roles/{roleId}` | Get role by ID | ⏳ | High |
| POST | `/roles` | Create custom role | ⏳ | Medium |
| PATCH | `/roles/{roleId}` | Update role | ⏳ | Medium |
| DELETE | `/roles/{roleId}` | Delete role | ⏳ | Low |

### Directory - Users

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/users` | List users | ⏳ | Medium |
| GET | `/users/{userId}` | Get user by ID | ⏳ | Medium |
| POST | `/users` | Create user | ⏳ | Low |
| PATCH | `/users/{userId}` | Update user | ⏳ | Low |
| DELETE | `/users/{userId}` | Delete user | ⏳ | Low |

### Directory - Groups

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/directory/groups` | List groups | ⏳ | Medium |
| GET | `/directory/groups/{groupId}` | Get group by ID | ⏳ | Medium |
| POST | `/directory/groups` | Create group | ⏳ | Low |
| PATCH | `/directory/groups/{groupId}` | Update group | ⏳ | Low |
| DELETE | `/directory/groups/{groupId}` | Delete group | ⏳ | Low |

### Endpoint Groups

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/endpoint-groups` | List endpoint groups | ⏳ | Medium |
| GET | `/endpoint-groups/{groupId}` | Get group by ID | ⏳ | Medium |
| POST | `/endpoint-groups` | Create group | ⏳ | Medium |
| PATCH | `/endpoint-groups/{groupId}` | Update group | ⏳ | Medium |
| DELETE | `/endpoint-groups/{groupId}` | Delete group | ⏳ | Low |
| POST | `/endpoint-groups/{groupId}/endpoints` | Add endpoints to group | ⏳ | Medium |
| DELETE | `/endpoint-groups/{groupId}/endpoints` | Remove endpoints from group | ⏳ | Medium |

### Account Health

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/account-health/check` | Get account health status | ⏳ | Low |

### Settings

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `/settings` | Get tenant settings | ⏳ | Low |
| PATCH | `/settings` | Update tenant settings | ⏳ | Low |

---

## Whoami & Authentication

### Authentication Endpoints

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| POST | `https://id.sophos.com/api/v2/oauth2/token` | Get OAuth2 token | ⏳ | Critical |
| POST | `https://id.sophos.com/api/v2/oauth2/revoke` | Revoke token | ⏳ | Low |

### Whoami Endpoint

| Method | Endpoint | Description | Status | Priority |
|--------|----------|-------------|--------|----------|
| GET | `https://api.central.sophos.com/whoami/v1` | Get API URLs | ⏳ | Critical |

---

## Implementation Priorities

### Phase 1: Critical (Weeks 1-2)
Must have for basic functionality:
- ✅ OAuth2 authentication
- ✅ Whoami endpoint
- ✅ Token management
- ✅ Base HTTP client
- ✅ Error handling

### Phase 2: High Priority (Weeks 3-5)
Core API functionality:
- Endpoint listing and details
- Endpoint scanning
- Endpoint isolation
- Tamper protection
- Alert listing and actions
- Tenant management
- Admin management
- Role management

### Phase 3: Medium Priority (Weeks 6-8)
Extended functionality:
- Endpoint settings (allowed/blocked items)
- Web control settings
- Alert search
- Endpoint groups
- User management
- Exclusions management

### Phase 4: Low Priority (Weeks 9-10)
Nice-to-have features:
- Migration operations
- Exploit mitigation settings
- Update policies
- Directory groups
- Account health check
- Local sites management

---

## CLI Command Structure

### Endpoint Commands

```bash
pysophos endpoint list [OPTIONS]
pysophos endpoint get <endpoint-id>
pysophos endpoint scan <endpoint-id>
pysophos endpoint isolate <endpoint-id> [--comment TEXT]
pysophos endpoint unisolate <endpoint-id> [--comment TEXT]
pysophos endpoint tamper get <endpoint-id>
pysophos endpoint tamper update <endpoint-id> [--enabled/--disabled]
pysophos endpoint tamper password <endpoint-id>
```

### Alert Commands

```bash
pysophos alerts list [OPTIONS]
pysophos alerts get <alert-id>
pysophos alerts action <alert-id> <action> [--message TEXT]
pysophos alerts search <query> [OPTIONS]
```

### Tenant Commands

```bash
pysophos tenants list [OPTIONS]
pysophos tenants get <tenant-id>
```

### Admin Commands

```bash
pysophos admins list
pysophos admins get <admin-id>
pysophos admins create [OPTIONS]
pysophos admins update <admin-id> [OPTIONS]
pysophos admins delete <admin-id>
```

### Role Commands

```bash
pysophos roles list
pysophos roles get <role-id>
pysophos roles create <name> [OPTIONS]
pysophos roles update <role-id> [OPTIONS]
pysophos roles delete <role-id>
```

### Settings Commands

```bash
pysophos settings allowed-items list
pysophos settings allowed-items add [OPTIONS]
pysophos settings allowed-items delete <item-id>

pysophos settings blocked-items list
pysophos settings blocked-items add [OPTIONS]
pysophos settings blocked-items delete <item-id>

pysophos settings web-control get
pysophos settings web-control update [OPTIONS]

pysophos settings tamper-protection get
pysophos settings tamper-protection update [--enabled/--disabled]
```

### Configuration Commands

```bash
pysophos config init
pysophos config show
pysophos config set <key> <value>
pysophos config test
```

---

## Testing Coverage Requirements

### Unit Tests Required

For each API endpoint:
- ✅ Success case
- ✅ With all filter combinations
- ✅ Pagination handling
- ✅ Error cases (400, 401, 403, 404, 500)
- ✅ Rate limiting (429)
- ✅ Network errors
- ✅ Invalid parameters
- ✅ Model validation

### Integration Tests Required

- ✅ Full authentication flow
- ✅ Multi-page pagination
- ✅ Filter combinations
- ✅ Export to JSON
- ✅ Export to CSV
- ✅ CLI command execution
- ✅ Error recovery

### CLI Tests Required

- ✅ All commands execute
- ✅ Option parsing
- ✅ Output formatting
- ✅ Export to file
- ✅ Error messages
- ✅ Help text

---

## Documentation Requirements

For each API endpoint/module:
- [ ] Function/method docstrings (Google style)
- [ ] Type hints
- [ ] Usage examples
- [ ] CLI examples
- [ ] Error handling documentation
- [ ] API reference entry
- [ ] User guide section (if applicable)

---

## Performance Benchmarks

Target performance metrics:

| Operation | Target | Notes |
|-----------|--------|-------|
| Single endpoint fetch | <500ms | Including auth |
| List 100 endpoints | <2s | Single page |
| List 1000 endpoints | <20s | Multiple pages |
| Export 1000 items to JSON | <5s | File write |
| Export 1000 items to CSV | <5s | File write |
| Concurrent requests (10) | <3s | With connection pooling |

---

## Security Checklist

- [ ] Credentials never logged
- [ ] Sensitive data filtered from logs
- [ ] Token expiration handled
- [ ] Rate limiting respected
- [ ] HTTPS only
- [ ] Input validation
- [ ] SQL injection prevention (N/A for REST API)
- [ ] Path traversal prevention (file exports)
- [ ] Dependency security audit
- [ ] Secrets not in code/docs

---

## Accessibility & Usability

- [ ] Colored output (with disable option)
- [ ] Progress indicators for long operations
- [ ] Clear error messages
- [ ] Helpful help text
- [ ] Tab completion support (future)
- [ ] Examples in help text
- [ ] Consistent command structure
- [ ] Sensible defaults
- [ ] Confirmation for destructive operations

---

This API coverage matrix will be updated throughout the project as endpoints are implemented. Use the status column to track progress and refer to this document when planning sprints and milestones.

