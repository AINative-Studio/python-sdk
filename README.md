# AINative Python SDK

Official Python SDK for AINative Studio APIs - unified database and AI operations platform.

## Features

- 🚀 **Simple Integration** - Get started with just an API key
- 🗄️ **ZeroDB Operations** - Full support for vector storage, search, and memory management
- 🤖 **Agent Swarm** - Orchestrate multiple AI agents for complex tasks
- 🔐 **Enterprise Security** - Multi-tenant authentication with API key management
- ⚡ **High Performance** - Async support and connection pooling
- 📊 **Analytics** - Built-in usage tracking and performance metrics

## Installation

```bash
pip install ainative-python
```

For development version:
```bash
pip install git+https://github.com/AINative-Studio/python-sdk.git
```

## Quick Start

```python
from ainative import AINativeClient

# Initialize client
client = AINativeClient(api_key="your-api-key")

# Create a project
project = client.zerodb.projects.create(
    name="My First Project",
    description="Testing AINative SDK"
)

# Store vectors
client.zerodb.vectors.upsert(
    project_id=project["id"],
    vectors=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
    metadata=[{"text": "Hello"}, {"text": "World"}]
)

# Search vectors
results = client.zerodb.vectors.search(
    project_id=project["id"],
    vector=[0.15, 0.25, 0.35],
    top_k=5
)

# Create memory
memory = client.zerodb.memory.create(
    content="Important information to remember",
    tags=["tutorial", "example"]
)
```

## Authentication

### Using Environment Variables

```bash
export AINATIVE_API_KEY="your-api-key"
export AINATIVE_API_SECRET="your-api-secret"  # Optional
export AINATIVE_ORG_ID="your-org-id"  # For multi-tenant scenarios
```

```python
from ainative import AINativeClient

# Automatically uses environment variables
client = AINativeClient()
```

### Direct Configuration

```python
from ainative import AINativeClient, AuthConfig

auth_config = AuthConfig(
    api_key="your-api-key",
    api_secret="your-api-secret",  # Optional for enhanced security
    environment="production"  # or "staging", "development"
)

client = AINativeClient(auth_config=auth_config)
```

## ZeroDB Operations

### Project Management

```python
# List all projects
projects = client.zerodb.projects.list(limit=10)

# Get project details
project = client.zerodb.projects.get(project_id="proj_123")

# Update project
client.zerodb.projects.update(
    project_id="proj_123",
    name="Updated Name",
    metadata={"version": "2.0"}
)

# Suspend/Activate project
client.zerodb.projects.suspend(project_id="proj_123", reason="Maintenance")
client.zerodb.projects.activate(project_id="proj_123")
```

### Vector Operations

```python
import numpy as np

# Upsert vectors with numpy arrays
vectors = np.random.rand(10, 768)  # 10 vectors of dimension 768
metadata = [{"doc_id": i, "category": "test"} for i in range(10)]

client.zerodb.vectors.upsert(
    project_id="proj_123",
    vectors=vectors,
    metadata=metadata,
    namespace="documents"
)

# Search vectors
query_vector = np.random.rand(768)
results = client.zerodb.vectors.search(
    project_id="proj_123",
    vector=query_vector,
    top_k=5,
    namespace="documents",
    filter={"category": "test"}
)

# Delete vectors
client.zerodb.vectors.delete(
    project_id="proj_123",
    ids=["vec_1", "vec_2"],
    namespace="documents"
)
```

### Memory Management

```python
from ainative.zerodb.memory import MemoryPriority

# Create memory with priority
memory = client.zerodb.memory.create(
    content="Critical system configuration",
    title="System Config",
    tags=["config", "system"],
    priority=MemoryPriority.HIGH,
    metadata={"version": "1.0"}
)

# Search memories
results = client.zerodb.memory.search(
    query="system configuration",
    semantic=True,  # Use semantic search
    limit=10
)

# List memories with filters
memories = client.zerodb.memory.list(
    tags=["config"],
    priority=MemoryPriority.HIGH
)

# Get related memories
related = client.zerodb.memory.get_related(
    memory_id=memory["id"],
    limit=5
)
```

## Agent Swarm

### Starting a Swarm

```python
from ainative.agent_swarm import AgentType

# Define agents
agents = [
    {
        "id": "researcher_1",
        "type": AgentType.RESEARCHER.value,
        "capabilities": ["web_search", "document_analysis"]
    },
    {
        "id": "coder_1",
        "type": AgentType.CODER.value,
        "capabilities": ["python", "javascript", "testing"]
    }
]

# Start swarm
swarm = client.agent_swarm.start_swarm(
    project_id="proj_123",
    agents=agents,
    objective="Research and implement a new feature"
)

# Orchestrate task
result = client.agent_swarm.orchestrate(
    swarm_id=swarm["id"],
    task="Find best practices for implementing OAuth2",
    context={"language": "Python", "framework": "FastAPI"}
)
```

### Managing Swarms

```python
# Get swarm status
status = client.agent_swarm.get_status(swarm_id="swarm_123")

# Get performance metrics
metrics = client.agent_swarm.get_metrics(swarm_id="swarm_123")

# Configure specific agent
client.agent_swarm.configure_agent(
    swarm_id="swarm_123",
    agent_id="coder_1",
    config={"temperature": 0.7, "max_tokens": 2000}
)

# Pause/Resume swarm
client.agent_swarm.pause_swarm(swarm_id="swarm_123")
client.agent_swarm.resume_swarm(swarm_id="swarm_123")

# Stop swarm
client.agent_swarm.stop_swarm(swarm_id="swarm_123")
```

## Analytics

```python
from datetime import datetime, timedelta

# Get usage analytics
usage = client.zerodb.analytics.get_usage(
    project_id="proj_123",
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    granularity="daily"
)

# Get performance metrics
performance = client.zerodb.analytics.get_performance_metrics(
    project_id="proj_123",
    metric_type="latency"
)

# Get cost analysis
costs = client.zerodb.analytics.get_cost_analysis(
    project_id="proj_123"
)

# Export analytics report
report = client.zerodb.analytics.export_report(
    report_type="detailed",
    project_id="proj_123",
    format="pdf"
)
```

## Async Support

```python
import asyncio
from ainative import AsyncAINativeClient

async def main():
    async with AsyncAINativeClient(api_key="your-api-key") as client:
        # Async operations
        project = await client.zerodb.projects.create(
            name="Async Project"
        )
        
        # Concurrent operations
        tasks = [
            client.zerodb.vectors.search(project_id, vector)
            for vector in vectors
        ]
        results = await asyncio.gather(*tasks)

asyncio.run(main())
```

## Error Handling

```python
from ainative.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ResourceNotFoundError
)

try:
    result = client.zerodb.projects.get("invalid_id")
except ResourceNotFoundError as e:
    print(f"Project not found: {e.resource_id}")
except AuthenticationError:
    print("Invalid API credentials")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid input: {e.message}")
```

## Configuration

### Custom Base URL

```python
client = AINativeClient(
    api_key="your-api-key",
    base_url="https://custom.ainative.studio"
)
```

### Timeout and Retries

```python
from ainative.client import ClientConfig

config = ClientConfig(
    timeout=60,  # 60 seconds
    max_retries=5,
    retry_delay=2.0
)

client = AINativeClient(
    api_key="your-api-key",
    config=config
)
```

## CLI Tool

The SDK includes a CLI tool for quick operations:

```bash
# Configure credentials
ainative config set api_key YOUR_API_KEY

# List projects
ainative projects list

# Create project
ainative projects create --name "CLI Project"

# Search vectors
ainative vectors search --project proj_123 --query "test"
```

## Examples

Full examples are available in the [examples/](examples/) directory:

- [Basic Usage](examples/basic_usage.py)
- [Vector Search](examples/vector_search.py)
- [Memory Management](examples/memory_management.py)
- [Agent Swarm](examples/agent_swarm.py)
- [Analytics Dashboard](examples/analytics.py)
- [Multi-tenant Setup](examples/multi_tenant.py)

## Development

### Setting up development environment

```bash
# Clone repository
git clone https://github.com/AINative-Studio/python-sdk.git
cd python-sdk

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black ainative/
isort ainative/

# Type checking
mypy ainative/
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=ainative

# Specific module
pytest tests/test_zerodb.py
```

## Support

- **Documentation**: [https://docs.ainative.studio/sdk/python](https://docs.ainative.studio/sdk/python)
- **API Reference**: [https://api.ainative.studio/docs-enhanced](https://api.ainative.studio/docs-enhanced)
- **Issues**: [GitHub Issues](https://github.com/AINative-Studio/python-sdk/issues)
- **Discord**: [Join our community](https://discord.gg/ainative)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.