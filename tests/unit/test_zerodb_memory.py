"""
Unit tests for the ZeroDB memory module.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from ainative.zerodb.memory import MemoryClient, MemoryPriority


class TestMemoryPriority:
    """Test MemoryPriority enum."""
    
    def test_priority_values(self):
        """Test all priority enum values."""
        assert MemoryPriority.LOW.value == "low"
        assert MemoryPriority.MEDIUM.value == "medium"
        assert MemoryPriority.HIGH.value == "high"
        assert MemoryPriority.CRITICAL.value == "critical"
    
    def test_priority_enum_membership(self):
        """Test enum membership."""
        priorities = [MemoryPriority.LOW, MemoryPriority.MEDIUM, MemoryPriority.HIGH, MemoryPriority.CRITICAL]
        for priority in priorities:
            assert priority in MemoryPriority


class TestMemoryClient:
    """Test MemoryClient class."""
    
    @pytest.fixture
    def memory_client(self, client):
        """Create MemoryClient instance."""
        return MemoryClient(client)
    
    def test_init(self, client):
        """Test initialization."""
        memory = MemoryClient(client)
        assert memory.client == client
        assert memory.base_path == "/zerodb/memory"
    
    def test_create_minimal(self, memory_client, sample_memory):
        """Test creating memory with minimal parameters."""
        memory_client.client.post.return_value = sample_memory
        
        result = memory_client.create("Test memory content")
        
        assert result == sample_memory
        
        call_args = memory_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["content"] == "Test memory content"
        assert data["title"] == "Memory Entry"  # Default title
        assert data["tags"] == []
        assert data["priority"] == "medium"
        assert data["metadata"] == {}
        assert "project_id" not in data
        assert "user_id" not in data
        assert "expires_at" not in data
    
    def test_create_full_params(self, memory_client, sample_memory):
        """Test creating memory with all parameters."""
        memory_client.client.post.return_value = sample_memory
        expires_at = datetime(2024, 12, 31, 23, 59, 59)
        
        result = memory_client.create(
            content="Full memory content",
            title="Custom Title",
            tags=["important", "project"],
            priority=MemoryPriority.HIGH,
            metadata={"category": "research"},
            project_id="proj_123",
            user_id="user_456",
            expires_at=expires_at
        )
        
        assert result == sample_memory
        
        call_args = memory_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["content"] == "Full memory content"
        assert data["title"] == "Custom Title"
        assert data["tags"] == ["important", "project"]
        assert data["priority"] == "high"
        assert data["metadata"] == {"category": "research"}
        assert data["project_id"] == "proj_123"
        assert data["user_id"] == "user_456"
        assert data["expires_at"] == expires_at.isoformat()
    
    def test_create_priority_types(self, memory_client, sample_memory):
        """Test creating memory with different priority levels."""
        memory_client.client.post.return_value = sample_memory
        
        priorities = [
            MemoryPriority.LOW,
            MemoryPriority.MEDIUM,
            MemoryPriority.HIGH,
            MemoryPriority.CRITICAL
        ]
        
        for priority in priorities:
            memory_client.create("Test content", priority=priority)
            
            call_args = memory_client.client.post.call_args
            data = call_args[1]["data"]
            assert data["priority"] == priority.value
            
            memory_client.client.post.reset_mock()
    
    def test_list_default_params(self, memory_client):
        """Test listing memories with default parameters."""
        memories_response = {
            "memories": [{"id": "mem_1"}, {"id": "mem_2"}],
            "total": 2,
            "limit": 100,
            "offset": 0
        }
        memory_client.client.get.return_value = memories_response
        
        result = memory_client.list()
        
        assert result == memories_response
        memory_client.client.get.assert_called_once_with(
            "/zerodb/memories",
            params={"limit": 100, "offset": 0}
        )
    
    def test_list_with_filters(self, memory_client):
        """Test listing memories with filters."""
        expected_response = {"memories": [], "total": 0}
        memory_client.client.get.return_value = expected_response
        
        result = memory_client.list(
            limit=50,
            offset=10,
            project_id="proj_123",
            user_id="user_456",
            tags=["important", "research"],
            priority=MemoryPriority.HIGH,
            search="machine learning"
        )
        
        assert result == expected_response
        
        call_args = memory_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["limit"] == 50
        assert params["offset"] == 10
        assert params["project_id"] == "proj_123"
        assert params["user_id"] == "user_456"
        assert params["tags"] == "important,research"
        assert params["priority"] == "high"
        assert params["search"] == "machine learning"
    
    def test_list_partial_filters(self, memory_client):
        """Test listing with some filters."""
        memory_client.client.get.return_value = {"memories": []}
        
        memory_client.list(
            project_id="proj_123",
            tags=["research"]
        )
        
        call_args = memory_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_123"
        assert params["tags"] == "research"
        assert "user_id" not in params
        assert "priority" not in params
        assert "search" not in params
    
    def test_get(self, memory_client, sample_memory):
        """Test getting memory by ID."""
        memory_client.client.get.return_value = sample_memory
        
        result = memory_client.get("mem_123")
        
        assert result == sample_memory
        memory_client.client.get.assert_called_once_with("/zerodb/memory/mem_123")
    
    def test_update_single_field(self, memory_client, sample_memory):
        """Test updating single field."""
        updated_memory = sample_memory.copy()
        updated_memory["content"] = "Updated content"
        memory_client.client.patch.return_value = updated_memory
        
        result = memory_client.update("mem_123", content="Updated content")
        
        assert result == updated_memory
        memory_client.client.patch.assert_called_once_with(
            "/zerodb/memory/mem_123",
            data={"content": "Updated content"}
        )
    
    def test_update_multiple_fields(self, memory_client, sample_memory):
        """Test updating multiple fields."""
        memory_client.client.patch.return_value = sample_memory
        
        result = memory_client.update(
            "mem_123",
            content="New content",
            title="New title",
            tags=["updated", "modified"],
            priority=MemoryPriority.CRITICAL,
            metadata={"updated": True}
        )
        
        call_args = memory_client.client.patch.call_args
        data = call_args[1]["data"]
        
        assert data["content"] == "New content"
        assert data["title"] == "New title"
        assert data["tags"] == ["updated", "modified"]
        assert data["priority"] == "critical"
        assert data["metadata"] == {"updated": True}
    
    def test_update_empty(self, memory_client):
        """Test update with no fields."""
        memory_client.client.patch.return_value = {}
        
        memory_client.update("mem_123")
        
        memory_client.client.patch.assert_called_once_with(
            "/zerodb/memory/mem_123",
            data={}
        )
    
    def test_delete(self, memory_client):
        """Test deleting memory."""
        delete_response = {"deleted": True, "id": "mem_123"}
        memory_client.client.delete.return_value = delete_response
        
        result = memory_client.delete("mem_123")
        
        assert result == delete_response
        memory_client.client.delete.assert_called_once_with("/zerodb/memory/mem_123")
    
    def test_search_basic(self, memory_client):
        """Test basic memory search."""
        search_results = [
            {"id": "mem_1", "content": "Python programming", "score": 0.95},
            {"id": "mem_2", "content": "Machine learning", "score": 0.80}
        ]
        memory_client.client.post.return_value = {"results": search_results}
        
        result = memory_client.search("programming")
        
        assert result == search_results
        
        call_args = memory_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["query"] == "programming"
        assert data["limit"] == 10  # Default
        assert data["semantic"] is True  # Default
        assert "project_id" not in data
        assert "user_id" not in data
    
    def test_search_with_filters(self, memory_client):
        """Test search with filters."""
        memory_client.client.post.return_value = {"results": []}
        
        result = memory_client.search(
            query="artificial intelligence",
            limit=20,
            project_id="proj_123",
            user_id="user_456",
            semantic=False
        )
        
        call_args = memory_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["query"] == "artificial intelligence"
        assert data["limit"] == 20
        assert data["project_id"] == "proj_123"
        assert data["user_id"] == "user_456"
        assert data["semantic"] is False
    
    def test_search_empty_results(self, memory_client):
        """Test search with no results."""
        memory_client.client.post.return_value = {}
        
        result = memory_client.search("nonexistent query")
        
        assert result == []
    
    def test_bulk_create(self, memory_client):
        """Test bulk memory creation."""
        memories = [
            {
                "content": "First memory",
                "title": "Memory 1",
                "tags": ["bulk", "test"]
            },
            {
                "content": "Second memory",
                "title": "Memory 2",
                "priority": "high"
            }
        ]
        
        bulk_response = {
            "created": 2,
            "memories": [
                {"id": "mem_1", "content": "First memory"},
                {"id": "mem_2", "content": "Second memory"}
            ]
        }
        memory_client.client.post.return_value = bulk_response
        
        result = memory_client.bulk_create(memories, project_id="proj_123")
        
        assert result == bulk_response
        
        call_args = memory_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["memories"] == memories
        assert data["project_id"] == "proj_123"
        
        # Verify endpoint
        assert call_args[0][0] == "/zerodb/memory/bulk"
    
    def test_bulk_create_without_project(self, memory_client):
        """Test bulk creation without project ID."""
        memories = [{"content": "Test memory"}]
        memory_client.client.post.return_value = {"created": 1}
        
        memory_client.bulk_create(memories)
        
        call_args = memory_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["memories"] == memories
        assert "project_id" not in data
    
    def test_get_related(self, memory_client):
        """Test getting related memories."""
        related_memories = [
            {"id": "mem_2", "content": "Related memory 1", "similarity": 0.85},
            {"id": "mem_3", "content": "Related memory 2", "similarity": 0.75}
        ]
        memory_client.client.get.return_value = {"memories": related_memories}
        
        result = memory_client.get_related("mem_1", limit=2)
        
        assert result == related_memories
        
        call_args = memory_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["limit"] == 2
        assert call_args[0][0] == "/zerodb/memory/mem_1/related"
    
    def test_get_related_default_limit(self, memory_client):
        """Test getting related memories with default limit."""
        memory_client.client.get.return_value = {"memories": []}
        
        memory_client.get_related("mem_1")
        
        call_args = memory_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["limit"] == 5  # Default
    
    def test_get_related_empty(self, memory_client):
        """Test getting related memories when none exist."""
        memory_client.client.get.return_value = {}
        
        result = memory_client.get_related("mem_1")
        
        assert result == []


class TestMemoryClientIntegration:
    """Test MemoryClient integration scenarios."""
    
    @pytest.fixture
    def memory_client(self, client):
        return MemoryClient(client)
    
    def test_full_memory_lifecycle(self, memory_client, sample_memory):
        """Test complete memory operations workflow."""
        # Setup mock responses
        create_response = sample_memory.copy()
        updated_response = create_response.copy()
        updated_response["content"] = "Updated content"
        search_response = {"results": [create_response]}
        related_response = {"memories": [{"id": "mem_related"}]}
        delete_response = {"deleted": True}
        
        memory_client.client.post.side_effect = [create_response, search_response]
        memory_client.client.get.side_effect = [create_response, related_response]
        memory_client.client.patch.return_value = updated_response
        memory_client.client.delete.return_value = delete_response
        
        # Create memory
        created = memory_client.create(
            content="Test memory content",
            title="Test Memory",
            tags=["test", "example"],
            priority=MemoryPriority.HIGH
        )
        assert created == create_response
        
        # Get memory
        retrieved = memory_client.get("mem_test123")
        assert retrieved == create_response
        
        # Update memory
        updated = memory_client.update(
            "mem_test123",
            content="Updated content",
            tags=["test", "updated"]
        )
        assert updated == updated_response
        
        # Search memories
        search_results = memory_client.search("test content")
        assert search_results == search_response["results"]
        
        # Get related memories
        related = memory_client.get_related("mem_test123")
        assert related == related_response["memories"]
        
        # Delete memory
        deleted = memory_client.delete("mem_test123")
        assert deleted == delete_response
    
    def test_bulk_operations(self, memory_client):
        """Test bulk memory operations."""
        # Prepare bulk data
        bulk_memories = [
            {
                "content": f"Bulk memory {i}",
                "title": f"Memory {i}",
                "tags": ["bulk", f"batch_{i//10}"],
                "priority": "medium"
            }
            for i in range(50)
        ]
        
        bulk_response = {
            "created": 50,
            "memories": [{"id": f"mem_{i}"} for i in range(50)]
        }
        memory_client.client.post.return_value = bulk_response
        
        result = memory_client.bulk_create(bulk_memories, project_id="proj_bulk")
        
        assert result == bulk_response
        
        call_args = memory_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert len(data["memories"]) == 50
        assert data["project_id"] == "proj_bulk"
    
    def test_search_variations(self, memory_client):
        """Test different search scenarios."""
        memory_client.client.post.return_value = {"results": []}
        
        search_scenarios = [
            # Semantic search
            {"query": "machine learning", "semantic": True},
            # Text search
            {"query": "python programming", "semantic": False},
            # With filters
            {
                "query": "data science",
                "project_id": "proj_123",
                "user_id": "user_456",
                "limit": 25
            },
            # Short query
            {"query": "AI", "limit": 5},
            # Long query
            {
                "query": "artificial intelligence and machine learning algorithms for natural language processing",
                "limit": 15
            }
        ]
        
        for scenario in search_scenarios:
            memory_client.search(**scenario)
            
            call_args = memory_client.client.post.call_args
            data = call_args[1]["data"]
            
            for key, value in scenario.items():
                assert data[key] == value
            
            memory_client.client.post.reset_mock()
    
    def test_priority_based_operations(self, memory_client, sample_memory):
        """Test operations with different priority levels."""
        memory_client.client.post.return_value = sample_memory
        memory_client.client.get.return_value = {"memories": []}
        
        priorities = [
            MemoryPriority.CRITICAL,
            MemoryPriority.HIGH,
            MemoryPriority.MEDIUM,
            MemoryPriority.LOW
        ]
        
        for priority in priorities:
            # Create with priority
            memory_client.create(
                f"Memory with {priority.value} priority",
                priority=priority
            )
            
            create_call = memory_client.client.post.call_args
            assert create_call[1]["data"]["priority"] == priority.value
            
            # List by priority
            memory_client.list(priority=priority, limit=10)
            
            list_call = memory_client.client.get.call_args
            assert list_call[1]["params"]["priority"] == priority.value
            
            # Reset mocks
            memory_client.client.post.reset_mock()
            memory_client.client.get.reset_mock()
    
    def test_datetime_handling(self, memory_client, sample_memory):
        """Test datetime handling for expiration."""
        memory_client.client.post.return_value = sample_memory
        
        # Test different datetime scenarios
        test_datetimes = [
            datetime(2024, 12, 31, 23, 59, 59),  # End of year
            datetime(2024, 6, 15, 12, 0, 0),     # Mid year
            datetime(2025, 1, 1, 0, 0, 0),       # New year
        ]
        
        for dt in test_datetimes:
            memory_client.create(
                "Memory with expiration",
                expires_at=dt
            )
            
            call_args = memory_client.client.post.call_args
            data = call_args[1]["data"]
            
            assert data["expires_at"] == dt.isoformat()
            memory_client.client.post.reset_mock()
    
    def test_tag_handling(self, memory_client, sample_memory):
        """Test tag handling in various operations."""
        memory_client.client.post.return_value = sample_memory
        memory_client.client.get.return_value = {"memories": []}
        
        tag_scenarios = [
            [],  # No tags
            ["single"],  # Single tag
            ["multiple", "tags", "here"],  # Multiple tags
            ["tag-with-dash", "tag_with_underscore"],  # Special characters
            ["🔥", "📚", "🚀"],  # Emoji tags
        ]
        
        for tags in tag_scenarios:
            # Create with tags
            memory_client.create("Test content", tags=tags)
            
            create_call = memory_client.client.post.call_args
            assert create_call[1]["data"]["tags"] == tags
            
            # List with tag filter
            if tags:  # Only test filtering if there are tags
                memory_client.list(tags=tags)
                
                list_call = memory_client.client.get.call_args
                expected_tag_string = ",".join(tags)
                assert list_call[1]["params"]["tags"] == expected_tag_string
            
            # Reset mocks
            memory_client.client.post.reset_mock()
            memory_client.client.get.reset_mock()
    
    def test_error_scenarios(self, memory_client):
        """Test error handling scenarios."""
        from ainative.exceptions import APIError, ValidationError
        
        # Test API errors during creation
        memory_client.client.post.side_effect = APIError("Content too long", status_code=400)
        
        with pytest.raises(APIError):
            memory_client.create("x" * 10000)  # Very long content
        
        # Test not found errors
        memory_client.client.get.side_effect = APIError("Memory not found", status_code=404)
        
        with pytest.raises(APIError):
            memory_client.get("nonexistent_memory")
        
        # Reset mocks
        memory_client.client.post.side_effect = None
        memory_client.client.get.side_effect = None
    
    def test_pagination_scenarios(self, memory_client):
        """Test pagination in list operations."""
        memory_client.client.get.return_value = {"memories": [], "total": 0}
        
        pagination_scenarios = [
            {"limit": 10, "offset": 0},     # First page
            {"limit": 10, "offset": 10},    # Second page
            {"limit": 50, "offset": 100},   # Large offset
            {"limit": 1, "offset": 999},    # Edge case
        ]
        
        for scenario in pagination_scenarios:
            memory_client.list(**scenario)
            
            call_args = memory_client.client.get.call_args
            params = call_args[1]["params"]
            
            assert params["limit"] == scenario["limit"]
            assert params["offset"] == scenario["offset"]
            
            memory_client.client.get.reset_mock()