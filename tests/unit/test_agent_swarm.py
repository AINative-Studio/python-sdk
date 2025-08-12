"""
Unit tests for the Agent Swarm module.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from ainative.agent_swarm import AgentSwarmClient, AgentType, SwarmStatus


class TestAgentType:
    """Test AgentType enum."""
    
    def test_agent_type_values(self):
        """Test all agent type enum values."""
        assert AgentType.RESEARCHER.value == "researcher"
        assert AgentType.CODER.value == "coder"
        assert AgentType.REVIEWER.value == "reviewer"
        assert AgentType.TESTER.value == "tester"
        assert AgentType.DOCUMENTER.value == "documenter"
        assert AgentType.ANALYST.value == "analyst"
        assert AgentType.DESIGNER.value == "designer"
        assert AgentType.ORCHESTRATOR.value == "orchestrator"
    
    def test_agent_type_membership(self):
        """Test enum membership."""
        types = [
            AgentType.RESEARCHER, AgentType.CODER, AgentType.REVIEWER,
            AgentType.TESTER, AgentType.DOCUMENTER, AgentType.ANALYST,
            AgentType.DESIGNER, AgentType.ORCHESTRATOR
        ]
        for agent_type in types:
            assert agent_type in AgentType


class TestSwarmStatus:
    """Test SwarmStatus enum."""
    
    def test_swarm_status_values(self):
        """Test all swarm status enum values."""
        assert SwarmStatus.IDLE.value == "idle"
        assert SwarmStatus.STARTING.value == "starting"
        assert SwarmStatus.RUNNING.value == "running"
        assert SwarmStatus.PAUSED.value == "paused"
        assert SwarmStatus.STOPPING.value == "stopping"
        assert SwarmStatus.COMPLETED.value == "completed"
        assert SwarmStatus.FAILED.value == "failed"


class TestAgentSwarmClient:
    """Test AgentSwarmClient class."""
    
    @pytest.fixture
    def swarm_client(self, client):
        """Create AgentSwarmClient instance."""
        return AgentSwarmClient(client)
    
    def test_init(self, client):
        """Test initialization."""
        swarm = AgentSwarmClient(client)
        assert swarm.client == client
        assert swarm.base_path == "/agent-swarm"
    
    def test_start_swarm_basic(self, swarm_client, sample_swarm):
        """Test starting a basic swarm."""
        agents = [
            {
                "id": "researcher_1",
                "type": "researcher",
                "capabilities": ["web_search", "analysis"]
            }
        ]
        swarm_client.client.post.return_value = sample_swarm
        
        result = swarm_client.start_swarm(
            project_id="proj_123",
            agents=agents,
            objective="Research market trends"
        )
        
        assert result == sample_swarm
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["project_id"] == "proj_123"
        assert data["agents"] == agents
        assert data["objective"] == "Research market trends"
        assert data["config"] == {}
    
    def test_start_swarm_with_config(self, swarm_client, sample_swarm):
        """Test starting swarm with configuration."""
        agents = [{"id": "coder_1", "type": "coder"}]
        config = {
            "max_iterations": 10,
            "timeout_minutes": 30,
            "coordination_mode": "sequential"
        }
        swarm_client.client.post.return_value = sample_swarm
        
        result = swarm_client.start_swarm(
            project_id="proj_456",
            agents=agents,
            objective="Implement feature",
            config=config
        )
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["config"] == config
        assert data["project_id"] == "proj_456"
    
    def test_start_swarm_multiple_agents(self, swarm_client, sample_swarm):
        """Test starting swarm with multiple agents."""
        agents = [
            {"id": "researcher_1", "type": "researcher", "capabilities": ["research"]},
            {"id": "coder_1", "type": "coder", "capabilities": ["python", "javascript"]},
            {"id": "reviewer_1", "type": "reviewer", "capabilities": ["code_review"]},
            {"id": "tester_1", "type": "tester", "capabilities": ["unit_testing"]}
        ]
        swarm_client.client.post.return_value = sample_swarm
        
        result = swarm_client.start_swarm(
            project_id="proj_multi",
            agents=agents,
            objective="Full development cycle"
        )
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert len(data["agents"]) == 4
        assert data["agents"] == agents
    
    def test_orchestrate_basic(self, swarm_client):
        """Test basic orchestration."""
        orchestration_result = {
            "task_id": "task_123",
            "status": "assigned",
            "agents": ["coder_1", "reviewer_1"]
        }
        swarm_client.client.post.return_value = orchestration_result
        
        result = swarm_client.orchestrate(
            swarm_id="swarm_123",
            task="Implement user authentication"
        )
        
        assert result == orchestration_result
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["swarm_id"] == "swarm_123"
        assert data["task"] == "Implement user authentication"
        assert data["context"] == {}
        assert "agents" not in data
    
    def test_orchestrate_with_context(self, swarm_client):
        """Test orchestration with context."""
        context = {
            "framework": "FastAPI",
            "database": "PostgreSQL",
            "requirements": ["JWT tokens", "password hashing"]
        }
        swarm_client.client.post.return_value = {"task_id": "task_456"}
        
        result = swarm_client.orchestrate(
            swarm_id="swarm_456",
            task="Build authentication system",
            context=context,
            agents=["coder_1", "security_specialist_1"]
        )
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["context"] == context
        assert data["agents"] == ["coder_1", "security_specialist_1"]
    
    def test_get_status(self, swarm_client):
        """Test getting swarm status."""
        status_data = {
            "id": "swarm_123",
            "status": "running",
            "progress": 65,
            "active_agents": 3,
            "completed_tasks": 8,
            "pending_tasks": 4
        }
        swarm_client.client.get.return_value = status_data
        
        result = swarm_client.get_status("swarm_123")
        
        assert result == status_data
        swarm_client.client.get.assert_called_once_with("/agent-swarm/swarm_123/status")
    
    def test_get_metrics_swarm_specific(self, swarm_client):
        """Test getting metrics for specific swarm."""
        metrics_data = {
            "swarm_id": "swarm_123",
            "tasks_completed": 15,
            "avg_task_duration": 45.6,
            "agent_utilization": 78.5,
            "total_tokens": 25000
        }
        swarm_client.client.get.return_value = metrics_data
        
        result = swarm_client.get_metrics(swarm_id="swarm_123")
        
        assert result == metrics_data
        
        call_args = swarm_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["swarm_id"] == "swarm_123"
        assert "project_id" not in params
    
    def test_get_metrics_project_specific(self, swarm_client):
        """Test getting metrics for specific project."""
        metrics_data = {
            "project_id": "proj_456",
            "total_swarms": 5,
            "active_swarms": 2
        }
        swarm_client.client.get.return_value = metrics_data
        
        result = swarm_client.get_metrics(project_id="proj_456")
        
        call_args = swarm_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["project_id"] == "proj_456"
        assert "swarm_id" not in params
    
    def test_get_metrics_both_filters(self, swarm_client):
        """Test getting metrics with both swarm and project filters."""
        swarm_client.client.get.return_value = {}
        
        swarm_client.get_metrics(swarm_id="swarm_123", project_id="proj_456")
        
        call_args = swarm_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["swarm_id"] == "swarm_123"
        assert params["project_id"] == "proj_456"
    
    def test_get_metrics_no_filters(self, swarm_client):
        """Test getting metrics without filters."""
        swarm_client.client.get.return_value = {"global_metrics": True}
        
        swarm_client.get_metrics()
        
        call_args = swarm_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert len(params) == 0
    
    def test_get_agent_types(self, swarm_client):
        """Test getting available agent types."""
        agent_types_data = [
            {
                "type": "researcher",
                "description": "Conducts research and gathers information",
                "capabilities": ["web_search", "document_analysis"]
            },
            {
                "type": "coder",
                "description": "Writes and maintains code",
                "capabilities": ["python", "javascript", "testing"]
            }
        ]
        swarm_client.client.get.return_value = {"agent_types": agent_types_data}
        
        result = swarm_client.get_agent_types()
        
        assert result == agent_types_data
        swarm_client.client.get.assert_called_once_with("/agent-swarm/agent-types")
    
    def test_get_agent_types_empty(self, swarm_client):
        """Test getting agent types when none are available."""
        swarm_client.client.get.return_value = {}
        
        result = swarm_client.get_agent_types()
        
        assert result == []
    
    def test_configure_agent(self, swarm_client):
        """Test configuring a specific agent."""
        agent_config = {
            "temperature": 0.8,
            "max_tokens": 2500,
            "specialized_knowledge": ["security", "authentication"],
            "response_style": "detailed"
        }
        config_response = {"configured": True, "agent_id": "coder_1"}
        swarm_client.client.put.return_value = config_response
        
        result = swarm_client.configure_agent(
            swarm_id="swarm_123",
            agent_id="coder_1",
            config=agent_config
        )
        
        assert result == config_response
        swarm_client.client.put.assert_called_once_with(
            "/agent-swarm/swarm_123/agents/coder_1/config",
            data=agent_config
        )
    
    def test_set_agent_prompt_basic(self, swarm_client):
        """Test setting agent prompt."""
        prompt_response = {"updated": True, "agent_id": "researcher_1"}
        swarm_client.client.post.return_value = prompt_response
        
        result = swarm_client.set_agent_prompt(
            swarm_id="swarm_456",
            agent_id="researcher_1",
            prompt="Focus on finding recent academic papers and industry reports"
        )
        
        assert result == prompt_response
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["prompt"] == "Focus on finding recent academic papers and industry reports"
        assert "system_prompt" not in data
        
        # Verify URL
        assert call_args[0][0] == "/agent-swarm/swarm_456/agents/researcher_1/prompt"
    
    def test_set_agent_prompt_with_system(self, swarm_client):
        """Test setting agent prompt with system prompt."""
        swarm_client.client.post.return_value = {"updated": True}
        
        result = swarm_client.set_agent_prompt(
            swarm_id="swarm_789",
            agent_id="coder_1",
            prompt="Write clean, well-documented code",
            system_prompt="You are a senior software engineer with expertise in Python and FastAPI"
        )
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["prompt"] == "Write clean, well-documented code"
        assert data["system_prompt"] == "You are a senior software engineer with expertise in Python and FastAPI"
    
    def test_stop_swarm_graceful(self, swarm_client):
        """Test gracefully stopping swarm."""
        stop_response = {
            "stopped": True,
            "swarm_id": "swarm_123",
            "cleanup_completed": True
        }
        swarm_client.client.post.return_value = stop_response
        
        result = swarm_client.stop_swarm("swarm_123")
        
        assert result == stop_response
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["force"] is False
        assert call_args[0][0] == "/agent-swarm/swarm_123/stop"
    
    def test_stop_swarm_force(self, swarm_client):
        """Test force stopping swarm."""
        swarm_client.client.post.return_value = {"stopped": True, "forced": True}
        
        result = swarm_client.stop_swarm("swarm_456", force=True)
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["force"] is True
    
    def test_pause_swarm(self, swarm_client):
        """Test pausing swarm."""
        pause_response = {
            "paused": True,
            "swarm_id": "swarm_123",
            "paused_at": "2024-01-01T12:00:00Z"
        }
        swarm_client.client.post.return_value = pause_response
        
        result = swarm_client.pause_swarm("swarm_123")
        
        assert result == pause_response
        swarm_client.client.post.assert_called_once_with("/agent-swarm/swarm_123/pause")
    
    def test_resume_swarm(self, swarm_client):
        """Test resuming swarm."""
        resume_response = {
            "resumed": True,
            "swarm_id": "swarm_123",
            "resumed_at": "2024-01-01T12:05:00Z"
        }
        swarm_client.client.post.return_value = resume_response
        
        result = swarm_client.resume_swarm("swarm_123")
        
        assert result == resume_response
        swarm_client.client.post.assert_called_once_with("/agent-swarm/swarm_123/resume")
    
    def test_get_swarm_history(self, swarm_client):
        """Test getting swarm execution history."""
        history_data = [
            {
                "timestamp": "2024-01-01T10:00:00Z",
                "event": "swarm_started",
                "description": "Swarm initialized with 3 agents"
            },
            {
                "timestamp": "2024-01-01T10:05:00Z",
                "event": "task_assigned",
                "description": "Research task assigned to researcher_1"
            }
        ]
        swarm_client.client.get.return_value = {"history": history_data}
        
        result = swarm_client.get_swarm_history("swarm_123", limit=50)
        
        assert result == history_data
        
        call_args = swarm_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["limit"] == 50
        assert call_args[0][0] == "/agent-swarm/swarm_123/history"
    
    def test_get_swarm_history_default_limit(self, swarm_client):
        """Test getting swarm history with default limit."""
        swarm_client.client.get.return_value = {"history": []}
        
        swarm_client.get_swarm_history("swarm_456")
        
        call_args = swarm_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["limit"] == 100  # Default
    
    def test_get_swarm_history_empty(self, swarm_client):
        """Test getting swarm history when none exists."""
        swarm_client.client.get.return_value = {}
        
        result = swarm_client.get_swarm_history("swarm_789")
        
        assert result == []
    
    def test_get_agent_communications_all(self, swarm_client):
        """Test getting all agent communications."""
        comm_data = [
            {
                "id": "comm_1",
                "from_agent": "researcher_1",
                "to_agent": "coder_1",
                "message_type": "task_handoff",
                "timestamp": "2024-01-01T11:00:00Z"
            },
            {
                "id": "comm_2",
                "from_agent": "coder_1",
                "to_agent": "reviewer_1",
                "message_type": "code_review_request",
                "timestamp": "2024-01-01T11:30:00Z"
            }
        ]
        swarm_client.client.get.return_value = {"communications": comm_data}
        
        result = swarm_client.get_agent_communications("swarm_123")
        
        assert result == comm_data
        
        call_args = swarm_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert len(params) == 0  # No agent filter
        assert call_args[0][0] == "/agent-swarm/swarm_123/communications"
    
    def test_get_agent_communications_specific_agent(self, swarm_client):
        """Test getting communications for specific agent."""
        swarm_client.client.get.return_value = {"communications": []}
        
        result = swarm_client.get_agent_communications(
            swarm_id="swarm_456",
            agent_id="coder_1"
        )
        
        call_args = swarm_client.client.get.call_args
        params = call_args[1]["params"]
        
        assert params["agent_id"] == "coder_1"
    
    def test_get_agent_communications_empty(self, swarm_client):
        """Test getting communications when none exist."""
        swarm_client.client.get.return_value = {}
        
        result = swarm_client.get_agent_communications("swarm_empty")
        
        assert result == []
    
    def test_create_agent(self, swarm_client, sample_agent):
        """Test creating custom agent template."""
        swarm_client.client.post.return_value = sample_agent
        
        result = swarm_client.create_agent(
            name="API Security Specialist",
            agent_type=AgentType.REVIEWER,
            capabilities=["security_audit", "penetration_testing"],
            prompt="Focus on API security vulnerabilities",
            config={"temperature": 0.3, "expertise": "security"}
        )
        
        assert result == sample_agent
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["name"] == "API Security Specialist"
        assert data["type"] == "reviewer"
        assert data["capabilities"] == ["security_audit", "penetration_testing"]
        assert data["prompt"] == "Focus on API security vulnerabilities"
        assert data["config"] == {"temperature": 0.3, "expertise": "security"}
        
        # Verify endpoint
        assert call_args[0][0] == "/agent-swarm/agents"
    
    def test_create_agent_minimal(self, swarm_client, sample_agent):
        """Test creating agent with minimal parameters."""
        swarm_client.client.post.return_value = sample_agent
        
        result = swarm_client.create_agent(
            name="Simple Agent",
            agent_type=AgentType.ANALYST,
            capabilities=["data_analysis"],
            prompt="Analyze data patterns"
        )
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert data["config"] == {}  # Default empty config


class TestAgentSwarmClientIntegration:
    """Test AgentSwarmClient integration scenarios."""
    
    @pytest.fixture
    def swarm_client(self, client):
        return AgentSwarmClient(client)
    
    def test_full_swarm_lifecycle(self, swarm_client, sample_swarm, sample_agent):
        """Test complete swarm lifecycle."""
        # Mock responses for each step
        start_response = sample_swarm.copy()
        status_response = {"status": "running", "progress": 50}
        orchestrate_response = {"task_id": "task_123", "assigned": True}
        pause_response = {"paused": True}
        resume_response = {"resumed": True}
        stop_response = {"stopped": True}
        
        swarm_client.client.post.side_effect = [
            start_response,
            orchestrate_response,
            pause_response,
            resume_response,
            stop_response
        ]
        swarm_client.client.get.return_value = status_response
        
        # Start swarm
        agents = [{"id": "coder_1", "type": "coder"}]
        started = swarm_client.start_swarm(
            project_id="proj_lifecycle",
            agents=agents,
            objective="Complete development task"
        )
        assert started == start_response
        
        # Check status
        status = swarm_client.get_status("swarm_test123")
        assert status == status_response
        
        # Orchestrate task
        orchestrated = swarm_client.orchestrate(
            swarm_id="swarm_test123",
            task="Implement feature"
        )
        assert orchestrated == orchestrate_response
        
        # Pause swarm
        paused = swarm_client.pause_swarm("swarm_test123")
        assert paused == pause_response
        
        # Resume swarm
        resumed = swarm_client.resume_swarm("swarm_test123")
        assert resumed == resume_response
        
        # Stop swarm
        stopped = swarm_client.stop_swarm("swarm_test123")
        assert stopped == stop_response
    
    def test_multi_agent_coordination(self, swarm_client, sample_swarm):
        """Test coordination between multiple agents."""
        # Complex agent setup
        agents = [
            {
                "id": "pm_1",
                "type": "orchestrator",
                "capabilities": ["project_management", "coordination"],
                "config": {"priority": "high"}
            },
            {
                "id": "researcher_1",
                "type": "researcher",
                "capabilities": ["market_research", "competitive_analysis"],
                "config": {"depth": "comprehensive"}
            },
            {
                "id": "architect_1",
                "type": "designer",
                "capabilities": ["system_design", "architecture"],
                "config": {"focus": "scalability"}
            },
            {
                "id": "dev_lead_1",
                "type": "coder",
                "capabilities": ["full_stack", "team_leadership"],
                "config": {"experience_level": "senior"}
            },
            {
                "id": "qa_lead_1",
                "type": "tester",
                "capabilities": ["test_strategy", "automation"],
                "config": {"methodology": "agile"}
            }
        ]
        
        swarm_client.client.post.return_value = sample_swarm
        
        result = swarm_client.start_swarm(
            project_id="proj_complex",
            agents=agents,
            objective="Build enterprise application",
            config={
                "coordination_mode": "hierarchical",
                "communication_protocol": "structured",
                "max_parallel_tasks": 3
            }
        )
        
        call_args = swarm_client.client.post.call_args
        data = call_args[1]["data"]
        
        assert len(data["agents"]) == 5
        assert data["config"]["coordination_mode"] == "hierarchical"
    
    def test_agent_specialization_workflow(self, swarm_client, sample_agent):
        """Test creating and configuring specialized agents."""
        specializations = [
            {
                "name": "Security Auditor",
                "type": AgentType.REVIEWER,
                "capabilities": ["security_audit", "vulnerability_assessment"],
                "prompt": "Focus on security vulnerabilities and best practices",
                "config": {"security_frameworks": ["OWASP", "NIST"]}
            },
            {
                "name": "Performance Optimizer",
                "type": AgentType.ANALYST,
                "capabilities": ["performance_analysis", "optimization"],
                "prompt": "Analyze and optimize system performance",
                "config": {"metrics_focus": ["latency", "throughput"]}
            },
            {
                "name": "Documentation Writer",
                "type": AgentType.DOCUMENTER,
                "capabilities": ["technical_writing", "api_documentation"],
                "prompt": "Create comprehensive technical documentation",
                "config": {"documentation_style": "detailed"}
            }
        ]
        
        created_agents = []
        for spec in specializations:
            swarm_client.client.post.return_value = {
                "id": f"agent_{spec['name'].lower().replace(' ', '_')}",
                **spec
            }
            
            agent = swarm_client.create_agent(**spec)
            created_agents.append(agent)
        
        assert len(created_agents) == 3
        
        # Verify each agent was created with correct specialization
        for i, agent in enumerate(created_agents):
            spec = specializations[i]
            assert agent["name"] == spec["name"]
            assert agent["capabilities"] == spec["capabilities"]
    
    def test_task_orchestration_patterns(self, swarm_client):
        """Test different task orchestration patterns."""
        orchestration_patterns = [
            # Sequential task flow
            {
                "task": "Research user requirements",
                "agents": ["researcher_1"],
                "context": {"phase": "discovery", "priority": "high"}
            },
            # Parallel task execution
            {
                "task": "Design system architecture",
                "agents": ["architect_1", "designer_1"],
                "context": {"phase": "design", "parallel": True}
            },
            # Collaborative task
            {
                "task": "Implement core features",
                "agents": ["coder_1", "coder_2", "reviewer_1"],
                "context": {"phase": "implementation", "review_required": True}
            },
            # Cross-functional task
            {
                "task": "Prepare production deployment",
                "agents": ["coder_1", "tester_1", "devops_1", "documenter_1"],
                "context": {"phase": "deployment", "cross_functional": True}
            }
        ]
        
        swarm_client.client.post.return_value = {"task_assigned": True}
        
        for pattern in orchestration_patterns:
            result = swarm_client.orchestrate(
                swarm_id="swarm_patterns",
                task=pattern["task"],
                context=pattern["context"],
                agents=pattern["agents"]
            )
            
            call_args = swarm_client.client.post.call_args
            data = call_args[1]["data"]
            
            assert data["task"] == pattern["task"]
            assert data["agents"] == pattern["agents"]
            assert data["context"] == pattern["context"]
            
            swarm_client.client.post.reset_mock()
    
    def test_swarm_monitoring_and_analytics(self, swarm_client):
        """Test comprehensive swarm monitoring."""
        # Mock different monitoring responses
        status_data = {"status": "running", "active_agents": 4, "progress": 75}
        metrics_data = {
            "tasks_completed": 25,
            "avg_task_duration": 180.5,
            "agent_utilization": 85.2,
            "communication_count": 150
        }
        history_data = [
            {"event": "task_completed", "agent": "coder_1", "duration": 120},
            {"event": "collaboration_initiated", "agents": ["coder_1", "reviewer_1"]}
        ]
        comm_data = [
            {"from": "researcher_1", "to": "coder_1", "type": "requirements_handoff"},
            {"from": "coder_1", "to": "tester_1", "type": "code_review_request"}
        ]
        
        swarm_client.client.get.side_effect = [
            status_data,
            metrics_data,
            {"history": history_data},
            {"communications": comm_data}
        ]
        
        # Get comprehensive monitoring data
        status = swarm_client.get_status("swarm_monitor")
        assert status["progress"] == 75
        
        metrics = swarm_client.get_metrics(swarm_id="swarm_monitor")
        assert metrics["tasks_completed"] == 25
        
        history = swarm_client.get_swarm_history("swarm_monitor", limit=20)
        assert len(history) == 2
        
        communications = swarm_client.get_agent_communications("swarm_monitor")
        assert len(communications) == 2
    
    def test_error_recovery_scenarios(self, swarm_client):
        """Test error handling and recovery scenarios."""
        from ainative.exceptions import APIError
        
        error_scenarios = [
            # Swarm not found
            (404, "Swarm not found"),
            # Invalid configuration
            (400, "Invalid swarm configuration"),
            # Resource exhaustion
            (429, "Too many active swarms"),
            # Internal server error
            (500, "Swarm orchestration failed")
        ]
        
        for status_code, error_message in error_scenarios:
            swarm_client.client.post.side_effect = APIError(
                error_message,
                status_code=status_code
            )
            
            with pytest.raises(APIError) as exc_info:
                swarm_client.start_swarm(
                    project_id="proj_error",
                    agents=[{"id": "agent_1", "type": "coder"}],
                    objective="Test error handling"
                )
            
            assert exc_info.value.status_code == status_code
            
            # Reset for next test
            swarm_client.client.post.side_effect = None
    
    def test_agent_configuration_management(self, swarm_client):
        """Test agent configuration management."""
        # Test different configuration scenarios
        config_scenarios = [
            # Performance tuning
            {
                "agent_id": "coder_1",
                "config": {
                    "temperature": 0.5,
                    "max_tokens": 3000,
                    "response_time_target": "fast"
                }
            },
            # Specialized knowledge
            {
                "agent_id": "security_1",
                "config": {
                    "temperature": 0.2,
                    "knowledge_domains": ["security", "compliance"],
                    "audit_level": "strict"
                }
            },
            # Collaboration settings
            {
                "agent_id": "pm_1",
                "config": {
                    "communication_style": "structured",
                    "coordination_level": "high",
                    "reporting_frequency": "real_time"
                }
            }
        ]
        
        swarm_client.client.put.return_value = {"configured": True}
        swarm_client.client.post.return_value = {"prompt_updated": True}
        
        for scenario in config_scenarios:
            # Configure agent
            config_result = swarm_client.configure_agent(
                swarm_id="swarm_config",
                agent_id=scenario["agent_id"],
                config=scenario["config"]
            )
            
            # Set specialized prompt
            prompt_result = swarm_client.set_agent_prompt(
                swarm_id="swarm_config",
                agent_id=scenario["agent_id"],
                prompt=f"Specialized prompt for {scenario['agent_id']}"
            )
            
            assert config_result["configured"] is True
            assert prompt_result["prompt_updated"] is True