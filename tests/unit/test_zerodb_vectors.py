"""
Unit tests for the ZeroDB vectors module.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from ainative.zerodb.vectors import VectorsClient


class TestVectorsClient:
    """Test VectorsClient class."""
    
    @pytest.fixture
    def vectors_client(self, client):
        """Create VectorsClient instance."""
        return VectorsClient(client)
    
    def test_init(self, client):
        """Test initialization."""
        vectors = VectorsClient(client)
        assert vectors.client == client
        assert vectors.base_path == "/zerodb/vectors"
    
    def test_upsert_basic_lists(self, vectors_client):
        """Test upserting vectors with basic list format."""
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        response = {"upserted": 2, "ids": ["vec_1", "vec_2"]}
        vectors_client.client.put.return_value = response
        
        result = vectors_client.upsert(
            project_id="proj_123",
            vectors=vectors,
            namespace="test"
        )
        
        assert result == response
        
        call_args = vectors_client.client.put.call_args
        data = call_args[1]["data"]
        
        assert data["project_id"] == "proj_123"
        assert data["namespace"] == "test"
        assert len(data["items"]) == 2
        assert data["items"][0]["vector"] == [0.1, 0.2, 0.3]
        assert data["items"][1]["vector"] == [0.4, 0.5, 0.6]
    
    def test_upsert_with_numpy_arrays(self, vectors_client):
        """Test upserting vectors with numpy arrays."""
        vectors = [
            np.array([0.1, 0.2, 0.3]),
            np.array([0.4, 0.5, 0.6])
        ]
        vectors_client.client.put.return_value = {"upserted": 2}
        
        vectors_client.upsert("proj_123", vectors)
        
        call_args = vectors_client.client.put.call_args
        data = call_args[1]["data"]
        
        # Should convert numpy arrays to lists
        assert data["items"][0]["vector"] == [0.1, 0.2, 0.3]
        assert data["items"][1]["vector"] == [0.4, 0.5, 0.6]
        assert isinstance(data["items"][0]["vector"], list)
    
    def test_upsert_with_metadata(self, vectors_client):
        """Test upserting vectors with metadata."""
        vectors = [[0.1, 0.2], [0.3, 0.4]]
        metadata = [
            {"text": "first vector", "category": "A"},
            {"text": "second vector", "category": "B"}
        ]
        vectors_client.client.put.return_value = {"upserted": 2}
        
        vectors_client.upsert("proj_123", vectors, metadata=metadata)
        
        call_args = vectors_client.client.put.call_args
        data = call_args[1]["data"]
        
        assert data["items"][0]["metadata"] == metadata[0]
        assert data["items"][1]["metadata"] == metadata[1]
    
    def test_upsert_with_ids(self, vectors_client):
        """Test upserting vectors with custom IDs."""
        vectors = [[0.1, 0.2]]
        ids = ["custom_id_1"]
        vectors_client.client.put.return_value = {"upserted": 1}
        
        vectors_client.upsert("proj_123", vectors, ids=ids)
        
        call_args = vectors_client.client.put.call_args
        data = call_args[1]["data"]
        
        assert data["items"][0]["id"] == "custom_id_1"
    
    def test_upsert_full_params(self, vectors_client):
        """Test upserting with all parameters."""
        vectors = [np.array([0.1, 0.2, 0.3])]
        metadata = [{"text": "test"}]
        ids = ["vec_custom"]
        vectors_client.client.put.return_value = {"upserted": 1}
        
        result = vectors_client.upsert(
            project_id="proj_456",
            vectors=vectors,
            metadata=metadata,
            ids=ids,
            namespace="custom_ns"
        )
        
        call_args = vectors_client.client.put.call_args
        data = call_args[1]["data"]
        
        assert data["project_id"] == "proj_456"
        assert data["namespace"] == "custom_ns"
        assert data["items"][0]["vector"] == [0.1, 0.2, 0.3]
        assert data["items"][0]["metadata"] == {"text": "test"}
        assert data["items"][0]["id"] == "vec_custom"
    
    def test_upsert_partial_metadata(self, vectors_client):
        """Test upserting where metadata list is shorter than vectors."""
        vectors = [[0.1], [0.2], [0.3]]
        metadata = [{"text": "first"}]  # Only metadata for first vector
        vectors_client.client.put.return_value = {"upserted": 3}
        
        vectors_client.upsert("proj_123", vectors, metadata=metadata)
        
        call_args = vectors_client.client.put.call_args
        data = call_args[1]["data"]
        
        assert "metadata" in data["items"][0]
        assert data["items"][0]["metadata"] == {"text": "first"}
        assert "metadata" not in data["items"][1]
        assert "metadata" not in data["items"][2]
    
    def test_search_basic(self, vectors_client):
        """Test basic vector search."""
        query_vector = [0.1, 0.2, 0.3]
        search_results = [
            {"id": "vec_1", "score": 0.95, "metadata": {"text": "match"}},
            {"id": "vec_2", "score": 0.80, "metadata": {"text": "close"}}
        ]
        vectors_client.client.post.return_value = {"results": search_results}
        
        result = vectors_client.search(
            project_id="proj_123",
            vector=query_vector,
            top_k=2
        )
        
        assert result == search_results
        
        call_args = vectors_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["project_id"] == "proj_123"
        assert data["vector"] == query_vector
        assert data["top_k"] == 2
        assert data["namespace"] == "default"
        assert data["include_metadata"] is True
        assert data["include_values"] is False
    
    def test_search_with_numpy_query(self, vectors_client):
        """Test search with numpy array query."""
        query_vector = np.array([0.1, 0.2, 0.3])
        vectors_client.client.post.return_value = {"results": []}
        
        vectors_client.search("proj_123", query_vector)
        
        call_args = vectors_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["vector"] == [0.1, 0.2, 0.3]
        assert isinstance(data["vector"], list)
    
    def test_search_with_filter(self, vectors_client):
        """Test search with metadata filter."""
        query_vector = [0.1, 0.2]
        filter_criteria = {"category": "documents", "language": "en"}
        vectors_client.client.post.return_value = {"results": []}
        
        vectors_client.search(
            project_id="proj_123",
            vector=query_vector,
            top_k=5,
            namespace="docs",
            filter=filter_criteria,
            include_metadata=True,
            include_values=True
        )
        
        call_args = vectors_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["top_k"] == 5
        assert data["namespace"] == "docs"
        assert data["filter"] == filter_criteria
        assert data["include_metadata"] is True
        assert data["include_values"] is True
    
    def test_search_no_results(self, vectors_client):
        """Test search when no results are returned."""
        vectors_client.client.post.return_value = {}
        
        result = vectors_client.search("proj_123", [0.1, 0.2])
        
        assert result == []
    
    def test_get_vectors_by_ids(self, vectors_client):
        """Test getting vectors by IDs."""
        ids = ["vec_1", "vec_2", "vec_3"]
        vector_data = [
            {"id": "vec_1", "vector": [0.1, 0.2], "metadata": {"text": "first"}},
            {"id": "vec_2", "vector": [0.3, 0.4], "metadata": {"text": "second"}}
        ]
        vectors_client.client.get.return_value = {"vectors": vector_data}
        
        result = vectors_client.get(
            project_id="proj_123",
            ids=ids,
            namespace="test"
        )
        
        assert result == vector_data
        
        call_args = vectors_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_123"
        assert params["ids"] == "vec_1,vec_2,vec_3"
        assert params["namespace"] == "test"
        assert params["include_metadata"] is True
        assert params["include_values"] is True
    
    def test_get_vectors_options(self, vectors_client):
        """Test getting vectors with different include options."""
        vectors_client.client.get.return_value = {"vectors": []}
        
        vectors_client.get(
            project_id="proj_123",
            ids=["vec_1"],
            include_metadata=False,
            include_values=False
        )
        
        call_args = vectors_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["include_metadata"] is False
        assert params["include_values"] is False
    
    def test_get_vectors_empty_result(self, vectors_client):
        """Test get when no vectors are returned."""
        vectors_client.client.get.return_value = {}
        
        result = vectors_client.get("proj_123", ["nonexistent"])
        
        assert result == []
    
    def test_delete_by_ids(self, vectors_client):
        """Test deleting vectors by IDs."""
        delete_response = {"deleted": 2, "ids": ["vec_1", "vec_2"]}
        vectors_client.client.delete.return_value = delete_response
        
        result = vectors_client.delete(
            project_id="proj_123",
            ids=["vec_1", "vec_2"],
            namespace="test"
        )
        
        assert result == delete_response
        
        call_args = vectors_client.client.delete.call_args
        data = call_args[1]["data"]
        
        assert data["project_id"] == "proj_123"
        assert data["ids"] == ["vec_1", "vec_2"]
        assert data["namespace"] == "test"
        assert "delete_all" not in data
        assert "filter" not in data
    
    def test_delete_all(self, vectors_client):
        """Test deleting all vectors in namespace."""
        vectors_client.client.delete.return_value = {"deleted": "all"}
        
        result = vectors_client.delete(
            project_id="proj_123",
            namespace="test",
            delete_all=True
        )
        
        call_args = vectors_client.client.delete.call_args
        data = call_args[1]["data"]
        
        assert data["delete_all"] is True
        assert data["project_id"] == "proj_123"
        assert data["namespace"] == "test"
    
    def test_delete_by_filter(self, vectors_client):
        """Test deleting vectors by filter."""
        filter_criteria = {"category": "obsolete"}
        vectors_client.client.delete.return_value = {"deleted": 5}
        
        result = vectors_client.delete(
            project_id="proj_123",
            filter=filter_criteria
        )
        
        call_args = vectors_client.client.delete.call_args
        data = call_args[1]["data"]
        
        assert data["filter"] == filter_criteria
        assert data["project_id"] == "proj_123"
        assert data["namespace"] == "default"
    
    def test_delete_invalid_params(self, vectors_client):
        """Test delete with invalid parameter combination."""
        with pytest.raises(ValueError, match="Must provide ids, filter, or delete_all=True"):
            vectors_client.delete(project_id="proj_123")
    
    def test_update_metadata(self, vectors_client):
        """Test updating vector metadata."""
        new_metadata = {"updated": True, "category": "processed"}
        update_response = {"updated": True, "id": "vec_123"}
        vectors_client.client.patch.return_value = update_response
        
        result = vectors_client.update_metadata(
            project_id="proj_123",
            id="vec_123",
            metadata=new_metadata,
            namespace="docs"
        )
        
        assert result == update_response
        
        call_args = vectors_client.client.patch.call_args
        data = call_args[1]["data"]
        
        assert data["project_id"] == "proj_123"
        assert data["id"] == "vec_123"
        assert data["metadata"] == new_metadata
        assert data["namespace"] == "docs"
        
        # Verify URL
        assert call_args[0][0] == "/zerodb/vectors/vec_123/metadata"
    
    def test_describe_index_stats_all_namespaces(self, vectors_client):
        """Test getting index statistics for all namespaces."""
        stats = {
            "total_vectors": 10000,
            "dimensions": 768,
            "namespaces": ["default", "documents", "embeddings"]
        }
        vectors_client.client.get.return_value = stats
        
        result = vectors_client.describe_index_stats(project_id="proj_123")
        
        assert result == stats
        
        call_args = vectors_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_123"
        assert "namespace" not in params
    
    def test_describe_index_stats_specific_namespace(self, vectors_client):
        """Test getting index statistics for specific namespace."""
        vectors_client.client.get.return_value = {"vectors": 5000}
        
        vectors_client.describe_index_stats(
            project_id="proj_123",
            namespace="documents"
        )
        
        call_args = vectors_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["namespace"] == "documents"


class TestVectorsClientIntegration:
    """Test VectorsClient integration scenarios."""
    
    @pytest.fixture
    def vectors_client(self, client):
        return VectorsClient(client)
    
    def test_full_vector_lifecycle(self, vectors_client):
        """Test complete vector operations workflow."""
        # Setup mock responses
        upsert_response = {"upserted": 2, "ids": ["vec_1", "vec_2"]}
        search_response = {"results": [{"id": "vec_1", "score": 0.95}]}
        get_response = {"vectors": [{"id": "vec_1", "vector": [0.1, 0.2]}]}
        update_response = {"updated": True}
        delete_response = {"deleted": 1}
        
        vectors_client.client.put.return_value = upsert_response
        vectors_client.client.post.return_value = search_response
        vectors_client.client.get.return_value = get_response
        vectors_client.client.patch.return_value = update_response
        vectors_client.client.delete.return_value = delete_response
        
        # Upsert vectors
        vectors = [[0.1, 0.2], [0.3, 0.4]]
        metadata = [{"text": "first"}, {"text": "second"}]
        
        upsert_result = vectors_client.upsert("proj_123", vectors, metadata=metadata)
        assert upsert_result == upsert_response
        
        # Search vectors
        search_result = vectors_client.search("proj_123", [0.15, 0.25])
        assert search_result == search_response["results"]
        
        # Get vectors
        get_result = vectors_client.get("proj_123", ["vec_1"])
        assert get_result == get_response["vectors"]
        
        # Update metadata
        update_result = vectors_client.update_metadata(
            "proj_123", "vec_1", {"updated": True}
        )
        assert update_result == update_response
        
        # Delete vectors
        delete_result = vectors_client.delete("proj_123", ids=["vec_1"])
        assert delete_result == delete_response
    
    def test_batch_operations(self, vectors_client):
        """Test batch vector operations."""
        # Large batch upsert
        vectors = [np.random.rand(768) for _ in range(100)]
        metadata = [{"id": i, "batch": "test"} for i in range(100)]
        ids = [f"vec_{i:03d}" for i in range(100)]
        
        vectors_client.client.put.return_value = {"upserted": 100}
        
        result = vectors_client.upsert(
            project_id="proj_123",
            vectors=vectors,
            metadata=metadata,
            ids=ids,
            namespace="batch_test"
        )
        
        call_args = vectors_client.client.put.call_args
        data = call_args[1]["data"]
        
        assert len(data["items"]) == 100
        assert all(isinstance(item["vector"], list) for item in data["items"])
        assert all("metadata" in item for item in data["items"])
        assert all("id" in item for item in data["items"])
    
    def test_mixed_vector_types(self, vectors_client):
        """Test handling mixed vector types."""
        vectors = [
            [0.1, 0.2, 0.3],  # List
            np.array([0.4, 0.5, 0.6]),  # NumPy array
            [0.7, 0.8, 0.9]   # List again
        ]
        
        vectors_client.client.put.return_value = {"upserted": 3}
        
        vectors_client.upsert("proj_123", vectors)
        
        call_args = vectors_client.client.put.call_args
        data = call_args[1]["data"]
        
        # All should be converted to lists
        for item in data["items"]:
            assert isinstance(item["vector"], list)
            assert len(item["vector"]) == 3
    
    def test_search_with_complex_filters(self, vectors_client):
        """Test search with complex metadata filters."""
        complex_filter = {
            "category": {"$in": ["documents", "articles"]},
            "score": {"$gte": 0.8},
            "published": True,
            "tags": {"$contains": "ai"}
        }
        
        vectors_client.client.post.return_value = {"results": []}
        
        vectors_client.search(
            project_id="proj_123",
            vector=[0.1, 0.2],
            filter=complex_filter,
            top_k=20,
            namespace="content"
        )
        
        call_args = vectors_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["filter"] == complex_filter
        assert data["top_k"] == 20
        assert data["namespace"] == "content"
    
    def test_error_handling_scenarios(self, vectors_client):
        """Test error handling in various scenarios."""
        from ainative.exceptions import APIError, ValidationError
        
        # Test validation errors
        with pytest.raises(ValueError):
            vectors_client.delete("proj_123")  # No deletion criteria
        
        # Test API errors
        vectors_client.client.put.side_effect = APIError("Invalid vector dimension", status_code=400)
        
        with pytest.raises(APIError):
            vectors_client.upsert("proj_123", [[0.1, 0.2]])
        
        # Reset
        vectors_client.client.put.side_effect = None
    
    def test_namespace_handling(self, vectors_client):
        """Test operations across different namespaces."""
        namespaces = ["default", "documents", "embeddings", "cache"]
        
        vectors_client.client.put.return_value = {"upserted": 1}
        vectors_client.client.post.return_value = {"results": []}
        vectors_client.client.get.return_value = {"vectors": []}
        vectors_client.client.delete.return_value = {"deleted": 1}
        
        for namespace in namespaces:
            # Test upsert
            vectors_client.upsert("proj_123", [[0.1]], namespace=namespace)
            upsert_call = vectors_client.client.put.call_args
            assert upsert_call[1]["data"]["namespace"] == namespace
            
            # Test search
            vectors_client.search("proj_123", [0.1], namespace=namespace)
            search_call = vectors_client.client.post.call_args
            assert search_call[1]["data"]["namespace"] == namespace
            
            # Test get
            vectors_client.get("proj_123", ["vec_1"], namespace=namespace)
            get_call = vectors_client.client.get.call_args
            assert get_call[1]["params"]["namespace"] == namespace
            
            # Test delete
            vectors_client.delete("proj_123", ids=["vec_1"], namespace=namespace)
            delete_call = vectors_client.client.delete.call_args
            assert delete_call[1]["data"]["namespace"] == namespace
    
    def test_large_vector_dimensions(self, vectors_client):
        """Test handling of high-dimensional vectors."""
        # Test with different common embedding dimensions
        dimensions = [128, 256, 512, 768, 1024, 1536, 2048]
        
        for dim in dimensions:
            vector = np.random.rand(dim).tolist()
            vectors_client.client.put.return_value = {"upserted": 1}
            
            vectors_client.upsert("proj_123", [vector])
            
            call_args = vectors_client.client.put.call_args
            data = call_args[1]["data"]
            
            assert len(data["items"][0]["vector"]) == dim
            assert isinstance(data["items"][0]["vector"], list)