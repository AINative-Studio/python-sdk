# AINative SDK - Table Operations Quick Reference

## Installation
```bash
pip install ainative-python>=0.2.0
```

## Setup
```python
from ainative import AINativeClient

client = AINativeClient(api_key="your_api_key")
tables = client.zerodb.tables  # Access table operations
```

## Table Management

### Create Table
```python
table = tables.create_table(
    "users",
    schema={
        "fields": {"email": "string", "name": "string", "age": "number"},
        "indexes": ["email"]
    }
)
```

### List Tables
```python
all_tables = tables.list_tables(limit=100, offset=0)
```

### Get Table
```python
table = tables.get_table("users")
```

### Delete Table
```python
result = tables.delete_table("users", confirm=True)  # confirm required
```

### Check Exists
```python
exists = tables.table_exists("users")  # Returns boolean
```

## Row Operations

### Insert
```python
result = tables.insert_rows("users", [
    {"email": "john@example.com", "name": "John", "age": 30},
    {"email": "jane@example.com", "name": "Jane", "age": 25}
])
# Max 1000 rows per request
```

### Query
```python
results = tables.query_rows(
    "users",
    filter={"age": {"$gte": 25}},
    sort={"age": -1},
    limit=10,
    offset=0,
    projection={"name": 1, "email": 1}
)
```

### Update
```python
result = tables.update_rows(
    "users",
    filter={"email": "john@example.com"},
    update={"$set": {"age": 31}},
    upsert=False
)
```

### Delete
```python
result = tables.delete_rows(
    "users",
    filter={"age": {"$lt": 18}},
    limit=0  # 0 = delete all matching
)
```

### Count
```python
total = tables.count_rows("users")
adults = tables.count_rows("users", filter={"age": {"$gte": 18}})
```

## Query Operators

### Comparison
```python
{"age": 30}                    # Equal
{"age": {"$gt": 25}}           # Greater than
{"age": {"$gte": 25}}          # Greater than or equal
{"age": {"$lt": 65}}           # Less than
{"age": {"$lte": 65}}          # Less than or equal
{"status": {"$ne": "deleted"}} # Not equal
{"status": {"$in": ["active", "pending"]}}     # In
{"status": {"$nin": ["deleted", "banned"]}}    # Not in
```

### Logical
```python
# AND (implicit)
{"age": {"$gte": 25}, "active": True}

# AND (explicit)
{"$and": [{"age": {"$gte": 25}}, {"active": True}]}

# OR
{"$or": [{"age": {"$lt": 18}}, {"age": {"$gt": 65}}]}

# NOT
{"age": {"$not": {"$gte": 18}}}

# Complex
{
    "$and": [
        {"age": {"$gte": 25}},
        {"$or": [{"premium": True}, {"verified": True}]}
    ]
}
```

### Update Operators
```python
{"$set": {"age": 31}}                    # Set value
{"$inc": {"age": 1}}                     # Increment
{"$mul": {"price": 1.1}}                 # Multiply
{"$unset": {"temp_field": ""}}           # Remove field
{"$push": {"tags": "new_tag"}}           # Add to array
{"$pull": {"tags": "old_tag"}}           # Remove from array
```

## Common Patterns

### Pagination
```python
offset = 0
limit = 100
all_data = []

while True:
    batch = tables.query_rows("users", limit=limit, offset=offset)
    all_data.extend(batch['rows'])
    if not batch['has_more']:
        break
    offset += limit
```

### Batch Insert
```python
large_dataset = [...]  # Your data
batch_size = 100

for i in range(0, len(large_dataset), batch_size):
    batch = large_dataset[i:i+batch_size]
    tables.insert_rows("users", batch)
```

### Upsert Pattern
```python
tables.update_rows(
    "users",
    filter={"email": "user@example.com"},
    update={"$set": {"name": "New Name", "updated_at": "2025-01-17"}},
    upsert=True  # Insert if not exists
)
```

### Conditional Update
```python
# Only update if age < 100
tables.update_rows(
    "users",
    filter={"email": "user@example.com", "age": {"$lt": 100}},
    update={"$inc": {"age": 1}}
)
```

### Field Projection
```python
# Only return name and email
results = tables.query_rows(
    "users",
    projection={"name": 1, "email": 1, "_id": 0}
)
```

## Error Handling

```python
from ainative.exceptions import APIError, ValidationError

try:
    result = tables.insert_rows("users", rows)

except ValidationError as e:
    print(f"Validation error: {e}")

except APIError as e:
    if e.status_code == 409:
        print("Conflict - table/row already exists")
    elif e.status_code == 404:
        print("Table not found")
    else:
        print(f"API error: {e}")

except ValueError as e:
    print(f"Invalid input: {e}")
```

## Field Types

```python
schema = {
    "fields": {
        "string_field": "string",
        "number_field": "number",
        "boolean_field": "boolean",
        "array_field": "array",
        "object_field": "object"
    },
    "indexes": ["string_field", "number_field"]  # Optional indexes
}
```

## Limits & Constraints

- **Max rows per insert:** 1000
- **Max query limit:** 10000 (use pagination)
- **Default query limit:** 100
- **Table name:** Alphanumeric + underscore
- **Field names:** No special characters
- **Indexes:** Recommended for frequently queried fields

## Complete Example

```python
from ainative import AINativeClient

# Initialize
client = AINativeClient(api_key="your_api_key")

# Create table
client.zerodb.tables.create_table(
    "products",
    schema={
        "fields": {
            "sku": "string",
            "name": "string",
            "price": "number",
            "in_stock": "boolean",
            "tags": "array"
        },
        "indexes": ["sku", "price"]
    }
)

# Insert products
client.zerodb.tables.insert_rows("products", [
    {"sku": "PROD-001", "name": "Widget", "price": 19.99, "in_stock": True, "tags": ["new"]},
    {"sku": "PROD-002", "name": "Gadget", "price": 29.99, "in_stock": True, "tags": ["sale"]},
    {"sku": "PROD-003", "name": "Gizmo", "price": 9.99, "in_stock": False, "tags": ["clearance"]}
])

# Query in-stock products under $25
products = client.zerodb.tables.query_rows(
    "products",
    filter={
        "in_stock": True,
        "price": {"$lt": 25}
    },
    sort={"price": 1}  # Ascending
)

# Update price
client.zerodb.tables.update_rows(
    "products",
    filter={"sku": "PROD-001"},
    update={"$set": {"price": 17.99}}
)

# Count in-stock
in_stock_count = client.zerodb.tables.count_rows(
    "products",
    filter={"in_stock": True}
)
print(f"In stock: {in_stock_count}")

# Delete out-of-stock
client.zerodb.tables.delete_rows(
    "products",
    filter={"in_stock": False}
)
```

## More Resources

- **Full Guide:** [TABLE_OPERATIONS.md](TABLE_OPERATIONS.md)
- **Examples:** [examples/table_operations_example.py](examples/table_operations_example.py)
- **API Docs:** https://api.ainative.studio/docs-enhanced
- **Support:** https://github.com/AINative-Studio/core/issues
