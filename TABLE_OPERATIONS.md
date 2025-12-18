# ZeroDB Table Operations - Python SDK

Complete guide to using NoSQL table operations in the AINative Python SDK.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Table Management](#table-management)
- [Row Operations](#row-operations)
- [Query Filters](#query-filters)
- [Best Practices](#best-practices)
- [Error Handling](#error-handling)
- [API Reference](#api-reference)

## Overview

The ZeroDB Table Operations provide a flexible NoSQL database interface with:

- **Schema-based tables** with field type validation
- **MongoDB-style queries** with rich filtering capabilities
- **CRUD operations** for both tables and rows
- **Indexing support** for optimized queries
- **Batch operations** for high-performance inserts
- **Pagination** for handling large datasets

## Installation

```bash
pip install ainative-python
```

Or from source:

```bash
git clone https://github.com/ainative/ainative-python.git
cd ainative-python
pip install -e .
```

## Quick Start

```python
from ainative import AINativeClient

# Initialize client
client = AINativeClient(api_key="your_api_key")

# Create a table
table = client.zerodb.tables.create_table(
    "users",
    schema={
        "fields": {"email": "string", "name": "string", "age": "number"},
        "indexes": ["email"]
    }
)

# Insert rows
result = client.zerodb.tables.insert_rows("users", [
    {"email": "user@example.com", "name": "John", "age": 30}
])

# Query rows
users = client.zerodb.tables.query_rows(
    "users",
    filter={"age": {"$gte": 25}},
    sort={"created_at": -1},
    limit=10
)

# Update rows
client.zerodb.tables.update_rows(
    "users",
    filter={"email": "user@example.com"},
    update={"$set": {"age": 31}}
)

# Delete rows
client.zerodb.tables.delete_rows(
    "users",
    filter={"age": {"$lt": 18}}
)
```

## Table Management

### Create Table

Create a new table with a defined schema:

```python
table = client.zerodb.tables.create_table(
    table_name="users",
    schema={
        "fields": {
            "email": "string",
            "name": "string",
            "age": "number",
            "active": "boolean",
            "tags": "array",
            "metadata": "object"
        },
        "indexes": ["email", "age"]  # Optional: fields to index
    },
    description="User data table"  # Optional
)

# Response
# {
#     "table_id": "550e8400-e29b-41d4-a716-446655440000",
#     "table_name": "users",
#     "status": "created",
#     "created_at": "2025-01-14T10:00:00Z"
# }
```

**Supported Field Types:**
- `string` - Text data
- `number` - Integers and floats
- `boolean` - True/False
- `array` - Lists
- `object` - Nested objects/dictionaries

### List Tables

Get all tables in your project:

```python
tables = client.zerodb.tables.list_tables(
    limit=100,   # Max results per page
    offset=0     # Pagination offset
)

# Response
# {
#     "tables": [
#         {
#             "table_id": "id1",
#             "table_name": "users",
#             "row_count": 1000,
#             "created_at": "2025-01-14T10:00:00Z"
#         },
#         ...
#     ],
#     "total": 5
# }

# Iterate through tables
for table in tables['tables']:
    print(f"{table['table_name']}: {table['row_count']} rows")
```

### Get Table Details

Retrieve table metadata and schema:

```python
table = client.zerodb.tables.get_table("users")

# Response
# {
#     "table_id": "550e8400-e29b-41d4-a716-446655440000",
#     "table_name": "users",
#     "schema": {...},
#     "row_count": 1000,
#     "created_at": "2025-01-14T10:00:00Z",
#     "updated_at": "2025-01-14T12:00:00Z"
# }
```

### Delete Table

Delete a table and all its data:

```python
# Requires explicit confirmation for safety
result = client.zerodb.tables.delete_table(
    "old_table",
    confirm=True  # Must be True
)

# Response
# {
#     "status": "deleted",
#     "rows_deleted": 1000,
#     "table_name": "old_table"
# }
```

### Check if Table Exists

```python
exists = client.zerodb.tables.table_exists("users")
# Returns: True or False
```

## Row Operations

### Insert Rows

Insert one or more rows into a table:

```python
rows = [
    {"email": "user1@example.com", "name": "John", "age": 30},
    {"email": "user2@example.com", "name": "Jane", "age": 25}
]

result = client.zerodb.tables.insert_rows(
    "users",
    rows,
    return_ids=True  # Optional: return inserted row IDs
)

# Response
# {
#     "inserted_count": 2,
#     "inserted_ids": ["row_id_1", "row_id_2"],
#     "failed_count": 0,
#     "status": "success"
# }
```

**Limitations:**
- Maximum 1000 rows per request
- For larger datasets, use batch processing

### Query Rows

Query rows with filtering, sorting, and pagination:

```python
results = client.zerodb.tables.query_rows(
    "users",
    filter={"age": {"$gte": 25}},  # MongoDB-style filters
    sort={"age": -1},               # -1 = descending, 1 = ascending
    limit=100,
    offset=0,
    projection={"name": 1, "email": 1, "_id": 0}  # Optional: field selection
)

# Response
# {
#     "rows": [
#         {
#             "row_id": "id1",
#             "data": {"email": "user@example.com", "name": "John", "age": 30},
#             "created_at": "2025-01-14T10:00:00Z"
#         },
#         ...
#     ],
#     "total": 150,
#     "has_more": True,
#     "offset": 0,
#     "limit": 100
# }
```

### Update Rows

Update rows matching a filter:

```python
result = client.zerodb.tables.update_rows(
    "users",
    filter={"email": "user@example.com"},
    update={"$set": {"age": 31}},
    upsert=False  # Optional: insert if not found
)

# Response
# {
#     "modified_count": 1,
#     "matched_count": 1,
#     "status": "success"
# }
```

**Update Operators:**
```python
# Set fields
update={"$set": {"age": 31, "active": True}}

# Increment/decrement
update={"$inc": {"age": 1, "login_count": 1}}

# Multiply
update={"$mul": {"price": 1.1}}

# Unset (remove) fields
update={"$unset": {"temp_field": ""}}

# Add to array
update={"$push": {"tags": "new_tag"}}

# Remove from array
update={"$pull": {"tags": "old_tag"}}
```

### Delete Rows

Delete rows matching a filter:

```python
result = client.zerodb.tables.delete_rows(
    "users",
    filter={"age": {"$lt": 18}},
    limit=0  # 0 = delete all matching, or specify a limit
)

# Response
# {
#     "deleted_count": 5,
#     "status": "success"
# }
```

### Count Rows

Count rows matching an optional filter:

```python
# Count all rows
total = client.zerodb.tables.count_rows("users")

# Count with filter
adults = client.zerodb.tables.count_rows(
    "users",
    filter={"age": {"$gte": 18}}
)
```

## Query Filters

MongoDB-style query operators:

### Comparison Operators

```python
# Equals
filter={"age": 30}

# Greater than / Greater than or equal
filter={"age": {"$gt": 25}}
filter={"age": {"$gte": 25}}

# Less than / Less than or equal
filter={"age": {"$lt": 65}}
filter={"age": {"$lte": 65}}

# Not equal
filter={"status": {"$ne": "deleted"}}

# In array
filter={"status": {"$in": ["active", "pending"]}}

# Not in array
filter={"status": {"$nin": ["deleted", "banned"]}}
```

### Logical Operators

```python
# AND (implicit)
filter={
    "age": {"$gte": 25},
    "active": True
}

# AND (explicit)
filter={
    "$and": [
        {"age": {"$gte": 25}},
        {"active": True}
    ]
}

# OR
filter={
    "$or": [
        {"age": {"$lt": 18}},
        {"age": {"$gt": 65}}
    ]
}

# NOT
filter={
    "age": {"$not": {"$gte": 18}}
}

# Complex combination
filter={
    "$and": [
        {"age": {"$gte": 25}},
        {"$or": [
            {"status": "premium"},
            {"verified": True}
        ]}
    ]
}
```

### Element Operators

```python
# Field exists
filter={"email": {"$exists": True}}

# Type check
filter={"age": {"$type": "number"}}
```

### Array Operators

```python
# Array contains element
filter={"tags": {"$in": ["premium"]}}

# Array contains all
filter={"tags": {"$all": ["verified", "premium"]}}

# Array size
filter={"tags": {"$size": 2}}
```

## Best Practices

### 1. Schema Design

```python
# ✅ Good: Clear, typed schema
schema = {
    "fields": {
        "user_id": "string",      # Primary identifier
        "email": "string",         # Indexed field
        "name": "string",
        "age": "number",
        "created_at": "string",    # ISO timestamp
        "metadata": "object"       # Flexible nested data
    },
    "indexes": ["user_id", "email"]  # Index frequently queried fields
}

# ❌ Bad: Unstructured, no indexes
schema = {
    "fields": {"data": "object"},
    "indexes": []
}
```

### 2. Batch Operations

```python
# ✅ Good: Batch insert
large_dataset = [...]  # 1000 items
for i in range(0, len(large_dataset), 100):
    batch = large_dataset[i:i+100]
    client.zerodb.tables.insert_rows("users", batch)

# ❌ Bad: Individual inserts
for item in large_dataset:
    client.zerodb.tables.insert_rows("users", [item])  # Too many API calls
```

### 3. Query Optimization

```python
# ✅ Good: Use projection to limit returned fields
users = client.zerodb.tables.query_rows(
    "users",
    projection={"name": 1, "email": 1, "_id": 0},
    limit=50
)

# ❌ Bad: Retrieve all fields when not needed
users = client.zerodb.tables.query_rows("users", limit=1000)
```

### 4. Pagination

```python
# ✅ Good: Paginate large result sets
offset = 0
limit = 100
all_users = []

while True:
    batch = client.zerodb.tables.query_rows(
        "users",
        limit=limit,
        offset=offset
    )
    all_users.extend(batch['rows'])

    if not batch['has_more']:
        break

    offset += limit

# ❌ Bad: Load all data at once
users = client.zerodb.tables.query_rows("users", limit=100000)
```

### 5. Error Handling

```python
# ✅ Good: Handle errors gracefully
try:
    result = client.zerodb.tables.insert_rows("users", rows)
    if result['failed_count'] > 0:
        for error in result['failed']:
            print(f"Row {error['index']} failed: {error['error']}")
except Exception as e:
    print(f"Insert failed: {e}")

# ❌ Bad: No error handling
result = client.zerodb.tables.insert_rows("users", rows)
```

## Error Handling

Common errors and how to handle them:

```python
from ainative.exceptions import APIError, ValidationError

try:
    # Table operations
    table = client.zerodb.tables.create_table("users", schema)

except ValidationError as e:
    # Schema validation failed
    print(f"Invalid schema: {e}")

except APIError as e:
    # API-level error
    if e.status_code == 409:
        print("Table already exists")
    elif e.status_code == 404:
        print("Table not found")
    else:
        print(f"API error: {e}")

except Exception as e:
    # Unexpected error
    print(f"Unexpected error: {e}")
```

## API Reference

### TablesClient Methods

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `create_table()` | Create a new table | `table_name`, `schema`, `description?` | Table info |
| `list_tables()` | List all tables | `limit?`, `offset?` | Tables list |
| `get_table()` | Get table details | `table_id` | Table details |
| `delete_table()` | Delete table | `table_id`, `confirm` | Delete result |
| `insert_rows()` | Insert rows | `table_name`, `rows`, `return_ids?` | Insert result |
| `query_rows()` | Query rows | `table_name`, `filter?`, `sort?`, `limit?`, `offset?`, `projection?` | Query results |
| `update_rows()` | Update rows | `table_name`, `filter`, `update`, `upsert?` | Update result |
| `delete_rows()` | Delete rows | `table_name`, `filter`, `limit?` | Delete result |
| `count_rows()` | Count rows | `table_name`, `filter?` | Count (int) |
| `table_exists()` | Check existence | `table_name` | Boolean |

### Complete Example

See the full example in `examples/table_operations_example.py`:

```bash
python examples/table_operations_example.py
```

## Support

- **Documentation**: https://docs.ainative.studio/sdk/python/tables
- **API Reference**: https://api.ainative.studio/docs-enhanced
- **GitHub**: https://github.com/ainative/ainative-python
- **Issues**: https://github.com/ainative/studio/issues

## License

MIT License - see LICENSE file for details
