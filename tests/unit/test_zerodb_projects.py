"""
Unit tests for the ZeroDB projects module.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from ainative.zerodb.projects import ProjectsClient, ProjectStatus


class TestProjectStatus:
    """Test ProjectStatus enum."""
    
    def test_status_values(self):
        """Test all status enum values."""
        assert ProjectStatus.ACTIVE.value == "active"
        assert ProjectStatus.SUSPENDED.value == "suspended"
        assert ProjectStatus.ARCHIVED.value == "archived"
        assert ProjectStatus.DELETED.value == "deleted"
    
    def test_status_enum_membership(self):
        """Test enum membership."""
        assert ProjectStatus.ACTIVE in ProjectStatus
        assert ProjectStatus.SUSPENDED in ProjectStatus
        assert ProjectStatus.ARCHIVED in ProjectStatus
        assert ProjectStatus.DELETED in ProjectStatus


class TestProjectsClient:
    """Test ProjectsClient class."""
    
    @pytest.fixture
    def projects_client(self, client):
        """Create ProjectsClient instance."""
        return ProjectsClient(client)
    
    def test_init(self, client):
        """Test initialization."""
        projects = ProjectsClient(client)
        assert projects.client == client
        assert projects.base_path == "/zerodb/projects"
    
    def test_list_default_params(self, projects_client, mock_response):
        """Test list with default parameters."""
        response_data = {
            "projects": [{"id": "proj_1"}, {"id": "proj_2"}],
            "total": 2,
            "limit": 100,
            "offset": 0
        }
        projects_client.client.get.return_value = response_data
        
        result = projects_client.list()
        
        assert result == response_data
        projects_client.client.get.assert_called_once_with(
            "/zerodb/projects",
            params={"limit": 100, "offset": 0}
        )
    
    def test_list_with_params(self, projects_client):
        """Test list with custom parameters."""
        expected_response = {"projects": [], "total": 0}
        projects_client.client.get.return_value = expected_response
        
        result = projects_client.list(
            limit=50,
            offset=10,
            status=ProjectStatus.ACTIVE,
            organization_id="org_123"
        )
        
        assert result == expected_response
        projects_client.client.get.assert_called_once_with(
            "/zerodb/projects",
            params={
                "limit": 50,
                "offset": 10,
                "status": "active",
                "organization_id": "org_123"
            }
        )
    
    def test_list_with_status_only(self, projects_client):
        """Test list filtering by status only."""
        projects_client.client.get.return_value = {"projects": []}
        
        projects_client.list(status=ProjectStatus.SUSPENDED)
        
        call_args = projects_client.client.get.call_args
        params = call_args[1]["params"]
        assert params["status"] == "suspended"
        assert "organization_id" not in params
    
    def test_create_minimal(self, projects_client, sample_project):
        """Test creating project with minimal parameters."""
        projects_client.client.post.return_value = sample_project
        
        result = projects_client.create("Test Project")
        
        assert result == sample_project
        projects_client.client.post.assert_called_once_with(
            "/zerodb/projects",
            data={
                "name": "Test Project",
                "description": "",
                "metadata": {},
                "config": {}
            }
        )
    
    def test_create_full(self, projects_client, sample_project):
        """Test creating project with all parameters."""
        metadata = {"team": "engineering"}
        config = {"max_vectors": 10000}
        projects_client.client.post.return_value = sample_project
        
        result = projects_client.create(
            name="Full Project",
            description="Complete project",
            metadata=metadata,
            config=config
        )
        
        assert result == sample_project
        projects_client.client.post.assert_called_once_with(
            "/zerodb/projects",
            data={
                "name": "Full Project",
                "description": "Complete project",
                "metadata": metadata,
                "config": config
            }
        )
    
    def test_get(self, projects_client, sample_project):
        """Test getting project by ID."""
        projects_client.client.get.return_value = sample_project
        
        result = projects_client.get("proj_123")
        
        assert result == sample_project
        projects_client.client.get.assert_called_once_with("/zerodb/projects/proj_123")
    
    def test_update_single_field(self, projects_client, sample_project):
        """Test updating single field."""
        updated_project = sample_project.copy()
        updated_project["name"] = "Updated Name"
        projects_client.client.patch.return_value = updated_project
        
        result = projects_client.update("proj_123", name="Updated Name")
        
        assert result == updated_project
        projects_client.client.patch.assert_called_once_with(
            "/zerodb/projects/proj_123",
            data={"name": "Updated Name"}
        )
    
    def test_update_multiple_fields(self, projects_client, sample_project):
        """Test updating multiple fields."""
        updated_project = sample_project.copy()
        projects_client.client.patch.return_value = updated_project
        
        result = projects_client.update(
            "proj_123",
            name="New Name",
            description="New Description",
            metadata={"updated": True}
        )
        
        assert result == updated_project
        projects_client.client.patch.assert_called_once_with(
            "/zerodb/projects/proj_123",
            data={
                "name": "New Name",
                "description": "New Description",
                "metadata": {"updated": True}
            }
        )
    
    def test_update_empty(self, projects_client):
        """Test update with no fields (should send empty data)."""
        projects_client.client.patch.return_value = {}
        
        projects_client.update("proj_123")
        
        projects_client.client.patch.assert_called_once_with(
            "/zerodb/projects/proj_123",
            data={}
        )
    
    def test_update_status_basic(self, projects_client, sample_project):
        """Test updating project status."""
        projects_client.client.put.return_value = sample_project
        
        result = projects_client.update_status("proj_123", ProjectStatus.SUSPENDED)
        
        assert result == sample_project
        projects_client.client.put.assert_called_once_with(
            "/zerodb/projects/proj_123/status",
            data={"status": "suspended", "reason": None}
        )
    
    def test_update_status_with_reason(self, projects_client, sample_project):
        """Test updating project status with reason."""
        projects_client.client.put.return_value = sample_project
        
        result = projects_client.update_status(
            "proj_123",
            ProjectStatus.ARCHIVED,
            reason="Project completed"
        )
        
        assert result == sample_project
        projects_client.client.put.assert_called_once_with(
            "/zerodb/projects/proj_123/status",
            data={"status": "archived", "reason": "Project completed"}
        )
    
    def test_suspend_shortcut(self, projects_client, sample_project):
        """Test suspend convenience method."""
        projects_client.client.put.return_value = sample_project
        
        result = projects_client.suspend("proj_123", reason="Maintenance")
        
        assert result == sample_project
        projects_client.client.put.assert_called_once_with(
            "/zerodb/projects/proj_123/status",
            data={"status": "suspended", "reason": "Maintenance"}
        )
    
    def test_suspend_without_reason(self, projects_client, sample_project):
        """Test suspend without reason."""
        projects_client.client.put.return_value = sample_project
        
        result = projects_client.suspend("proj_123")
        
        projects_client.client.put.assert_called_once_with(
            "/zerodb/projects/proj_123/status",
            data={"status": "suspended", "reason": None}
        )
    
    def test_activate_shortcut(self, projects_client, sample_project):
        """Test activate convenience method."""
        projects_client.client.put.return_value = sample_project
        
        result = projects_client.activate("proj_123")
        
        assert result == sample_project
        projects_client.client.put.assert_called_once_with(
            "/zerodb/projects/proj_123/status",
            data={"status": "active", "reason": None}
        )
    
    def test_delete(self, projects_client):
        """Test deleting project."""
        delete_response = {"deleted": True, "id": "proj_123"}
        projects_client.client.delete.return_value = delete_response
        
        result = projects_client.delete("proj_123")
        
        assert result == delete_response
        projects_client.client.delete.assert_called_once_with("/zerodb/projects/proj_123")
    
    def test_get_statistics(self, projects_client, sample_analytics):
        """Test getting project statistics."""
        stats = {
            "vector_count": 1500,
            "memory_count": 25,
            "storage_bytes": 2048000,
            "last_activity": "2024-01-01T12:00:00Z"
        }
        projects_client.client.get.return_value = stats
        
        result = projects_client.get_statistics("proj_123")
        
        assert result == stats
        projects_client.client.get.assert_called_once_with("/zerodb/projects/proj_123/statistics")
    
    def test_get_collections(self, projects_client):
        """Test getting project collections."""
        collections_response = {
            "collections": [
                {"name": "documents", "vector_count": 1000},
                {"name": "embeddings", "vector_count": 500}
            ]
        }
        projects_client.client.get.return_value = collections_response
        
        result = projects_client.get_collections("proj_123")
        
        expected_collections = collections_response["collections"]
        assert result == expected_collections
        projects_client.client.get.assert_called_once_with("/zerodb/projects/proj_123/collections")
    
    def test_get_collections_empty(self, projects_client):
        """Test getting collections when none exist."""
        projects_client.client.get.return_value = {}
        
        result = projects_client.get_collections("proj_123")
        
        assert result == []


class TestProjectsClientIntegration:
    """Test ProjectsClient integration scenarios."""
    
    @pytest.fixture
    def projects_client(self, client):
        return ProjectsClient(client)
    
    def test_full_project_lifecycle(self, projects_client, sample_project):
        """Test complete project lifecycle."""
        # Mock responses for each step
        created_project = sample_project.copy()
        updated_project = created_project.copy()
        updated_project["name"] = "Updated Project"
        suspended_project = updated_project.copy()
        suspended_project["status"] = "suspended"
        
        projects_client.client.post.return_value = created_project
        projects_client.client.patch.return_value = updated_project
        projects_client.client.put.return_value = suspended_project
        projects_client.client.delete.return_value = {"deleted": True}
        
        # Create
        created = projects_client.create(
            "Test Project",
            description="Test description"
        )
        assert created == created_project
        
        # Update
        updated = projects_client.update(
            "proj_test123",
            name="Updated Project"
        )
        assert updated == updated_project
        
        # Suspend
        suspended = projects_client.suspend(
            "proj_test123",
            reason="Testing"
        )
        assert suspended == suspended_project
        
        # Delete
        deleted = projects_client.delete("proj_test123")
        assert deleted["deleted"] is True
    
    def test_status_transition_workflow(self, projects_client, sample_project):
        """Test project status transitions."""
        projects_client.client.put.return_value = sample_project
        
        statuses = [
            (ProjectStatus.ACTIVE, "active"),
            (ProjectStatus.SUSPENDED, "suspended"),
            (ProjectStatus.ARCHIVED, "archived")
        ]
        
        for status_enum, status_value in statuses:
            projects_client.update_status("proj_123", status_enum)
            
            call_args = projects_client.client.put.call_args
            data = call_args[1]["data"]
            assert data["status"] == status_value
            
            projects_client.client.put.reset_mock()
    
    def test_error_handling(self, projects_client):
        """Test error handling in projects operations."""
        from ainative.exceptions import APIError, ResourceNotFoundError
        
        # Test different error scenarios
        projects_client.client.get.side_effect = APIError("Not found", status_code=404)
        
        with pytest.raises(APIError):
            projects_client.get("nonexistent_project")
        
        # Reset mock
        projects_client.client.get.side_effect = None
    
    def test_parameter_validation_types(self, projects_client):
        """Test that parameters are handled correctly."""
        projects_client.client.post.return_value = {}
        
        # Test with various parameter types
        projects_client.create(
            name="Test",
            description=None,  # Should become empty string
            metadata=None,     # Should become empty dict
            config=None        # Should become empty dict
        )
        
        call_args = projects_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["description"] == ""
        assert data["metadata"] == {}
        assert data["config"] == {}
    
    def test_list_pagination_handling(self, projects_client):
        """Test list method with various pagination scenarios."""
        projects_client.client.get.return_value = {"projects": []}
        
        # Test edge cases
        edge_cases = [
            {"limit": 0, "offset": 0},
            {"limit": 1000, "offset": 0},
            {"limit": 10, "offset": 999}
        ]
        
        for params in edge_cases:
            projects_client.list(**params)
            call_args = projects_client.client.get.call_args
            assert call_args[1]["params"]["limit"] == params["limit"]
            assert call_args[1]["params"]["offset"] == params["offset"]
            projects_client.client.get.reset_mock()