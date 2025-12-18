"""
AINative SDK - Table Operations Examples

This example demonstrates how to use the Table Operations in the AINative Python SDK.
"""

from ainative import AINativeClient
import os


def main():
    """
    Complete example of using ZeroDB Table Operations
    """

    # Initialize the client
    api_key = os.getenv("AINATIVE_API_KEY")
    if not api_key:
        print("Please set AINATIVE_API_KEY environment variable")
        return

    client = AINativeClient(api_key=api_key)

    # ========================================
    # 1. Create a Table
    # ========================================
    print("1. Creating a table...")

    table_schema = {
        "fields": {
            "email": "string",
            "name": "string",
            "age": "number",
            "active": "boolean",
            "tags": "array",
            "metadata": "object"
        },
        "indexes": ["email"]  # Index the email field for faster queries
    }

    try:
        table = client.zerodb.tables.create_table(
            table_name="users",
            schema=table_schema,
            description="User data table"
        )
        print(f"✓ Table created: {table['table_name']} (ID: {table['table_id']})")
    except Exception as e:
        print(f"Table already exists or error: {e}")

    # ========================================
    # 2. List All Tables
    # ========================================
    print("\n2. Listing all tables...")

    tables = client.zerodb.tables.list_tables(limit=10)
    print(f"✓ Found {tables['total']} tables:")
    for table in tables['tables']:
        print(f"  - {table['table_name']}: {table['row_count']} rows")

    # ========================================
    # 3. Insert Rows
    # ========================================
    print("\n3. Inserting rows...")

    users = [
        {
            "email": "john.doe@example.com",
            "name": "John Doe",
            "age": 30,
            "active": True,
            "tags": ["premium", "verified"],
            "metadata": {"signup_date": "2025-01-01", "referral": "organic"}
        },
        {
            "email": "jane.smith@example.com",
            "name": "Jane Smith",
            "age": 25,
            "active": True,
            "tags": ["verified"],
            "metadata": {"signup_date": "2025-01-05", "referral": "paid"}
        },
        {
            "email": "bob.johnson@example.com",
            "name": "Bob Johnson",
            "age": 35,
            "active": False,
            "tags": ["premium"],
            "metadata": {"signup_date": "2024-12-20", "referral": "organic"}
        }
    ]

    result = client.zerodb.tables.insert_rows("users", users)
    print(f"✓ Inserted {result['inserted_count']} rows")
    print(f"  Row IDs: {result['inserted_ids'][:3]}...")

    # ========================================
    # 4. Query Rows - Basic
    # ========================================
    print("\n4. Querying all users...")

    all_users = client.zerodb.tables.query_rows("users", limit=10)
    print(f"✓ Found {all_users['total']} users")
    for row in all_users['rows']:
        user = row['data']
        print(f"  - {user['name']} ({user['email']}): {user['age']} years old")

    # ========================================
    # 5. Query Rows - With Filter
    # ========================================
    print("\n5. Querying active users over 25...")

    active_users = client.zerodb.tables.query_rows(
        "users",
        filter={
            "age": {"$gte": 25},
            "active": True
        }
    )
    print(f"✓ Found {active_users['total']} active users over 25")
    for row in active_users['rows']:
        user = row['data']
        print(f"  - {user['name']}: {user['age']} years old")

    # ========================================
    # 6. Query Rows - With Sorting
    # ========================================
    print("\n6. Querying users sorted by age (descending)...")

    sorted_users = client.zerodb.tables.query_rows(
        "users",
        sort={"age": -1},  # -1 for descending, 1 for ascending
        limit=5
    )
    print(f"✓ Top users by age:")
    for row in sorted_users['rows']:
        user = row['data']
        print(f"  - {user['name']}: {user['age']} years old")

    # ========================================
    # 7. Query Rows - With Projection
    # ========================================
    print("\n7. Querying users (name and email only)...")

    projected_users = client.zerodb.tables.query_rows(
        "users",
        projection={"name": 1, "email": 1, "_id": 0}
    )
    print(f"✓ Users (projected fields):")
    for row in projected_users['rows']:
        user = row['data']
        print(f"  - {user.get('name')}: {user.get('email')}")

    # ========================================
    # 8. Count Rows
    # ========================================
    print("\n8. Counting rows...")

    total_count = client.zerodb.tables.count_rows("users")
    print(f"✓ Total users: {total_count}")

    active_count = client.zerodb.tables.count_rows(
        "users",
        filter={"active": True}
    )
    print(f"✓ Active users: {active_count}")

    # ========================================
    # 9. Update Rows
    # ========================================
    print("\n9. Updating user age...")

    update_result = client.zerodb.tables.update_rows(
        "users",
        filter={"email": "john.doe@example.com"},
        update={"$set": {"age": 31}}
    )
    print(f"✓ Updated {update_result['modified_count']} users")

    # Verify the update
    updated_user = client.zerodb.tables.query_rows(
        "users",
        filter={"email": "john.doe@example.com"}
    )
    if updated_user['rows']:
        user = updated_user['rows'][0]['data']
        print(f"  - {user['name']} is now {user['age']} years old")

    # ========================================
    # 10. Update with Increment
    # ========================================
    print("\n10. Incrementing age for all users...")

    increment_result = client.zerodb.tables.update_rows(
        "users",
        filter={},  # Match all users
        update={"$inc": {"age": 1}}  # Increment age by 1
    )
    print(f"✓ Incremented age for {increment_result['modified_count']} users")

    # ========================================
    # 11. Update with Upsert
    # ========================================
    print("\n11. Updating with upsert (insert if not exists)...")

    upsert_result = client.zerodb.tables.update_rows(
        "users",
        filter={"email": "new.user@example.com"},
        update={
            "$set": {
                "email": "new.user@example.com",
                "name": "New User",
                "age": 28,
                "active": True
            }
        },
        upsert=True
    )
    print(f"✓ Upsert result: {upsert_result}")

    # ========================================
    # 12. Delete Rows
    # ========================================
    print("\n12. Deleting inactive users...")

    delete_result = client.zerodb.tables.delete_rows(
        "users",
        filter={"active": False}
    )
    print(f"✓ Deleted {delete_result['deleted_count']} inactive users")

    # ========================================
    # 13. Get Table Details
    # ========================================
    print("\n13. Getting table details...")

    table_details = client.zerodb.tables.get_table("users")
    print(f"✓ Table: {table_details['table_name']}")
    print(f"  - Rows: {table_details['row_count']}")
    print(f"  - Schema: {list(table_details['schema']['fields'].keys())}")
    print(f"  - Created: {table_details['created_at']}")

    # ========================================
    # 14. Check if Table Exists
    # ========================================
    print("\n14. Checking if tables exist...")

    users_exists = client.zerodb.tables.table_exists("users")
    print(f"✓ 'users' table exists: {users_exists}")

    fake_exists = client.zerodb.tables.table_exists("nonexistent_table")
    print(f"✓ 'nonexistent_table' exists: {fake_exists}")

    # ========================================
    # 15. Delete Table (Optional - Cleanup)
    # ========================================
    print("\n15. Cleanup: Deleting table (optional)...")

    cleanup = input("Do you want to delete the 'users' table? (yes/no): ")
    if cleanup.lower() == 'yes':
        delete_table_result = client.zerodb.tables.delete_table(
            "users",
            confirm=True  # Safety confirmation required
        )
        print(f"✓ Table deleted: {delete_table_result['status']}")
        print(f"  - Rows deleted: {delete_table_result['rows_deleted']}")
    else:
        print("✓ Skipping table deletion")

    print("\n" + "="*50)
    print("✓ All table operations completed successfully!")
    print("="*50)


def advanced_example():
    """
    Advanced example with complex queries
    """

    api_key = os.getenv("AINATIVE_API_KEY")
    client = AINativeClient(api_key=api_key)

    print("\n" + "="*50)
    print("ADVANCED TABLE OPERATIONS")
    print("="*50)

    # Complex query with multiple conditions
    print("\n1. Complex query with $and, $or operators...")

    complex_query = client.zerodb.tables.query_rows(
        "users",
        filter={
            "$and": [
                {"age": {"$gte": 25}},
                {"$or": [
                    {"tags": {"$in": ["premium"]}},
                    {"active": True}
                ]}
            ]
        },
        sort={"age": -1},
        limit=10
    )
    print(f"✓ Found {complex_query['total']} users matching complex criteria")

    # Batch insert with error handling
    print("\n2. Batch insert with large dataset...")

    large_dataset = [
        {
            "email": f"user{i}@example.com",
            "name": f"User {i}",
            "age": 20 + (i % 40),
            "active": i % 2 == 0
        }
        for i in range(100)
    ]

    # Insert in batches of 100
    batch_size = 100
    for i in range(0, len(large_dataset), batch_size):
        batch = large_dataset[i:i + batch_size]
        result = client.zerodb.tables.insert_rows("users", batch)
        print(f"✓ Inserted batch {i//batch_size + 1}: {result['inserted_count']} rows")

    # Aggregation-like query (count by condition)
    print("\n3. Aggregation: Count users by age groups...")

    age_groups = {
        "18-25": {"$gte": 18, "$lte": 25},
        "26-35": {"$gte": 26, "$lte": 35},
        "36+": {"$gte": 36}
    }

    for group_name, age_filter in age_groups.items():
        count = client.zerodb.tables.count_rows(
            "users",
            filter={"age": age_filter}
        )
        print(f"✓ {group_name}: {count} users")

    print("\n" + "="*50)
    print("✓ Advanced operations completed!")
    print("="*50)


if __name__ == "__main__":
    try:
        main()

        # Uncomment to run advanced examples
        # advanced_example()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
