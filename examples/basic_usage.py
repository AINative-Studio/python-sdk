#!/usr/bin/env python3
"""
Basic Usage Example for AINative Python SDK

This example demonstrates the fundamental operations of the AINative SDK.
"""

import os
from ainative import AINativeClient
from ainative.zerodb.memory import MemoryPriority


def main():
    # Initialize client using environment variable or direct API key
    api_key = os.getenv("AINATIVE_API_KEY", "your-api-key-here")
    
    # Create client instance
    client = AINativeClient(api_key=api_key)
    
    print("🚀 AINative SDK Basic Usage Example\n")
    
    try:
        # 1. Health Check
        print("1. Checking API health...")
        health = client.health_check()
        print(f"   ✅ API Status: {health.get('status', 'unknown')}\n")
        
        # 2. Create a Project
        print("2. Creating a new project...")
        project = client.zerodb.projects.create(
            name="SDK Demo Project",
            description="Created via Python SDK example",
            metadata={
                "environment": "development",
                "version": "1.0.0"
            }
        )
        project_id = project["id"]
        print(f"   ✅ Project created: {project_id}\n")
        
        # 3. Store Some Vectors
        print("3. Storing vectors...")
        vectors = [
            [0.1, 0.2, 0.3, 0.4, 0.5],
            [0.2, 0.3, 0.4, 0.5, 0.6],
            [0.3, 0.4, 0.5, 0.6, 0.7],
        ]
        metadata = [
            {"text": "Hello world", "category": "greeting"},
            {"text": "Python SDK", "category": "technology"},
            {"text": "Vector database", "category": "technology"},
        ]
        
        upsert_result = client.zerodb.vectors.upsert(
            project_id=project_id,
            vectors=vectors,
            metadata=metadata,
            namespace="examples"
        )
        print(f"   ✅ Stored {len(vectors)} vectors\n")
        
        # 4. Search Vectors
        print("4. Searching for similar vectors...")
        query_vector = [0.15, 0.25, 0.35, 0.45, 0.55]
        search_results = client.zerodb.vectors.search(
            project_id=project_id,
            vector=query_vector,
            top_k=2,
            namespace="examples"
        )
        print(f"   ✅ Found {len(search_results)} similar vectors")
        for i, result in enumerate(search_results, 1):
            print(f"      {i}. Score: {result.get('score', 0):.3f}, "
                  f"Text: {result.get('metadata', {}).get('text', 'N/A')}")
        print()
        
        # 5. Create Memory Entries
        print("5. Creating memory entries...")
        memory1 = client.zerodb.memory.create(
            content="The SDK was initialized successfully with project " + project_id,
            title="SDK Initialization",
            tags=["sdk", "initialization", "example"],
            priority=MemoryPriority.HIGH,
            project_id=project_id
        )
        
        memory2 = client.zerodb.memory.create(
            content="Vectors can be stored and searched efficiently using the ZeroDB module",
            title="Vector Operations",
            tags=["vectors", "search", "example"],
            priority=MemoryPriority.MEDIUM,
            project_id=project_id
        )
        print(f"   ✅ Created 2 memory entries\n")
        
        # 6. Search Memories
        print("6. Searching memories...")
        memory_results = client.zerodb.memory.search(
            query="SDK initialization",
            project_id=project_id,
            semantic=True,
            limit=5
        )
        print(f"   ✅ Found {len(memory_results)} relevant memories\n")
        
        # 7. Get Project Statistics
        print("7. Getting project statistics...")
        stats = client.zerodb.projects.get_statistics(project_id)
        print(f"   ✅ Project Statistics:")
        print(f"      - Vectors: {stats.get('vector_count', 0)}")
        print(f"      - Memories: {stats.get('memory_count', 0)}")
        print(f"      - Storage: {stats.get('storage_bytes', 0)} bytes\n")
        
        # 8. Get Usage Analytics
        print("8. Getting usage analytics...")
        usage = client.zerodb.analytics.get_usage(project_id=project_id)
        print(f"   ✅ Usage data retrieved\n")
        
        # 9. Clean Up (Optional)
        print("9. Cleaning up...")
        # Uncomment to delete the project
        # client.zerodb.projects.delete(project_id)
        # print(f"   ✅ Project {project_id} deleted\n")
        
        print("✨ Basic usage example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Close client connection
        client.close()


if __name__ == "__main__":
    main()