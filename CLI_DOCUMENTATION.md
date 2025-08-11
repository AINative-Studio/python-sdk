# AINative Python SDK - CLI Documentation

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Install the SDK & CLI

```bash
# Navigate to SDK directory
cd /Volumes/Cody/projects/AINative/developer-tools/sdks/python

# Install in development mode (recommended)
pip install --break-system-packages -e .

# Or install from local package
pip install --break-system-packages .
```

### Verify Installation
```bash
ainative --version
ainative --help
```

---

## ⚙️ Initial Configuration

Before using the CLI, configure your API credentials:

```bash
# Set your API key (required)
ainative config set api_key YOUR_API_KEY

# Set base URL (optional - defaults to production)
ainative config set base_url https://api.ainative.studio

# View current configuration
ainative config show
```

---

## 📋 Complete CLI Commands Reference

### **Global Options**
```bash
ainative [OPTIONS] COMMAND [ARGS]...

Global Options:
  --version      Show the version and exit
  -v, --verbose  Enable verbose output
  --help         Show this message and exit
```

---

### **1. Configuration Management**

#### `ainative config`
Manage CLI configuration settings.

```bash
# Set configuration values
ainative config set api_key YOUR_API_KEY
ainative config set api_secret YOUR_SECRET  # Optional for enhanced security
ainative config set base_url https://api.ainative.studio
ainative config set organization_id ORG_ID  # For multi-tenant scenarios

# View current configuration
ainative config show
```

**Available config keys:**
- `api_key` - Your AINative API key (required)
- `api_secret` - API secret for enhanced security (optional)
- `base_url` - API base URL (default: https://api.ainative.studio)
- `organization_id` - Organization ID for multi-tenant usage

---

### **2. Health Check**

#### `ainative health`
Check API connectivity and health status.

```bash
# Basic health check
ainative health

# Verbose health check with detailed output
ainative -v health
```

---

### **3. Project Management**

#### `ainative projects`
Manage ZeroDB projects for data organization.

```bash
# List all projects
ainative projects list

# Create a new project
ainative projects create "My Project" "Project description"
ainative projects create "Vector Search App" "AI-powered search application"

# Get detailed project information
ainative projects get PROJECT_ID

# Suspend a project (temporarily disable)
ainative projects suspend PROJECT_ID

# Activate a suspended project
ainative projects activate PROJECT_ID

# Delete a project (permanent - use with caution)
ainative projects delete PROJECT_ID
```

**Examples:**
```bash
# Create a project for a chatbot
ainative projects create "Customer Support Bot" "AI chatbot for customer service"

# List all projects to see the new one
ainative projects list

# Get details for a specific project
ainative projects get proj_12345
```

---

### **4. Vector Operations**

#### `ainative vectors`
Manage vector data for semantic search and AI operations.

```bash
# Search vectors by text query
ainative vectors search --query "machine learning algorithms" --top-k 5
ainative vectors search --query "customer support" --top-k 10 --project-id PROJECT_ID

# Upsert vectors from JSON file
ainative vectors upsert vectors_data.json --project-id PROJECT_ID

# Get vector index statistics
ainative vectors stats --project-id PROJECT_ID
```

**JSON file format for upsert:**
```json
{
  "vectors": [
    {
      "id": "doc_1",
      "vector": [0.1, 0.2, 0.3, ...],
      "metadata": {
        "title": "Document Title",
        "category": "documentation"
      }
    }
  ]
}
```

**Examples:**
```bash
# Search for AI-related content
ainative vectors search --query "artificial intelligence trends" --top-k 3

# Upload vectors from a file
ainative vectors upsert my_embeddings.json --project-id proj_12345

# Check vector database statistics
ainative vectors stats --project-id proj_12345
```

---

### **5. Memory Operations**

#### `ainative memory`
Manage memory entries for AI context and knowledge storage.

```bash
# List all memory entries
ainative memory list
ainative memory list --project-id PROJECT_ID

# Create a new memory entry
ainative memory create --content "Important customer feedback about feature X"
ainative memory create --content "Meeting notes from Q4 planning" --tags "meeting,planning,q4"
ainative memory create --content "Bug report: login issue" --tags "bug,login" --priority high

# Search memory entries
ainative memory search --query "customer feedback"
ainative memory search --query "bug reports" --project-id PROJECT_ID
```

**Priority levels:** `low`, `medium`, `high`, `urgent`

**Examples:**
```bash
# Create high-priority memory
ainative memory create --content "Critical security update needed" --tags "security,urgent" --priority urgent

# Search for planning-related memories
ainative memory search --query "quarterly planning"

# List all memories with verbose output
ainative -v memory list
```

---

### **6. Agent Swarm Operations**

#### `ainative swarm`
Orchestrate and manage AI agent swarms for complex task automation.

```bash
# Start an agent swarm from configuration file
ainative swarm start agents_config.json --project-id PROJECT_ID

# Orchestrate a task within an active swarm
ainative swarm orchestrate --task "Analyze customer feedback and generate report" --swarm-id SWARM_ID

# Get swarm status and metrics
ainative swarm status --swarm-id SWARM_ID

# List available agent types
ainative swarm agent-types

# Stop a running swarm
ainative swarm stop --swarm-id SWARM_ID
```

**Agent configuration file format:**
```json
{
  "agents": [
    {
      "type": "data_analyst",
      "config": {
        "specialization": "customer_data",
        "max_concurrent_tasks": 3
      }
    },
    {
      "type": "report_generator",
      "config": {
        "format": "markdown",
        "include_charts": true
      }
    }
  ],
  "orchestration": {
    "max_agents": 5,
    "coordination_model": "hierarchical"
  }
}
```

**Examples:**
```bash
# Start a swarm for data analysis
ainative swarm start data_analysis_agents.json --project-id proj_12345

# Orchestrate a complex task
ainative swarm orchestrate --task "Process customer survey data and create insights report" --swarm-id swarm_abc123

# Check what agent types are available
ainative swarm agent-types

# Monitor swarm performance
ainative swarm status --swarm-id swarm_abc123
```

---

### **7. Analytics & Metrics**

#### `ainative analytics`
Access usage analytics, cost tracking, and performance metrics.

```bash
# Get usage analytics
ainative analytics usage --project-id PROJECT_ID
ainative analytics usage --project-id PROJECT_ID --days 30

# Get cost analysis
ainative analytics costs --project-id PROJECT_ID
ainative analytics costs --project-id PROJECT_ID --days 7

# Get trend data for specific metrics
ainative analytics trends --metric "api_requests" --days 30
ainative analytics trends --metric "vector_searches" --days 7 --project-id PROJECT_ID
```

**Available metrics for trends:**
- `api_requests` - Total API requests
- `vector_searches` - Vector search operations
- `memory_operations` - Memory read/write operations
- `agent_tasks` - Agent task executions
- `storage_usage` - Storage utilization
- `compute_time` - Compute resource usage

**Examples:**
```bash
# Check last 30 days usage
ainative analytics usage --project-id proj_12345 --days 30

# Get cost breakdown for current month
ainative analytics costs --project-id proj_12345 --days 30

# View API request trends
ainative analytics trends --metric "api_requests" --days 14
```

---

## 🔧 Advanced Usage

### **Verbose Mode**
Add `-v` or `--verbose` to any command for detailed output:

```bash
ainative -v projects list
ainative -v vectors search --query "example"
ainative -v swarm status --swarm-id SWARM_ID
```

### **Environment Variables**
Set configuration via environment variables:

```bash
export AINATIVE_API_KEY="your_api_key"
export AINATIVE_BASE_URL="https://api.ainative.studio"
export AINATIVE_ORG_ID="your_org_id"
```

### **JSON Output**
Many commands support JSON output for scripting:

```bash
ainative projects list --format json
ainative analytics usage --project-id PROJECT_ID --format json
```

---

## 🚨 Troubleshooting

### **Common Issues**

1. **Command not found:**
   ```bash
   # Reinstall the package
   pip install --break-system-packages -e /path/to/sdk
   ```

2. **Authentication errors:**
   ```bash
   # Check your API key configuration
   ainative config show
   
   # Reset API key
   ainative config set api_key YOUR_NEW_KEY
   ```

3. **Connection errors:**
   ```bash
   # Test connectivity
   ainative health
   
   # Check base URL
   ainative config show
   ```

### **Debug Mode**
Use verbose flag for debugging:

```bash
ainative -v health
ainative -v projects list
```

---

## 📚 Quick Reference

### **Essential Commands**
```bash
# Setup
ainative config set api_key YOUR_KEY
ainative health

# Projects
ainative projects list
ainative projects create "Name" "Description"

# Vectors
ainative vectors search --query "search term" --top-k 5

# Memory
ainative memory create --content "Important note"
ainative memory search --query "search term"

# Analytics
ainative analytics usage --project-id PROJECT_ID
```

### **File Formats**

**Vectors JSON:**
```json
{
  "vectors": [
    {
      "id": "unique_id",
      "vector": [0.1, 0.2, 0.3],
      "metadata": {"key": "value"}
    }
  ]
}
```

**Agents JSON:**
```json
{
  "agents": [
    {
      "type": "agent_type",
      "config": {"setting": "value"}
    }
  ]
}
```

---

## 🔗 Next Steps

1. **Set up your first project:**
   ```bash
   ainative projects create "My First Project" "Learning the AINative CLI"
   ```

2. **Upload some vectors:**
   ```bash
   ainative vectors upsert my_data.json --project-id YOUR_PROJECT_ID
   ```

3. **Start exploring:**
   ```bash
   ainative vectors search --query "your search term" --top-k 3
   ```

For more information, visit the [AINative Documentation](https://docs.ainative.studio) or use `ainative COMMAND --help` for command-specific help.