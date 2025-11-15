# Technical Decision: Dual Interface Support (Async + Sync)

**Date**: November 15, 2025  
**Status**: ✅ Approved  
**Decision**: Implement both asynchronous and synchronous interfaces

---

## Decision Summary

PySophosCentralApi will provide **both async and sync interfaces** with the following architecture:

- **Async interface is primary and default**: All core functionality implemented async-first
- **Sync interface via thin wrappers**: Use `asyncio.run()` to wrap async calls
- **Library usage**: Users can choose either interface based on their needs
- **CLI usage**: Async by default, with optional `--sync` flag for sync mode

---

## Rationale

### Why Support Both?

1. **Flexibility**: Different use cases have different requirements
   - **Async**: Optimal for scripts with concurrent operations
   - **Sync**: Easier for simple scripts, interactive use, legacy integration

2. **Ease of Integration**: 
   - Some users have existing sync codebases
   - Interactive Python sessions work better with sync code
   - Simple one-off scripts don't need async complexity

3. **Performance Options**:
   - Async users get maximum performance through concurrency
   - Sync users get simpler code without async ceremony
   - Same underlying implementation ensures consistency

4. **Minimal Maintenance Burden**:
   - Single source of truth (async implementation)
   - Sync wrappers are thin and mechanical
   - No duplicate business logic

---

## Implementation Architecture

```
User Code
    │
    ├─ Async Interface (primary)
    │  └─ async with SophosClient(config) as client:
    │      └─ await client.endpoint.list_endpoints()
    │
    └─ Sync Interface (wrapper)
       └─ with SophosClientSync(config) as client:
           └─ client.endpoint.list_endpoints()  # No await
               │
               └─ Internally calls: asyncio.run(async_method())
```

### Module Structure

```
pysophoscentralapi/
├── core/              # Async implementations (PRIMARY)
│   ├── client.py      # HTTPClient (async)
│   ├── auth.py        # OAuth2ClientCredentials (async)
│   └── pagination.py  # Paginator (async)
│
├── sync/              # Sync wrappers (NEW)
│   ├── __init__.py
│   ├── base.py        # SyncWrapper base class
│   ├── client.py      # HTTPClientSync
│   ├── auth.py        # OAuth2ClientCredentialsSync
│   └── pagination.py  # PaginatorSync
│
└── api/
    ├── endpoint/      # Async API clients + sync wrappers
    └── common/        # Async API clients + sync wrappers
```

---

## Usage Examples

### Async (Recommended for Concurrent Operations)

```python
import asyncio
from pysophoscentralapi import SophosClient
from pysophoscentralapi.core.config import Config

async def main():
    config = Config.from_file()
    async with SophosClient(config) as client:
        # Async operations with await
        endpoints = await client.endpoint.list_endpoints()
        alerts = await client.alerts.list_alerts()
        
        # Concurrent operations (FAST!)
        results = await asyncio.gather(
            client.endpoint.get("id-1"),
            client.endpoint.get("id-2"),
            client.endpoint.get("id-3"),
        )

asyncio.run(main())
```

### Sync (For Simple Scripts)

```python
from pysophoscentralapi.sync import SophosClientSync
from pysophoscentralapi.core.config import Config

config = Config.from_file()
with SophosClientSync(config) as client:
    # Blocking operations, no await needed
    endpoints = client.endpoint.list_endpoints()
    alerts = client.alerts.list_alerts()
    
    # Sequential operations (simple but slower)
    for endpoint_id in ["id-1", "id-2", "id-3"]:
        result = client.endpoint.get(endpoint_id)
```

### CLI Usage

```bash
# Async mode (default - better performance for complex operations)
pysophos endpoint list

# Sync mode (explicit flag - simpler for quick queries)
pysophos --sync endpoint list
```

---

## Implementation Plan

### Phase 1: Foundation (Current)
- [x] Async core infrastructure implemented
- [ ] **NEW**: Add sync wrapper infrastructure
  - [ ] `sync/base.py` - SyncWrapper base class
  - [ ] `sync/client.py` - HTTPClientSync
  - [ ] `sync/auth.py` - OAuth2ClientCredentialsSync
  - [ ] `sync/pagination.py` - PaginatorSync
  - [ ] Tests for sync wrappers

**Note**: Sync wrappers will be added after Phase 2-3 when we have API clients to wrap.

### Phase 2: Endpoint API
- [ ] Implement async Endpoint API client
- [ ] Create sync wrapper for Endpoint API
- [ ] Test both interfaces

### Phase 3: Common API
- [ ] Implement async Common API client
- [ ] Create sync wrapper for Common API
- [ ] Test both interfaces

### Phase 4: CLI
- [ ] Add `--sync` global flag
- [ ] Update all commands to support both modes
- [ ] Test CLI in both modes

---

## Benefits

### For Users

✅ **Choice**: Use what fits your use case  
✅ **Simplicity**: Sync interface for simple scripts  
✅ **Performance**: Async for concurrent operations  
✅ **Integration**: Works with existing sync codebases  
✅ **Learning curve**: Start with sync, upgrade to async when needed

### For Maintainers

✅ **Single source of truth**: All logic in async implementation  
✅ **Thin wrappers**: Sync code is just `asyncio.run()` calls  
✅ **Less duplication**: No parallel implementations  
✅ **Easy testing**: Test async thoroughly, sync lightly  
✅ **Clear pattern**: Consistent wrapper approach

---

## Trade-offs

### Pros
- Maximum flexibility for users
- Easy integration with sync code
- Performance benefits of async when needed
- Clear, understandable pattern

### Cons
- Slightly larger API surface
- Need to maintain sync wrappers
- Documentation needs to show both patterns
- Users must understand when to use which

**Verdict**: Pros outweigh cons. The pattern is well-established (httpx, databases, etc.)

---

## Documentation Strategy

All documentation will show **both** patterns:

1. **Quick Start**: Show sync for simplicity
2. **Advanced Usage**: Show async for performance
3. **Best Practices**: Guide users on when to use which
4. **API Reference**: Document both interfaces

Example from README:

```python
# Simple script? Use sync:
with SophosClientSync(config) as client:
    endpoints = client.endpoint.list_endpoints()

# Need concurrency? Use async:
async with SophosClient(config) as client:
    endpoints = await client.endpoint.list_endpoints()
```

---

## Testing Strategy

### Async Tests (Comprehensive)
- Test all functionality thoroughly
- Test error cases
- Test edge cases
- Test concurrent operations

### Sync Tests (Light)
- Verify wrapper works
- Test context manager
- Test error propagation
- Don't duplicate all async tests

**Principle**: Test implementation (async) thoroughly, test interface (sync wrapper) lightly.

---

## Related Documents

- [Project Plan - Technical Decisions](plans/project-plan.md#15-technical-decisions--open-questions)
- [Technical Specification - Dual Interface](plans/technical-specification.md#0-dual-interface-architecture-async--sync)
- [Sync Implementation Guide](plans/sync-implementation-guide.md)
- [Architecture Diagrams](plans/architecture-diagrams.md#0-dual-interface-architecture-async--sync)
- [API Coverage Matrix](plans/api-coverage-matrix.md#interface-support)

---

## Approval

This decision has been approved and incorporated into all planning documents:

- ✅ Project Plan updated
- ✅ Technical Specification updated  
- ✅ Architecture Diagrams updated
- ✅ API Coverage Matrix updated
- ✅ Plans README updated
- ✅ Sync Implementation Guide created

**Implementation begins in Phase 1.5** (after current Phase 1 completion, before Phase 2).

---

## Questions?

For implementation details, see [Sync Implementation Guide](plans/sync-implementation-guide.md).

For architectural overview, see [Technical Specification](plans/technical-specification.md#0-dual-interface-architecture-async--sync).

