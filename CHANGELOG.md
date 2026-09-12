# Changelog

All notable changes to the AINative Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-01-12

### Changed
- SDK certified compatible with backend endpoint consolidation (Issue #757, #758)
- No code changes required - SDK already uses canonical paths
- SDK ready for deprecated /v1/admin/* endpoint sunset (2026-02-12)

### Notes
- Python SDK does not use any of the deprecated admin paths
- All SDK endpoints already use canonical /v1/public/* or /v1/projects/* paths
- Version bump ensures users have deprecation-safe SDK version
- See docs/api/ISSUE_757_MIGRATION_GUIDE.md for backend changes

### Deprecated Backend Paths (Not Used by SDK)
The following backend paths are deprecated (sunset: 2026-02-12):
- /v1/admin/api-keys → /v1/public/api-keys
- /v1/admin/subscription → /v1/public/subscription
- /v1/admin/profile → /v1/public/profile
- /v1/admin/settings → /v1/public/settings
- /v1/admin/github → /v1/public/github
- /v1/admin/load-testing → /v1/public/load-testing
- /v1/admin/sandbox → /v1/public/sandbox

**Python SDK Status:** Already compliant - no changes needed.

## [3.0.0] - 2026-01-09 🚨 BREAKING CHANGES

### 🔴 BREAKING CHANGES - API Endpoint Path Updates (Issue #738)

This release updates all SDK endpoint paths to use canonical API routes following the backend API cleanup (Issues #728-734). **All deprecated endpoint paths have been removed from the backend and will return 404 errors as of 2026-02-07.**

#### Changed Endpoint Paths

**ZeroDB Projects:**
- ❌ OLD: `/zerodb/projects/*`
- ✅ NEW: `/projects/*`

**ZeroDB Vectors:**
- ❌ OLD: `/zerodb/vectors/*`
- ✅ NEW: `/projects/{project_id}/database/vectors/*`
- 🔴 **BREAKING**: All vector methods now require `project_id` as first parameter

**ZeroDB Tables:**
- ❌ OLD: `/zerodb/tables/*`
- ✅ NEW: `/projects/{project_id}/database/tables/*`
- 🔴 **BREAKING**: All table methods now require `project_id` as first parameter

**ZeroDB Memory:**
- ❌ OLD: `/zerodb/memory/*`
- ✅ NEW: `/projects/{project_id}/database/memory/*`
- 🔴 **BREAKING**: All memory methods now require `project_id` as first parameter

**ZeroDB Analytics:**
- ❌ OLD: `/zerodb/analytics/*`
- ✅ NEW: `/projects/{project_id}/database/analytics/*`
- 🔴 **BREAKING**: All analytics methods now require `project_id` as first parameter

**Auth Endpoints:**
- ❌ OLD: `/public/auth/*`
- ✅ NEW: `/auth/*` (no changes required - already canonical)

### Migration Guide

#### Before (v2.x):
```python
from ainative import AINativeClient

client = AINativeClient(api_key="your-key")

# Old - NO project_id required
tables = client.zerodb.tables.list_tables()
vectors = client.zerodb.vectors.search(
    project_id="proj-123",
    vector=[0.1, 0.2, ...],
    top_k=10
)
```

#### After (v3.0):
```python
from ainative import AINativeClient

client = AINativeClient(api_key="your-key")

# New - project_id REQUIRED as first parameter
PROJECT_ID = "your-project-id"

tables = client.zerodb.tables.list_tables(PROJECT_ID)
vectors = client.zerodb.vectors.search(
    PROJECT_ID,  # Now first parameter
    vector=[0.1, 0.2, ...],
    top_k=10
)
```

### Updated Modules

#### `zerodb.projects.ProjectsClient`
- ✅ Updated base_path: `/zerodb/projects` → `/projects`
- ✅ All methods now use canonical `/projects/*` paths

#### `zerodb.vectors.VectorsClient`
- ✅ Updated base_path: `/zerodb/vectors` → `/projects`
- ✅ `upsert()` - Now uses `/projects/{project_id}/database/vectors`
- ✅ `search()` - Now uses `/projects/{project_id}/database/vectors/search`
- ✅ `get()` - Now uses `/projects/{project_id}/database/vectors`
- ✅ `delete()` - Now uses `/projects/{project_id}/database/vectors`
- ✅ `update_metadata()` - Now uses `/projects/{project_id}/database/vectors/{id}/metadata`
- ✅ `describe_index_stats()` - Now uses `/projects/{project_id}/database/vectors/stats`

#### `zerodb.tables.TablesClient`
- ✅ Updated base_path: `/zerodb/tables` → `/projects`
- 🔴 **BREAKING**: All methods now require `project_id` as first parameter
- Methods affected: `create_table`, `list_tables`, `get_table`, `delete_table`, `insert_rows`, `query_rows`, `update_rows`, `delete_rows`, `count_rows`, `table_exists`

#### `zerodb.memory.MemoryClient`
- ✅ Updated base_path: `/zerodb/memory` → `/projects`
- 🔴 **BREAKING**: All methods now require `project_id` as first parameter

#### `zerodb.analytics.AnalyticsClient`
- ✅ Updated base_path: `/zerodb/analytics` → `/projects`
- 🔴 **BREAKING**: All methods now require `project_id` as first parameter

### Important Dates

- **2026-01-09**: SDK v3.0.0 released with new canonical paths
- **2026-02-07**: Backend removes all deprecated paths (30-day grace period)
- **Action Required**: Update to SDK v3.0.0 before 2026-02-07

### References

- Issue #738: Python SDK Endpoint Path Updates
- Issue #728-734: Backend API Cleanup Phase 1
- API Migration Guide: `docs/api/API_MIGRATION_GUIDE_v2.md`
- SOW Alignment Audit: `docs/reports/SOW_ALIGNMENT_AUDIT_ISSUES_728_734.md`

---

## [2.0.0] - 2025-12-28

### Added - ZeroDB Local Support (Epic 3)

#### Local Environment Management
- **`local` command group** - Manage local ZeroDB environment
  - `local init` - Initialize local ZeroDB environment
  - `local up` - Start local Docker services
  - `local down` - Stop local Docker services
  - `local logs` - View local service logs
  - `local status` - Check local environment status
  - `local reset` - Reset local environment (wipe data)

#### Database Synchronization
- **`sync` command group** - Sync between local and cloud environments
  - `sync plan` - Preview database diff between local and cloud
  - `sync push` - Push local changes to cloud
  - `sync pull` - Pull cloud changes to local
  - `sync apply` - Apply pending sync plan
  - Smart conflict detection and resolution
  - Atomic sync operations with rollback support

#### Inspection & Debugging
- **`inspect` command group** - Inspect local database state
  - `inspect config` - Show local configuration
  - `inspect services` - Show Docker service status
  - `inspect db` - Show PostgreSQL database info
  - `inspect vectors` - Show Qdrant vector collections
  - `inspect sync` - Show sync state and history
  - Pretty-formatted output with JSON option

### Changed
- Updated package description to reflect ZeroDB Local support
- Enhanced CLI with modular command group architecture
- Improved error handling for local environment operations

### Technical Details
- Added `DatabaseDiff` utility for schema comparison
- Added `DiffFormatter` for human-readable diff output
- Integrated Docker Compose orchestration
- Added environment configuration management
- Enhanced client with local/cloud environment switching

## [1.0.0] - 2025-10-10

### Added
- Initial release of AINative Python SDK
- Complete API client for AINative Studio APIs
- Table operations with MongoDB-style query syntax
- Agent Swarm coordination and orchestration
- Authentication with API keys
- Comprehensive error handling
- Analytics and metrics commands
- CLI tool with `ainative` command

### Features
- Full async/await support
- Type safety with Pydantic models
- Retry logic with exponential backoff
- Rate limiting support
- Project and resource management
- Agent identity and learning systems

---

## Migration Guide

### Upgrading from 1.x to 2.0

**New Commands Available:**
```bash
# Local environment management
ainative local init
ainative local up
ainative local status

# Database synchronization
ainative sync plan
ainative sync push --dry-run
ainative sync pull

# Inspection and debugging
ainative inspect config
ainative inspect services
ainative inspect sync
```

**New Dependencies:**
- Docker and Docker Compose required for local environment
- Local environment runs PostgreSQL, Qdrant, MinIO, RedPanda

**Configuration:**
- Local environment config stored in `.zerodb/config.json`
- Environment variables for local/cloud switching
- See documentation for full setup guide

---

For more information, visit:
- Documentation: https://docs.ainative.studio/sdk/python
- GitHub: https://github.com/AINative-Studio/core
- Issues: https://github.com/AINative-Studio/core/issues
