# AINative Python SDK v3.0 Migration Guide

**Release Date:** 2026-01-09
**Deprecation Deadline:** 2026-02-07 (30 days)

## Overview

AINative Python SDK v3.0.0 introduces **breaking changes** to endpoint paths to align with the backend API cleanup (Issues #728-734). All deprecated endpoint paths will be removed from the backend on **2026-02-07**.

**⚠️ ACTION REQUIRED:** Update to SDK v3.0.0 before February 7, 2026 to avoid service disruption.

---

## What Changed?

### Endpoint Path Updates

All ZeroDB endpoints have moved from `/zerodb/*` prefixes to canonical `/projects/*` paths:

| Module | Old Path | New Path | Breaking? |
|--------|----------|----------|-----------|
| Projects | `/zerodb/projects/*` | `/projects/*` | ❌ No |
| Vectors | `/zerodb/vectors/*` | `/projects/{project_id}/database/vectors/*` | ✅ **Yes** |
| Tables | `/zerodb/tables/*` | `/projects/{project_id}/database/tables/*` | ✅ **Yes** |
| Memory | `/zerodb/memory/*` | `/projects/{project_id}/database/memory/*` | ✅ **Yes** |
| Analytics | `/zerodb/analytics/*` | `/projects/{project_id}/database/analytics/*` | ✅ **Yes** |

### Breaking Changes

#### 1. Tables Module - `project_id` Now Required

**All table methods now require `project_id` as the first parameter.**

##### Before (v2.x):
```python
client = AINativeClient(api_key="your-key")

# Create table - NO project_id required
table = client.zerodb.tables.create_table(
    table_name="users",
    schema={"fields": {"email": "string", "name": "string"}}
)

# List tables - NO project_id required
tables = client.zerodb.tables.list_tables(limit=50)

# Query rows - NO project_id required
results = client.zerodb.tables.query_rows(
    table_name="users",
    filter={"age": {"$gte": 25}}
)
```

##### After (v3.0):
```python
client = AINativeClient(api_key="your-key")
PROJECT_ID = "your-project-id"

# Create table - project_id REQUIRED
table = client.zerodb.tables.create_table(
    PROJECT_ID,  # NEW: First parameter
    table_name="users",
    schema={"fields": {"email": "string", "name": "string"}}
)

# List tables - project_id REQUIRED
tables = client.zerodb.tables.list_tables(PROJECT_ID, limit=50)

# Query rows - project_id REQUIRED
results = client.zerodb.tables.query_rows(
    PROJECT_ID,  # NEW: First parameter
    table_name="users",
    filter={"age": {"$gte": 25}}
)
```

#### 2. Memory Module - `project_id` Now Required

##### Before (v2.x):
```python
# Create memory - NO project_id required
memory = client.zerodb.memory.create(
    content="User prefers dark mode",
    tags=["preferences", "ui"]
)

# Search memory - NO project_id required
results = client.zerodb.memory.search(
    query="What does user prefer?",
    top_k=5
)
```

##### After (v3.0):
```python
PROJECT_ID = "your-project-id"

# Create memory - project_id REQUIRED
memory = client.zerodb.memory.create(
    PROJECT_ID,  # NEW: First parameter
    content="User prefers dark mode",
    tags=["preferences", "ui"]
)

# Search memory - project_id REQUIRED
results = client.zerodb.memory.search(
    PROJECT_ID,  # NEW: First parameter
    query="What does user prefer?",
    top_k=5
)
```

#### 3. Analytics Module - `project_id` Now Required

##### Before (v2.x):
```python
# Get usage analytics
usage = client.zerodb.analytics.get_usage(
    project_id="proj-123",  # Optional parameter
    start_date=datetime(2026, 1, 1)
)
```

##### After (v3.0):
```python
PROJECT_ID = "proj-123"

# Get usage analytics
usage = client.zerodb.analytics.get_usage(
    PROJECT_ID,  # NEW: Required first parameter
    start_date=datetime(2026, 1, 1)
)
```

---

## Migration Checklist

### Step 1: Install SDK v3.0.0

```bash
pip install --upgrade ainative-python==3.0.0
```

### Step 2: Update Code

#### Find All SDK Usage
```bash
# Search for SDK imports
grep -r "from ainative import\|import ainative" .

# Search for table operations
grep -r "\.tables\." .

# Search for memory operations
grep -r "\.memory\." .

# Search for analytics operations
grep -r "\.analytics\." .
```

#### Update Each Module

1. **Tables Module**
   - Add `project_id` as first parameter to ALL table methods
   - Methods affected:
     - `create_table(project_id, ...)`
     - `list_tables(project_id, ...)`
     - `get_table(project_id, ...)`
     - `delete_table(project_id, ...)`
     - `insert_rows(project_id, ...)`
     - `query_rows(project_id, ...)`
     - `update_rows(project_id, ...)`
     - `delete_rows(project_id, ...)`
     - `count_rows(project_id, ...)`
     - `table_exists(project_id, ...)`

2. **Memory Module**
   - Add `project_id` as first parameter to ALL memory methods
   - Methods affected:
     - `create(project_id, ...)`
     - `list(project_id, ...)`
     - `search(project_id, ...)`
     - `get(project_id, ...)`
     - `update(project_id, ...)`
     - `delete(project_id, ...)`

3. **Analytics Module**
   - Add `project_id` as first parameter to ALL analytics methods
   - Methods affected:
     - `get_usage(project_id, ...)`
     - `get_performance_metrics(project_id, ...)`
     - `get_storage_stats(project_id, ...)`
     - `get_query_insights(project_id, ...)`

### Step 3: Test Your Application

```python
# Test basic operations
import ainative

client = ainative.AINativeClient(api_key="your-key")
PROJECT_ID = "your-project-id"

# Test tables
try:
    tables = client.zerodb.tables.list_tables(PROJECT_ID)
    print(f"✅ Tables: {len(tables['tables'])} found")
except Exception as e:
    print(f"❌ Tables error: {e}")

# Test vectors
try:
    vectors = client.zerodb.vectors.search(
        PROJECT_ID,
        vector=[0.1] * 1536,
        top_k=5
    )
    print(f"✅ Vectors: {len(vectors)} results")
except Exception as e:
    print(f"❌ Vectors error: {e}")

# Test memory
try:
    memories = client.zerodb.memory.list(PROJECT_ID, limit=10)
    print(f"✅ Memory: Listed successfully")
except Exception as e:
    print(f"❌ Memory error: {e}")
```

### Step 4: Update Tests

If you have tests using the SDK, update all test assertions:

```python
# Before (v2.x)
def test_list_tables():
    tables = client.zerodb.tables.list_tables()
    assert len(tables['tables']) > 0

# After (v3.0)
def test_list_tables():
    PROJECT_ID = "test-project"
    tables = client.zerodb.tables.list_tables(PROJECT_ID)
    assert len(tables['tables']) > 0
```

---

## Common Migration Errors

### Error 1: Missing `project_id` Parameter
```python
TypeError: create_table() missing 1 required positional argument: 'project_id'
```

**Solution:** Add `project_id` as the first parameter:
```python
# Fix: Add PROJECT_ID as first parameter
table = client.zerodb.tables.create_table(PROJECT_ID, "users", schema)
```

### Error 2: Wrong Parameter Order
```python
# ❌ WRONG: project_id after table_name
client.zerodb.tables.query_rows("users", PROJECT_ID, filter={...})
```

**Solution:** `project_id` must be **first**:
```python
# ✅ CORRECT: project_id first
client.zerodb.tables.query_rows(PROJECT_ID, "users", filter={...})
```

### Error 3: 404 Endpoint Not Found
```
APIError: API error: 404 - Endpoint not found
```

**Solution:** You're still using SDK v2.x. Upgrade to v3.0:
```bash
pip install --upgrade ainative-python==3.0.0
```

---

## Non-Breaking Changes

### Modules That Did NOT Change

✅ **Projects Module** - No changes required
```python
# These still work the same
projects = client.zerodb.projects.list()
project = client.zerodb.projects.get("proj-123")
project = client.zerodb.projects.create(name="My Project")
```

✅ **Auth Module** - No changes required
```python
# These still work the same
user = client.auth.get_current_user()
client.auth.logout()
```

✅ **Agent Swarm Module** - No changes required
```python
# These still work the same
swarm = client.agent_swarm.start_swarm(...)
```

---

## Timeline

| Date | Event |
|------|-------|
| **2026-01-09** | ✅ SDK v3.0.0 released |
| **2026-01-09 - 2026-02-06** | 🟡 Grace period - both old and new paths work |
| **2026-02-07** | 🔴 Backend removes deprecated paths - **OLD PATHS STOP WORKING** |

---

## Getting Help

### Documentation
- **Full SDK Docs:** https://docs.ainative.studio/sdk/python
- **API Reference:** https://api.ainative.studio/docs-enhanced
- **CHANGELOG:** See `CHANGELOG.md` in SDK

### Support Channels
- **GitHub Issues:** https://github.com/AINative-Studio/core/issues
- **Email:** support@ainative.studio
- **Discord:** https://discord.gg/ainative

### Related Issues
- Issue #738: Python SDK Endpoint Path Updates
- Issue #728-734: Backend API Cleanup Phase 1

---

## FAQ

**Q: Do I need to update my API keys?**
A: No, API keys remain the same.

**Q: Will my existing code break on 2026-02-07?**
A: Yes, if you don't update to SDK v3.0.0 before then. Old paths will return 404 errors.

**Q: Can I test the new SDK without breaking production?**
A: Yes, install v3.0.0 in a test environment first. Both old and new paths work during the grace period.

**Q: What if I can't migrate by February 7?**
A: Contact support@ainative.studio for assistance. We can provide guidance or extend the grace period for critical cases.

**Q: Are there any performance improvements in v3.0?**
A: Performance is the same, but the new paths follow REST best practices and are more maintainable.

---

**Last Updated:** 2026-01-09
**SDK Version:** 3.0.0
**Status:** Active Migration Period
