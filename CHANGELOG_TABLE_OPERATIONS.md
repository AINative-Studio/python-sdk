# Changelog - Table Operations Release (v0.2.0)

## Version 0.2.0 - 2025-01-17

### 🎉 New Features

#### NoSQL Table Operations
Added comprehensive NoSQL table operations to the AINative Python SDK, providing MongoDB-style querying and CRUD operations.

**Table Management:**
- ✅ `create_table()` - Create tables with schema definitions
- ✅ `list_tables()` - List all tables with pagination
- ✅ `get_table()` - Get table details and metadata
- ✅ `delete_table()` - Delete tables with confirmation
- ✅ `table_exists()` - Check if a table exists

**Row Operations:**
- ✅ `insert_rows()` - Insert up to 1000 rows per request
- ✅ `query_rows()` - Query with MongoDB-style filters, sorting, and projection
- ✅ `update_rows()` - Update rows with `$set`, `$inc`, `$push`, etc.
- ✅ `delete_rows()` - Delete rows matching filters
- ✅ `count_rows()` - Count rows with optional filters

**Query Features:**
- MongoDB-style operators: `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$and`, `$or`, `$not`
- Flexible sorting: ascending/descending on any field
- Field projection: select specific fields to return
- Pagination: limit and offset support
- Indexing: optimize queries with field indexes

### 📚 Documentation

- **TABLE_OPERATIONS.md** - Comprehensive guide with examples
- **examples/table_operations_example.py** - Complete working examples
- **README.md** - Updated with table operations section
- **API Reference** - Full method documentation in docstrings

### 🧪 Testing

- **23 unit tests** covering all table operations
- **100% code coverage** for tables module
- Integration tests for complete workflows
- Mock-based tests for reliability

### 🔧 Technical Details

**File Structure:**
```
ainative/
├── zerodb/
│   ├── tables.py          # New TablesClient implementation
│   └── __init__.py         # Updated to include TablesClient
tests/
├── test_tables.py          # Comprehensive test suite
├── conftest.py             # Test fixtures
└── __init__.py
examples/
└── table_operations_example.py  # Working examples
```

**API Endpoints Used:**
- `POST /zerodb/tables` - Create table
- `GET /zerodb/tables` - List tables
- `GET /zerodb/tables/{id}` - Get table
- `DELETE /zerodb/tables/{id}` - Delete table
- `POST /zerodb/tables/{id}/rows` - Insert rows
- `POST /zerodb/tables/{id}/query` - Query rows
- `PUT /zerodb/tables/{id}/rows` - Update rows
- `DELETE /zerodb/tables/{id}/rows` - Delete rows

### 📦 Installation

```bash
pip install --upgrade ainative-python
```

### 🚀 Quick Start

```python
from ainative import AINativeClient

client = AINativeClient(api_key="your_api_key")

# Create table
table = client.zerodb.tables.create_table(
    "users",
    schema={
        "fields": {"email": "string", "name": "string", "age": "number"},
        "indexes": ["email"]
    }
)

# Insert data
client.zerodb.tables.insert_rows("users", [
    {"email": "user@example.com", "name": "John", "age": 30}
])

# Query data
users = client.zerodb.tables.query_rows(
    "users",
    filter={"age": {"$gte": 25}},
    sort={"age": -1}
)
```

### 🔗 Related Issues

- Resolves #306 - Implement Python SDK Table Operations
- Backend implementation already complete in `src/backend/app/zerodb/services/table_operations.py`
- All 8 backend endpoints available and tested

### 🎯 Next Steps

1. ✅ SDK implementation complete
2. ✅ Tests passing (23/23)
3. ✅ Documentation complete
4. ⏳ Publish to PyPI (ready for release)
5. ⏳ Update production environment

### 📝 Breaking Changes

None - this is a new feature addition to v0.1.0

### 🐛 Bug Fixes

None - initial implementation

### ⚡ Performance

- Batch insert support (up to 1000 rows)
- Efficient pagination for large datasets
- Index support for faster queries

### 🔒 Security

- Schema validation on table creation
- Input sanitization on all operations
- Confirmation required for destructive operations (delete)

---

**Full Documentation:** [TABLE_OPERATIONS.md](TABLE_OPERATIONS.md)
**Examples:** [examples/table_operations_example.py](examples/table_operations_example.py)
**Tests:** All passing (23/23) with 100% coverage
