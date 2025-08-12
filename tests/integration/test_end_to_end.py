"""
Integration tests for the AINative SDK.

These tests verify the complete SDK workflow from initialization to cleanup.
They can be run against a test server or with mocked responses.
"""

import pytest
import os
import time
import numpy as np
from datetime import datetime, timedelta

from ainative import AINativeClient
from ainative.auth import AuthConfig
from ainative.zerodb.memory import MemoryPriority
from ainative.agent_swarm import AgentType
from ainative.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    ValidationError
)


@pytest.fixture(scope="module")
def integration_client():
    """
    Create client for integration tests.
    
    Uses test API key from environment or mock if not available.
    """
    api_key = os.getenv("AINATIVE_TEST_API_KEY")
    base_url = os.getenv("AINATIVE_TEST_BASE_URL", "https://api.test.ainative.studio")
    
    if not api_key:
        pytest.skip("No test API key provided - set AINATIVE_TEST_API_KEY environment variable")
    
    auth_config = AuthConfig(
        api_key=api_key,
        environment="development"
    )
    
    return AINativeClient(
        auth_config=auth_config,
        base_url=base_url
    )


@pytest.fixture(scope="module")
def test_project(integration_client):
    """
    Create a test project for integration tests.
    Cleans up after tests complete.
    """
    project = integration_client.zerodb.projects.create(
        name=f"SDK Integration Test {int(time.time())}",
        description="Project created during SDK integration tests",
        metadata={
            "test": True,
            "created_by": "sdk_integration_tests",
            "timestamp": datetime.now().isoformat()
        }
    )
    
    yield project
    
    # Cleanup - delete the project
    try:
        integration_client.zerodb.projects.delete(project["id"])
    except Exception as e:
        print(f"Warning: Failed to cleanup test project {project['id']}: {e}")


@pytest.mark.integration
class TestSDKIntegration:
    """Integration tests for core SDK functionality."""
    
    def test_client_initialization_and_health_check(self, integration_client):
        """Test client initialization and basic connectivity."""
        # Test health check
        try:
            health = integration_client.health_check()
            assert "status" in health
        except APIError as e:
            if e.status_code == 404:
                # Health endpoint might not exist, that's OK
                pytest.skip("Health endpoint not available")
            else:
                raise
    
    def test_authentication_flow(self):
        """Test various authentication scenarios."""
        # Test with invalid API key
        invalid_client = AINativeClient(api_key="invalid-key-12345")
        
        with pytest.raises(AuthenticationError):
            invalid_client.zerodb.projects.list()
    
    def test_project_lifecycle(self, integration_client):
        """Test complete project lifecycle."""
        # Create project
        project = integration_client.zerodb.projects.create(
            name="Lifecycle Test Project",
            description="Testing project lifecycle",
            metadata={"lifecycle_test": True}
        )
        
        project_id = project["id"]
        assert project["name"] == "Lifecycle Test Project"
        
        try:
            # Get project
            retrieved = integration_client.zerodb.projects.get(project_id)
            assert retrieved["id"] == project_id
            assert retrieved["name"] == project["name"]
            
            # Update project
            updated = integration_client.zerodb.projects.update(
                project_id,
                name="Updated Lifecycle Test",
                metadata={"updated": True}
            )
            assert updated["name"] == "Updated Lifecycle Test"
            
            # Get project statistics
            stats = integration_client.zerodb.projects.get_statistics(project_id)
            assert "vector_count" in stats or "storage_bytes" in stats
            
            # Suspend project
            suspended = integration_client.zerodb.projects.suspend(
                project_id,
                reason="Testing suspension"
            )
            assert suspended["status"] == "suspended" or "suspended" in str(suspended).lower()
            
            # Reactivate project
            activated = integration_client.zerodb.projects.activate(project_id)
            # Status should be active or activation should be acknowledged
            
        finally:
            # Cleanup
            integration_client.zerodb.projects.delete(project_id)
    
    def test_vector_operations_workflow(self, integration_client, test_project):
        """Test complete vector operations workflow."""
        project_id = test_project["id"]
        
        # Prepare test vectors
        vectors = [
            np.random.rand(128).tolist() for _ in range(10)
        ]
        metadata = [
            {
                "text": f"Test document {i}",
                "category": "integration_test",
                "index": i
            }
            for i in range(10)
        ]
        ids = [f"test_vec_{i}" for i in range(10)]
        
        # Upsert vectors
        upsert_result = integration_client.zerodb.vectors.upsert(
            project_id=project_id,
            vectors=vectors,
            metadata=metadata,
            ids=ids,
            namespace="integration_test"
        )
        
        assert "upserted" in str(upsert_result).lower() or "success" in str(upsert_result).lower()
        
        # Search vectors
        query_vector = np.random.rand(128).tolist()
        search_results = integration_client.zerodb.vectors.search(
            project_id=project_id,
            vector=query_vector,
            top_k=5,
            namespace="integration_test",
            include_metadata=True
        )
        
        assert isinstance(search_results, list)
        # Should have results or be empty (depending on vector similarity)
        
        # Get specific vectors
        get_results = integration_client.zerodb.vectors.get(
            project_id=project_id,
            ids=ids[:3],  # Get first 3 vectors
            namespace="integration_test",
            include_metadata=True
        )
        
        assert isinstance(get_results, list)
        
        # Update vector metadata
        if get_results and len(get_results) > 0:
            first_vec_id = get_results[0].get("id", ids[0])
            update_result = integration_client.zerodb.vectors.update_metadata(
                project_id=project_id,
                id=first_vec_id,
                metadata={"updated": True, "test": "integration"},
                namespace="integration_test"
            )
            # Should complete without error
        
        # Get index statistics
        index_stats = integration_client.zerodb.vectors.describe_index_stats(
            project_id=project_id,
            namespace="integration_test"
        )
        
        assert isinstance(index_stats, dict)
        
        # Cleanup - delete vectors
        delete_result = integration_client.zerodb.vectors.delete(
            project_id=project_id,
            ids=ids,
            namespace="integration_test"
        )
        # Should complete without error
    
    def test_memory_operations_workflow(self, integration_client, test_project):
        """Test complete memory operations workflow."""
        project_id = test_project["id"]
        
        # Create memories
        memories = []
        for i in range(5):
            memory = integration_client.zerodb.memory.create(
                content=f"Integration test memory content {i}",
                title=f"Test Memory {i}",
                tags=["integration", "test", f"batch_{i//2}"],
                priority=MemoryPriority.MEDIUM if i % 2 == 0 else MemoryPriority.HIGH,
                metadata={"test_index": i, "batch": i//2},
                project_id=project_id
            )
            memories.append(memory)
            assert memory["content"].startswith("Integration test memory")
        
        memory_ids = [mem["id"] for mem in memories]
        
        try:
            # List memories
            memory_list = integration_client.zerodb.memory.list(
                project_id=project_id,
                limit=10
            )
            
            assert isinstance(memory_list, dict)
            assert "memories" in memory_list or isinstance(memory_list, list)
            
            # Search memories
            search_results = integration_client.zerodb.memory.search(
                query="integration test",
                project_id=project_id,
                semantic=True,
                limit=5
            )
            
            assert isinstance(search_results, list)
            
            # Get specific memory
            if memories:
                first_memory = integration_client.zerodb.memory.get(memory_ids[0])
                assert first_memory["id"] == memory_ids[0]
                
                # Update memory
                updated = integration_client.zerodb.memory.update(
                    memory_ids[0],
                    content="Updated integration test content",
                    tags=["updated", "integration", "test"]
                )
                assert "updated" in updated.get("content", "").lower() or updated.get("updated", False)
                
                # Get related memories
                related = integration_client.zerodb.memory.get_related(
                    memory_ids[0],
                    limit=3
                )
                assert isinstance(related, list)
            
            # Bulk create memories
            bulk_memories = [
                {
                    "content": f"Bulk memory {i}",
                    "title": f"Bulk {i}",
                    "tags": ["bulk", "integration"]
                }
                for i in range(3)
            ]
            
            bulk_result = integration_client.zerodb.memory.bulk_create(
                bulk_memories,
                project_id=project_id
            )
            
            assert "created" in str(bulk_result).lower() or "success" in str(bulk_result).lower()
            
        finally:
            # Cleanup memories
            for memory_id in memory_ids:
                try:
                    integration_client.zerodb.memory.delete(memory_id)
                except Exception as e:
                    print(f"Warning: Failed to delete memory {memory_id}: {e}")
    
    def test_analytics_operations(self, integration_client, test_project):
        """Test analytics operations."""
        project_id = test_project["id"]
        
        # Get usage analytics
        usage = integration_client.zerodb.analytics.get_usage(
            project_id=project_id,
            granularity="daily"
        )
        
        assert isinstance(usage, dict)
        
        # Get performance metrics
        performance = integration_client.zerodb.analytics.get_performance_metrics(
            project_id=project_id
        )
        
        assert isinstance(performance, dict)
        
        # Get storage statistics
        storage = integration_client.zerodb.analytics.get_storage_stats(
            project_id=project_id
        )
        
        assert isinstance(storage, dict)
        
        # Get cost analysis
        costs = integration_client.zerodb.analytics.get_cost_analysis(
            project_id=project_id
        )
        
        assert isinstance(costs, dict)
        
        # Get trends
        trends = integration_client.zerodb.analytics.get_trends(
            metric="vectors",
            project_id=project_id,
            period=7
        )
        
        assert isinstance(trends, list)
        
        # Get anomalies
        anomalies = integration_client.zerodb.analytics.get_anomalies(
            project_id=project_id,
            severity="all"
        )
        
        assert isinstance(anomalies, list)
    
    def test_agent_swarm_operations(self, integration_client, test_project):
        """Test agent swarm operations."""
        project_id = test_project["id"]
        
        # Get available agent types
        agent_types = integration_client.agent_swarm.get_agent_types()
        assert isinstance(agent_types, list)
        
        # Define test agents
        agents = [
            {
                "id": "test_researcher_1",
                "type": AgentType.RESEARCHER.value,
                "capabilities": ["research", "analysis"]
            },
            {
                "id": "test_coder_1",
                "type": AgentType.CODER.value,
                "capabilities": ["python", "testing"]
            }
        ]
        
        # Start swarm
        swarm = integration_client.agent_swarm.start_swarm(
            project_id=project_id,
            agents=agents,
            objective="Integration test swarm",
            config={"test_mode": True, "timeout_minutes": 5}
        )
        
        swarm_id = swarm["id"]
        
        try:
            # Get swarm status
            status = integration_client.agent_swarm.get_status(swarm_id)
            assert isinstance(status, dict)
            assert "status" in status
            
            # Get swarm metrics
            metrics = integration_client.agent_swarm.get_metrics(swarm_id=swarm_id)
            assert isinstance(metrics, dict)
            
            # Configure agent
            config_result = integration_client.agent_swarm.configure_agent(
                swarm_id=swarm_id,
                agent_id="test_coder_1",
                config={"temperature": 0.7, "test_mode": True}
            )
            assert isinstance(config_result, dict)
            
            # Set agent prompt
            prompt_result = integration_client.agent_swarm.set_agent_prompt(
                swarm_id=swarm_id,
                agent_id="test_researcher_1",
                prompt="Focus on integration testing scenarios"
            )
            assert isinstance(prompt_result, dict)
            
            # Orchestrate task
            task_result = integration_client.agent_swarm.orchestrate(
                swarm_id=swarm_id,
                task="Analyze integration test requirements",
                context={"test_type": "integration", "priority": "low"}
            )
            assert isinstance(task_result, dict)
            
            # Get swarm history
            history = integration_client.agent_swarm.get_swarm_history(
                swarm_id,
                limit=10
            )
            assert isinstance(history, list)
            
            # Get agent communications
            communications = integration_client.agent_swarm.get_agent_communications(
                swarm_id
            )
            assert isinstance(communications, list)
            
        finally:
            # Stop swarm
            try:
                stop_result = integration_client.agent_swarm.stop_swarm(swarm_id)
                assert isinstance(stop_result, dict)
            except Exception as e:
                print(f"Warning: Failed to stop swarm {swarm_id}: {e}")
    
    def test_error_handling_integration(self, integration_client):
        """Test error handling in integration scenarios."""
        # Test with non-existent project
        with pytest.raises((APIError, ValidationError)):
            integration_client.zerodb.projects.get("nonexistent_project_id")
        
        # Test with invalid vector data
        with pytest.raises((APIError, ValidationError)):
            integration_client.zerodb.vectors.upsert(
                project_id="invalid_project",
                vectors=[],  # Empty vectors
                namespace="test"
            )
        
        # Test with invalid memory data
        with pytest.raises((APIError, ValidationError)):
            integration_client.zerodb.memory.create("")  # Empty content
    
    def test_pagination_and_filtering(self, integration_client, test_project):
        """Test pagination and filtering across different operations."""
        project_id = test_project["id"]
        
        # Test project listing with pagination
        projects_page1 = integration_client.zerodb.projects.list(
            limit=5,
            offset=0
        )
        assert isinstance(projects_page1, dict)
        
        projects_page2 = integration_client.zerodb.projects.list(
            limit=5,
            offset=5
        )
        assert isinstance(projects_page2, dict)
        
        # Test memory listing with filters
        memories = integration_client.zerodb.memory.list(
            project_id=project_id,
            limit=10,
            offset=0
        )
        assert isinstance(memories, dict) or isinstance(memories, list)


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Performance-focused integration tests."""
    
    def test_bulk_vector_operations(self, integration_client, test_project):
        """Test bulk vector operations performance."""
        project_id = test_project["id"]
        
        # Generate large batch of vectors
        batch_size = 100
        vectors = [np.random.rand(256).tolist() for _ in range(batch_size)]
        metadata = [{"index": i, "batch": "performance_test"} for i in range(batch_size)]
        ids = [f"perf_vec_{i}" for i in range(batch_size)]
        
        start_time = time.time()
        
        # Bulk upsert
        upsert_result = integration_client.zerodb.vectors.upsert(
            project_id=project_id,
            vectors=vectors,
            metadata=metadata,
            ids=ids,
            namespace="performance_test"
        )
        
        upsert_time = time.time() - start_time
        print(f"Bulk upsert of {batch_size} vectors took {upsert_time:.2f} seconds")
        
        # Bulk search operations
        search_times = []
        for _ in range(10):
            query_vector = np.random.rand(256).tolist()
            start_search = time.time()
            
            results = integration_client.zerodb.vectors.search(
                project_id=project_id,
                vector=query_vector,
                top_k=10,
                namespace="performance_test"
            )
            
            search_time = time.time() - start_search
            search_times.append(search_time)
        
        avg_search_time = sum(search_times) / len(search_times)
        print(f"Average search time: {avg_search_time:.3f} seconds")
        
        # Cleanup
        try:
            integration_client.zerodb.vectors.delete(
                project_id=project_id,
                ids=ids,
                namespace="performance_test"
            )
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")
        
        # Assert reasonable performance
        assert upsert_time < 30  # Should complete within 30 seconds
        assert avg_search_time < 2  # Average search should be under 2 seconds
    
    def test_concurrent_operations(self, integration_client, test_project):
        """Test concurrent operations handling."""
        import threading
        import queue
        
        project_id = test_project["id"]
        results = queue.Queue()
        errors = queue.Queue()
        
        def create_memory(index):
            try:
                memory = integration_client.zerodb.memory.create(
                    content=f"Concurrent memory {index}",
                    title=f"Concurrent {index}",
                    tags=["concurrent", "test"],
                    project_id=project_id
                )
                results.put(memory)
            except Exception as e:
                errors.put(e)
        
        # Create memories concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_memory, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Check results
        created_memories = []
        while not results.empty():
            created_memories.append(results.get())
        
        concurrent_errors = []
        while not errors.empty():
            concurrent_errors.append(errors.get())
        
        print(f"Created {len(created_memories)} memories concurrently")
        print(f"Encountered {len(concurrent_errors)} errors")
        
        # Cleanup
        for memory in created_memories:
            try:
                integration_client.zerodb.memory.delete(memory["id"])
            except Exception as e:
                print(f"Warning: Failed to cleanup memory {memory['id']}: {e}")
        
        # Should have created most memories successfully
        assert len(created_memories) >= 7  # Allow for some failures due to rate limiting


@pytest.mark.integration
@pytest.mark.network
class TestNetworkResilienceIntegration:
    """Test network resilience and retry behavior."""
    
    def test_retry_behavior(self, integration_client):
        """Test that the client properly retries failed requests."""
        # This test would ideally use a test server that can simulate failures
        # For now, we test that the client can handle normal operations
        
        try:
            projects = integration_client.zerodb.projects.list(limit=1)
            assert isinstance(projects, dict) or isinstance(projects, list)
        except NetworkError:
            # Network errors are expected in some test environments
            pytest.skip("Network not available for retry testing")
    
    def test_timeout_handling(self, integration_client):
        """Test timeout handling."""
        # Test with very short timeout (this might fail in slow environments)
        from ainative.client import ClientConfig
        from ainative.auth import AuthConfig
        
        short_timeout_config = ClientConfig(timeout=0.1)  # Very short timeout
        
        short_timeout_client = AINativeClient(
            api_key=os.getenv("AINATIVE_TEST_API_KEY", "test-key"),
            config=short_timeout_config
        )
        
        # This request should either succeed quickly or timeout
        try:
            result = short_timeout_client.zerodb.projects.list(limit=1)
            # If it succeeds, that's fine too
            assert isinstance(result, (dict, list))
        except (NetworkError, APIError):
            # Timeout or network error is expected
            pass
        finally:
            short_timeout_client.close()


if __name__ == "__main__":
    # Allow running integration tests directly
    pytest.main([__file__, "-v", "--tb=short"])