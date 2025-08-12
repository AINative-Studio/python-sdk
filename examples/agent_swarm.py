#!/usr/bin/env python3
"""
Agent Swarm Example for AINative Python SDK

Demonstrates how to orchestrate multiple AI agents for complex tasks.
"""

import os
import time
from ainative import AINativeClient
from ainative.agent_swarm import AgentType, SwarmStatus


def main():
    # Initialize client
    api_key = os.getenv("AINATIVE_API_KEY", "your-api-key-here")
    client = AINativeClient(api_key=api_key)
    
    print("🤖 AINative Agent Swarm Example\n")
    
    try:
        # Create a project for agent swarm
        print("Setting up project...")
        project = client.zerodb.projects.create(
            name="Agent Swarm Demo",
            description="Multi-agent orchestration example"
        )
        project_id = project["id"]
        print(f"✅ Project created: {project_id}\n")
        
        # Get available agent types
        print("Available Agent Types:")
        agent_types = client.agent_swarm.get_agent_types()
        for agent_type in agent_types:
            print(f"   - {agent_type['type']}: {agent_type['description']}")
        print()
        
        # Define agent team for a software development task
        print("Configuring agent team for software development...")
        agents = [
            {
                "id": "researcher_001",
                "type": AgentType.RESEARCHER.value,
                "name": "Research Agent",
                "capabilities": ["web_search", "documentation_analysis", "best_practices"],
                "config": {
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "focus_areas": ["security", "performance", "scalability"]
                }
            },
            {
                "id": "coder_001",
                "type": AgentType.CODER.value,
                "name": "Senior Developer",
                "capabilities": ["python", "javascript", "sql", "api_design"],
                "config": {
                    "temperature": 0.5,
                    "max_tokens": 3000,
                    "code_style": "clean_code",
                    "languages": ["Python", "TypeScript"]
                }
            },
            {
                "id": "reviewer_001",
                "type": AgentType.REVIEWER.value,
                "name": "Code Reviewer",
                "capabilities": ["code_review", "security_audit", "performance_analysis"],
                "config": {
                    "temperature": 0.3,
                    "max_tokens": 1500,
                    "review_focus": ["security", "efficiency", "maintainability"]
                }
            },
            {
                "id": "tester_001",
                "type": AgentType.TESTER.value,
                "name": "QA Engineer",
                "capabilities": ["unit_testing", "integration_testing", "test_automation"],
                "config": {
                    "temperature": 0.4,
                    "max_tokens": 2000,
                    "testing_frameworks": ["pytest", "jest", "selenium"]
                }
            },
            {
                "id": "documenter_001",
                "type": AgentType.DOCUMENTER.value,
                "name": "Technical Writer",
                "capabilities": ["api_documentation", "user_guides", "code_comments"],
                "config": {
                    "temperature": 0.6,
                    "max_tokens": 2500,
                    "documentation_style": "comprehensive"
                }
            }
        ]
        print(f"✅ Configured {len(agents)} agents\n")
        
        # Start the agent swarm
        print("Starting agent swarm...")
        swarm = client.agent_swarm.start_swarm(
            project_id=project_id,
            agents=agents,
            objective="Build a secure REST API for user authentication with JWT tokens",
            config={
                "coordination_mode": "collaborative",
                "communication_protocol": "async",
                "max_iterations": 10,
                "timeout_minutes": 30
            }
        )
        swarm_id = swarm["id"]
        print(f"✅ Swarm started: {swarm_id}\n")
        
        # Check swarm status
        status = client.agent_swarm.get_status(swarm_id)
        print(f"Swarm Status: {status['status']}")
        print(f"Active Agents: {status.get('active_agents', 0)}")
        print(f"Progress: {status.get('progress', 0)}%\n")
        
        # Task 1: Research Phase
        print("📚 Task 1: Research best practices for JWT authentication")
        research_result = client.agent_swarm.orchestrate(
            swarm_id=swarm_id,
            task="Research current best practices for implementing JWT authentication in REST APIs",
            context={
                "requirements": [
                    "Security best practices",
                    "Token refresh strategies",
                    "Storage recommendations",
                    "Common vulnerabilities to avoid"
                ],
                "target_framework": "FastAPI with Python"
            },
            agents=["researcher_001"]
        )
        print(f"   ✅ Research completed\n")
        
        # Task 2: Design Phase
        print("📐 Task 2: Design the authentication system")
        design_result = client.agent_swarm.orchestrate(
            swarm_id=swarm_id,
            task="Design a secure authentication system based on the research findings",
            context={
                "research_findings": research_result.get("output", {}),
                "requirements": [
                    "User registration endpoint",
                    "Login endpoint with JWT generation",
                    "Token refresh endpoint",
                    "Password reset flow",
                    "Role-based access control"
                ]
            },
            agents=["coder_001", "reviewer_001"]
        )
        print(f"   ✅ Design completed\n")
        
        # Task 3: Implementation Phase
        print("💻 Task 3: Implement the authentication endpoints")
        implementation_result = client.agent_swarm.orchestrate(
            swarm_id=swarm_id,
            task="Implement the JWT authentication system with all specified endpoints",
            context={
                "design": design_result.get("output", {}),
                "technology_stack": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "jwt_library": "python-jose",
                    "password_hashing": "passlib with bcrypt"
                }
            },
            agents=["coder_001"]
        )
        print(f"   ✅ Implementation completed\n")
        
        # Task 4: Code Review Phase
        print("🔍 Task 4: Review the implementation")
        review_result = client.agent_swarm.orchestrate(
            swarm_id=swarm_id,
            task="Review the implemented code for security vulnerabilities and best practices",
            context={
                "code": implementation_result.get("output", {}),
                "review_criteria": [
                    "Security vulnerabilities",
                    "Code quality",
                    "Performance implications",
                    "Error handling",
                    "Input validation"
                ]
            },
            agents=["reviewer_001"]
        )
        print(f"   ✅ Code review completed\n")
        
        # Task 5: Testing Phase
        print("🧪 Task 5: Create comprehensive tests")
        testing_result = client.agent_swarm.orchestrate(
            swarm_id=swarm_id,
            task="Create unit and integration tests for the authentication system",
            context={
                "implementation": implementation_result.get("output", {}),
                "test_requirements": [
                    "Unit tests for each endpoint",
                    "Integration tests for auth flow",
                    "Edge cases and error scenarios",
                    "Security test cases",
                    "Performance tests"
                ]
            },
            agents=["tester_001"]
        )
        print(f"   ✅ Test suite created\n")
        
        # Task 6: Documentation Phase
        print("📝 Task 6: Generate documentation")
        documentation_result = client.agent_swarm.orchestrate(
            swarm_id=swarm_id,
            task="Create comprehensive documentation for the authentication API",
            context={
                "implementation": implementation_result.get("output", {}),
                "documentation_requirements": [
                    "API endpoint documentation",
                    "Authentication flow diagrams",
                    "Setup and configuration guide",
                    "Security considerations",
                    "Example code snippets"
                ]
            },
            agents=["documenter_001"]
        )
        print(f"   ✅ Documentation generated\n")
        
        # Configure specific agent with custom prompts
        print("Configuring agents with specialized prompts...")
        client.agent_swarm.set_agent_prompt(
            swarm_id=swarm_id,
            agent_id="reviewer_001",
            prompt="Focus on OWASP Top 10 vulnerabilities and ensure all inputs are properly validated",
            system_prompt="You are a senior security engineer specializing in authentication systems"
        )
        print("   ✅ Agent prompts configured\n")
        
        # Get swarm metrics
        print("Performance Metrics:")
        metrics = client.agent_swarm.get_metrics(swarm_id=swarm_id)
        print(f"   Total tasks completed: {metrics.get('tasks_completed', 0)}")
        print(f"   Average task duration: {metrics.get('avg_task_duration', 0):.2f}s")
        print(f"   Agent utilization: {metrics.get('agent_utilization', 0):.1f}%")
        print(f"   Token usage: {metrics.get('total_tokens', 0)}")
        print()
        
        # Get agent communications log
        print("Agent Communications Summary:")
        communications = client.agent_swarm.get_agent_communications(swarm_id=swarm_id)
        print(f"   Total messages exchanged: {len(communications)}")
        if communications:
            recent = communications[:3]
            for comm in recent:
                print(f"   - {comm['from_agent']} → {comm['to_agent']}: {comm['type']}")
        print()
        
        # Get swarm history
        print("Execution History:")
        history = client.agent_swarm.get_swarm_history(swarm_id=swarm_id, limit=5)
        for entry in history:
            print(f"   {entry['timestamp']}: {entry['event']} - {entry['description']}")
        print()
        
        # Pause and resume demonstration
        print("Testing swarm control...")
        client.agent_swarm.pause_swarm(swarm_id=swarm_id)
        print("   ⏸️  Swarm paused")
        time.sleep(2)
        client.agent_swarm.resume_swarm(swarm_id=swarm_id)
        print("   ▶️  Swarm resumed")
        print()
        
        # Final orchestration task
        print("🎯 Final Task: Compile final deliverables")
        final_result = client.agent_swarm.orchestrate(
            swarm_id=swarm_id,
            task="Compile all outputs into a final deliverable package",
            context={
                "components": [
                    "Research findings",
                    "System design",
                    "Implementation code",
                    "Test suite",
                    "Documentation"
                ]
            }
        )
        print("   ✅ Final package compiled\n")
        
        # Stop the swarm
        print("Stopping swarm...")
        stop_result = client.agent_swarm.stop_swarm(swarm_id=swarm_id)
        print(f"   ✅ Swarm stopped: {stop_result['status']}\n")
        
        # Create a custom agent template for future use
        print("Creating custom agent template...")
        custom_agent = client.agent_swarm.create_agent(
            name="API Security Specialist",
            agent_type=AgentType.REVIEWER,
            capabilities=[
                "api_security",
                "penetration_testing",
                "vulnerability_assessment",
                "compliance_checking"
            ],
            prompt="You are an API security specialist focused on identifying and mitigating security risks in REST APIs",
            config={
                "temperature": 0.3,
                "specialized_knowledge": ["OWASP", "OAuth2", "JWT", "API Gateway Security"]
            }
        )
        print(f"   ✅ Custom agent template created: {custom_agent['id']}\n")
        
        print("✨ Agent Swarm example completed successfully!")
        print("\nSummary:")
        print("- Orchestrated 5 specialized agents")
        print("- Completed 6 complex tasks")
        print("- Demonstrated swarm control (pause/resume)")
        print("- Created custom agent template")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()