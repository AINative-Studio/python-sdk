# Changelog

All notable changes to the AINative Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- GitHub: https://github.com/ainative/ainative-python
- Issues: https://github.com/ainative/studio/issues
