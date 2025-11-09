# Agentic Workflow - Production System

> **Self-Evolving Multi-Agent System with RL Training & Evolutionary Selection**

A production-grade agentic workflow system designed for businesses, featuring autonomous evolution, comprehensive logging, and continuous improvement through reinforcement learning.

## 🌟 System Overview

This is a **self-evolving agentic ecosystem** that:

- Executes curated business workflows through coordinated multi-agent teams
- Logs every run, tool call, and decision to a git-style database
- Uses reinforcement learning to continuously improve agent performance
- Employs evolutionary selection to kill underperforming agents and promote successful ones
- Maintains dual-memory architecture (short-term + long-term with Helix-DB)
- Eventually trains small action models from distilled agent behaviors

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Manager Agent                               │
│              (User-Facing Interface)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 Supervisor Agent                             │
│         (Orchestration & Evolution)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐     ┌──────────┐    ┌──────────┐
    │ Research │     │  Writer  │    │  Analyst │
    │  Agent   │     │  Agent   │    │  Agent   │
    └──────────┘     └──────────┘    └──────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Git-Style Logging Database                      │
│         + Helix-DB (Graph + Vector)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              RL Training Pipeline                            │
│         (Agent Evolution & Optimization)                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔑 Key Features

### 1. Manager Agent (User-Facing)
- Natural language understanding of business requests
- Workflow selection and creation
- Result presentation
- Feedback collection for RL

### 2. Supervisor Agent (Orchestration & Evolution)
- Task decomposition and agent assignment
- Progress monitoring and error recovery
- Performance tracking and agent evaluation
- Evolutionary selection (kill/modify/create agents)
- Self-optimization

### 3. Specialized Worker Agents
- **Research Agent**: Information gathering and analysis
- **Writer Agent**: Content creation and documentation
- **Analyst Agent**: Data analysis and insights
- **Extensible**: Add custom agents as needed

### 4. Git-Style Logging Database
Every aspect of execution is logged:
- **Runs** (like git commits): Complete workflow executions
- **Steps** (like operations): Individual agent actions
- **Tool Calls**: Detailed tool usage logs
- **Feedback**: User feedback for RL training
- **Agent Versions**: Full version history for evolution tracking

### 5. Dual-Memory Architecture

**Short-Term Memory:**
- Current conversation context
- Active workflow state
- Recent decisions and tool calls
- In-memory or Redis-backed

**Long-Term Memory (Helix-DB):**
- **Graph Component**: Relationships between agents, workflows, runs
  - "Which agents work well together?"
  - "What workflows succeed for X type of task?"
  - "How have agents evolved over time?"

- **Vector Component**: Semantic search over past runs
  - Find similar situations
  - Learn from past successes
  - Avoid repeated mistakes

### 6. Evolutionary Selection

The system evolves like natural selection:

1. **Performance Tracking**: Every agent's success rate, speed, quality
2. **Evaluation Cycles**: Periodic evaluation of all agents
3. **Selection Pressure**:
   - **Kill**: Remove consistently underperforming agents
   - **Modify**: Evolve agents with potential
   - **Create**: Spawn new agents when needed
4. **Version Control**: All agent versions saved for analysis
5. **Continuous Improvement**: System gets better over time

### 7. RL Training Pipeline

```
Workflow Execution → Log Everything → Collect Feedback
        ↓                                    ↑
   Store in DB ← Extract Patterns ← Analyze Performance
        ↓
Update Agent Behaviors ← Identify Improvements
        ↓
A/B Test Changes
        ↓
Deploy Best Performers → Next Iteration
```

## 📦 Project Structure

```
Agentic-workflow/
├── agents/
│   ├── __init__.py
│   ├── manager.py              # Manager Agent (user-facing)
│   └── supervisor.py           # Supervisor Agent (orchestration)
│
├── workflow_db/                # Git-style database
│   ├── runs/                   # Workflow run logs
│   ├── steps/                  # Step-by-step execution logs
│   ├── feedback/               # User feedback for RL
│   ├── workflows/              # Workflow templates
│   ├── agents/                 # Agent version history
│   └── models/                 # Trained action models
│
├── config.py                   # Configuration management
├── models.py                   # Data models (Run, Step, Feedback, etc.)
├── storage.py                  # Git-style storage layer
├── memory.py                   # Dual-memory system
├── helix_integration.py        # Helix-DB integration
├── workflow_engine.py          # Main orchestration engine
├── production_example.py       # Production workflow demo
│
├── basic_agent.py              # Simple agent example
├── multi_agent_team.py         # Multi-agent collaboration example
├── agent_with_tools.py         # Agent with custom tools
├── main.py                     # Interactive menu
│
├── architecture.md             # Detailed architecture docs
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # Basic README
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo>
cd Agentic-workflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your LMStudio endpoint
```

### Configuration

Edit `.env`:

```env
# LMStudio Configuration
LMSTUDIO_BASE_URL=https://lmstudio.subh-dev.xyz/v1
LMSTUDIO_API_KEY=lm-studio
LMSTUDIO_MODEL=local-model
```

### Run Production System

```bash
python production_example.py
```

This will:
1. Initialize the workflow engine
2. Register all agents
3. Show an interactive menu
4. Execute workflows with full logging
5. Collect feedback for RL
6. Trigger evolution when ready

## 💼 Business Workflows

### Content Creation Workflow

```
User: "Create a blog post about AI agents"
  ↓
Manager: Analyzes request, selects content_creation workflow
  ↓
Supervisor: Plans execution
  1. Research Agent → Gather information about AI agents
  2. Writer Agent → Draft blog post
  3. Analyst Agent → Review and improve
  ↓
Manager: Presents polished blog post
  ↓
System: Logs entire process for RL training
```

### Data Analysis Workflow

```
User: "Analyze Q4 sales trends"
  ↓
Manager: Selects data_analysis workflow
  ↓
Supervisor: Orchestrates
  1. Research Agent → Load and understand data
  2. Analyst Agent → Perform trend analysis
  3. Writer Agent → Create report
  ↓
Manager: Presents insights and visualizations
  ↓
System: Records patterns for future optimization
```

## 🧬 Evolution in Action

### Evaluation Metrics

Each agent is continuously evaluated on:
- **Success Rate**: % of tasks completed successfully
- **Average Duration**: Speed of execution
- **Quality Score**: Based on user feedback
- **Collaboration Score**: Success when working with other agents

### Evolution Trigger

```python
from workflow_engine import WorkflowEngine

engine = WorkflowEngine()

# Run multiple workflows...
# Collect metrics and feedback...

# Trigger evolution
engine.evolve_system()
```

This will:
1. Analyze all agent performance
2. Recommend actions:
   - **Keep**: High performers
   - **Modify**: Agents with potential
   - **Kill**: Consistent underperformers
   - **Create**: Fill gaps in capabilities
3. Apply evolutionary pressure
4. Update the ecosystem

### Example Evolution Cycle

```
Iteration 1:
- Research Agent v1: 85% success
- Writer Agent v1: 92% success
- Analyst Agent v1: 65% success  ← Low performer

Evaluation:
- Keep: Research v1, Writer v1
- Kill: Analyst v1 (< 70% threshold)
- Create: Analyst v2 with improved instructions

Iteration 2:
- Research Agent v1: 85% success
- Writer Agent v1: 92% success
- Analyst Agent v2: 88% success  ← Improved!

System evolved successfully! ✨
```

## 📊 Monitoring & Analytics

### View Statistics

```python
engine.print_statistics()
```

Shows:
- Total runs (completed/failed)
- Success rates by workflow type
- Agent performance metrics
- System-wide trends

### Query Historical Data

```python
from storage import WorkflowStorage

storage = WorkflowStorage()

# Get all runs
runs = storage.list_runs(limit=100)

# Get specific run
run = storage.load_run(run_id)

# Get feedback
feedback = storage.load_feedback(run_id)

# Get agent evolution history
versions = storage.get_agent_versions("Research Agent")
```

### Helix-DB Queries

```python
from helix_integration import HelixConnection, HelixMemoryAdapter

helix = HelixConnection()
helix.connect()

adapter = HelixMemoryAdapter(helix)

# Find best agent for a task
best_agent = adapter.find_best_agent_for_task(
    task_type="content_creation",
    context={"topic": "AI", "audience": "technical"}
)

# Discover agent synergies
synergies = adapter.discover_agent_synergies()
# Returns: [("Research", "Writer", 0.92), ...]

# Optimize workflow
optimizations = adapter.optimize_workflow("content_creation")
```

## 🎯 Use Cases

### 1. Content Creation Pipeline
- Blog posts, articles, documentation
- Research → Write → Review → Publish
- Self-optimizing based on engagement

### 2. Data Analysis & Reporting
- Business intelligence
- Trend analysis
- Automated report generation

### 3. Customer Support Automation
- Query understanding
- Solution research
- Response generation
- Quality assurance

### 4. Code Analysis & Review
- Code understanding
- Bug detection
- Improvement suggestions
- Documentation generation

### 5. Custom Business Workflows
- Define your own workflows
- System learns and optimizes
- Continuous improvement

## 🔧 Extending the System

### Add a New Agent

```python
from agno.agent import Agent
from config import Config

lm_config = Config.get_lmstudio_config()

custom_agent = Agent(
    name="Custom Agent",
    role="Your specialized role",
    model=OpenAIChat(
        id=lm_config["model"],
        api_key=lm_config["api_key"],
        base_url=lm_config["base_url"]
    ),
    instructions=[
        "Your custom instructions",
        "Define specific behaviors",
    ],
    markdown=True,
)

# Register with Supervisor
engine.supervisor.register_worker("Custom Agent", custom_agent)
```

### Create a New Workflow

```python
from models import Workflow

workflow = Workflow(
    name="custom_workflow",
    description="Your custom workflow",
    steps_template=[
        {"agent": "Research Agent", "task": "Step 1"},
        {"agent": "Custom Agent", "task": "Step 2"},
        {"agent": "Writer Agent", "task": "Step 3"},
    ],
    required_agents=["Research Agent", "Custom Agent", "Writer Agent"]
)

engine.storage.save_workflow(workflow)
```

### Add Custom Tools

```python
from agno.tools import tool

@tool
def custom_tool(input: str) -> str:
    """Your custom tool description"""
    # Tool logic here
    return result

# Add to agent
agent = Agent(
    name="Tool Agent",
    model=...,
    tools=[custom_tool],
)
```

## 🔮 Future Enhancements

### Phase 1: Core System ✅
- Manager, Supervisor, Worker agents
- Git-style logging
- Basic evolution

### Phase 2: Advanced Memory (In Progress)
- Helix-DB integration
- Semantic search
- Graph analytics

### Phase 3: RL Pipeline
- Pattern extraction
- Agent behavior optimization
- A/B testing framework
- Automated evolution

### Phase 4: Action Model Training
- Collect large-scale data
- Train small action models
- Distill agent behaviors
- Edge deployment

### Phase 5: Self-Modification
- Workflows that modify themselves
- Agents that rewrite their instructions
- Fully autonomous evolution

## 🤝 Contributing

This is a production system for businesses. Contributions welcome:

- New workflow templates
- Additional agents
- Tool integrations
- Performance optimizations
- Documentation improvements

## 📚 Resources

- [Agno Framework](https://github.com/agno-agi/agno)
- [LMStudio](https://lmstudio.ai/)
- [Architecture Documentation](architecture.md)

## 🙋 Support

For issues or questions:
1. Check `architecture.md` for system design
2. Review example workflows
3. Examine logs in `workflow_db/`
4. Open an issue with details

## 📄 License

MIT License - Use for your business needs!

---

**Built with ❤️ for Businesses**

*Self-evolving. Continuously learning. Always improving.*
