#!/usr/bin/env python3
"""
Vector Search Example for AINative Python SDK

Demonstrates advanced vector operations including batch processing,
filtering, and namespace management.
"""

import os
import time
import numpy as np
from ainative import AINativeClient


def generate_embeddings(texts, dimension=768):
    """
    Simulate generating embeddings from text.
    In production, use a real embedding model like OpenAI or Sentence Transformers.
    """
    np.random.seed(42)  # For reproducible examples
    embeddings = []
    for text in texts:
        # Simple hash-based pseudo-embedding for demonstration
        hash_val = hash(text) % 1000
        base_vector = np.random.randn(dimension) * 0.1
        base_vector[hash_val % dimension] += 0.5  # Make vectors somewhat unique
        embeddings.append(base_vector.tolist())
    return embeddings


def main():
    # Initialize client
    api_key = os.getenv("AINATIVE_API_KEY", "your-api-key-here")
    client = AINativeClient(api_key=api_key)
    
    print("🔍 AINative Vector Search Example\n")
    
    try:
        # Create a project for this example
        print("Setting up project...")
        project = client.zerodb.projects.create(
            name="Vector Search Demo",
            description="Advanced vector search operations",
            config={
                "vector_dimension": 768,
                "distance_metric": "cosine"
            }
        )
        project_id = project["id"]
        print(f"✅ Project created: {project_id}\n")
        
        # Prepare sample documents
        documents = [
            # Technology category
            {"id": "doc1", "text": "Python is a versatile programming language", "category": "technology", "language": "en"},
            {"id": "doc2", "text": "Machine learning transforms data into insights", "category": "technology", "language": "en"},
            {"id": "doc3", "text": "Cloud computing enables scalable applications", "category": "technology", "language": "en"},
            {"id": "doc4", "text": "APIs connect different software systems", "category": "technology", "language": "en"},
            
            # Science category
            {"id": "doc5", "text": "Quantum physics explores subatomic particles", "category": "science", "language": "en"},
            {"id": "doc6", "text": "DNA contains genetic instructions for life", "category": "science", "language": "en"},
            {"id": "doc7", "text": "Climate change affects global weather patterns", "category": "science", "language": "en"},
            
            # Business category
            {"id": "doc8", "text": "Strategic planning drives business growth", "category": "business", "language": "en"},
            {"id": "doc9", "text": "Market analysis reveals consumer trends", "category": "business", "language": "en"},
            {"id": "doc10", "text": "Innovation creates competitive advantages", "category": "business", "language": "en"},
        ]
        
        # Generate embeddings
        print("Generating embeddings...")
        texts = [doc["text"] for doc in documents]
        embeddings = generate_embeddings(texts, dimension=768)
        print(f"✅ Generated {len(embeddings)} embeddings\n")
        
        # Batch upsert vectors with metadata
        print("Upserting vectors in batches...")
        batch_size = 5
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_embeddings = embeddings[i:i+batch_size]
            batch_ids = [doc["id"] for doc in batch_docs]
            batch_metadata = [
                {
                    "text": doc["text"],
                    "category": doc["category"],
                    "language": doc["language"],
                    "timestamp": int(time.time())
                }
                for doc in batch_docs
            ]
            
            client.zerodb.vectors.upsert(
                project_id=project_id,
                vectors=batch_embeddings,
                metadata=batch_metadata,
                ids=batch_ids,
                namespace="documents"
            )
            print(f"   Batch {i//batch_size + 1}: Upserted {len(batch_docs)} vectors")
        print(f"✅ Total vectors upserted: {len(documents)}\n")
        
        # Get index statistics
        print("Index Statistics:")
        stats = client.zerodb.vectors.describe_index_stats(
            project_id=project_id,
            namespace="documents"
        )
        print(f"   Total vectors: {stats.get('total_vectors', 0)}")
        print(f"   Dimensions: {stats.get('dimension', 0)}")
        print(f"   Index size: {stats.get('index_size_bytes', 0)} bytes\n")
        
        # Perform various searches
        print("Performing searches...\n")
        
        # 1. Basic similarity search
        query = "How does artificial intelligence work?"
        print(f"1. Basic search: '{query}'")
        query_embedding = generate_embeddings([query], dimension=768)[0]
        results = client.zerodb.vectors.search(
            project_id=project_id,
            vector=query_embedding,
            top_k=3,
            namespace="documents"
        )
        print(f"   Top {len(results)} results:")
        for idx, result in enumerate(results, 1):
            text = result.get("metadata", {}).get("text", "N/A")
            score = result.get("score", 0)
            print(f"   {idx}. (Score: {score:.3f}) {text}")
        print()
        
        # 2. Filtered search by category
        query = "data analysis and insights"
        print(f"2. Filtered search: '{query}' (category=technology)")
        query_embedding = generate_embeddings([query], dimension=768)[0]
        results = client.zerodb.vectors.search(
            project_id=project_id,
            vector=query_embedding,
            top_k=3,
            namespace="documents",
            filter={"category": "technology"}
        )
        print(f"   Top {len(results)} technology results:")
        for idx, result in enumerate(results, 1):
            text = result.get("metadata", {}).get("text", "N/A")
            score = result.get("score", 0)
            print(f"   {idx}. (Score: {score:.3f}) {text}")
        print()
        
        # 3. Multi-filter search
        query = "innovation and growth"
        print(f"3. Multi-filter search: '{query}' (category=business, language=en)")
        query_embedding = generate_embeddings([query], dimension=768)[0]
        results = client.zerodb.vectors.search(
            project_id=project_id,
            vector=query_embedding,
            top_k=3,
            namespace="documents",
            filter={"category": "business", "language": "en"}
        )
        print(f"   Top {len(results)} business results:")
        for idx, result in enumerate(results, 1):
            text = result.get("metadata", {}).get("text", "N/A")
            score = result.get("score", 0)
            print(f"   {idx}. (Score: {score:.3f}) {text}")
        print()
        
        # 4. Get specific vectors by ID
        print("4. Fetching specific vectors by ID...")
        specific_ids = ["doc1", "doc5", "doc8"]
        vectors = client.zerodb.vectors.get(
            project_id=project_id,
            ids=specific_ids,
            namespace="documents",
            include_metadata=True,
            include_values=False  # Don't include actual vector values
        )
        print(f"   Retrieved {len(vectors)} vectors:")
        for vec in vectors:
            vec_id = vec.get("id", "N/A")
            text = vec.get("metadata", {}).get("text", "N/A")
            print(f"   - {vec_id}: {text}")
        print()
        
        # 5. Update vector metadata
        print("5. Updating vector metadata...")
        client.zerodb.vectors.update_metadata(
            project_id=project_id,
            id="doc1",
            metadata={
                "text": "Python is a versatile programming language",
                "category": "technology",
                "language": "en",
                "updated": True,
                "importance": "high",
                "timestamp": int(time.time())
            },
            namespace="documents"
        )
        print("   ✅ Metadata updated for doc1\n")
        
        # 6. Delete specific vectors
        print("6. Deleting vectors...")
        client.zerodb.vectors.delete(
            project_id=project_id,
            ids=["doc10"],
            namespace="documents"
        )
        print("   ✅ Deleted vector: doc10\n")
        
        # 7. Batch similarity search (multiple queries)
        print("7. Batch similarity search...")
        queries = [
            "programming and software development",
            "scientific research methods",
            "business strategy planning"
        ]
        print("   Queries:")
        for q in queries:
            print(f"   - {q}")
        print("\n   Results:")
        
        for query in queries:
            query_embedding = generate_embeddings([query], dimension=768)[0]
            results = client.zerodb.vectors.search(
                project_id=project_id,
                vector=query_embedding,
                top_k=1,
                namespace="documents"
            )
            if results:
                best_match = results[0].get("metadata", {}).get("text", "N/A")
                score = results[0].get("score", 0)
                print(f"   '{query}' → '{best_match}' (Score: {score:.3f})")
        print()
        
        print("✨ Vector search example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()