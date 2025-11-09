# Agentic Workflow

A multi-agent system built with [Agno](https://github.com/agno-agi/agno) framework, designed to work with your local LMStudio endpoint.

## 🚀 Features

- **Basic Agent**: Simple conversational agent for general tasks
- **Multi-Agent Teams**: Collaborative agents with specialized roles (Research, Writer, Critic)
- **Custom Tools**: Agents with custom tool capabilities (calculator, system info, text analysis)
- **LMStudio Integration**: Uses your local LMStudio endpoint at `https://lmstudio.subh-dev.xyz/v1`

## 📋 Prerequisites

- Python 3.8+
- LMStudio running at `https://lmstudio.subh-dev.xyz/v1`
- pip or uv for package management

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Agentic-workflow
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your configuration:
   ```env
   LMSTUDIO_BASE_URL=https://lmstudio.subh-dev.xyz/v1
   LMSTUDIO_API_KEY=lm-studio
   LMSTUDIO_MODEL=local-model
   ```

## 🎮 Usage

### Interactive Menu

Run the main script to access all examples:

```bash
python main.py
```

This will show an interactive menu where you can choose different examples.

### Individual Examples

You can also run examples directly:

#### 1. Basic Agent
Simple conversational agent:
```bash
python basic_agent.py
```

#### 2. Multi-Agent Team
Collaborative agents working together:
```bash
python multi_agent_team.py
```

This example demonstrates:
- **Research Agent**: Gathers and analyzes information
- **Writer Agent**: Creates well-written content
- **Critic Agent**: Reviews and provides feedback
- **Team Leader**: Coordinates all agents

#### 3. Agent with Tools
Agent with custom tool capabilities:
```bash
python agent_with_tools.py
```

Available tools:
- `calculate`: Evaluate mathematical expressions
- `get_system_info`: Get system information
- `count_words`: Analyze text statistics

## 📁 Project Structure

```
Agentic-workflow/
├── main.py                  # Interactive menu to run examples
├── config.py                # Configuration management
├── basic_agent.py           # Simple agent example
├── multi_agent_team.py      # Multi-agent collaboration example
├── agent_with_tools.py      # Agent with custom tools example
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Configuration

The project uses environment variables for configuration. Key settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `LMSTUDIO_BASE_URL` | LMStudio API endpoint | `https://lmstudio.subh-dev.xyz/v1` |
| `LMSTUDIO_API_KEY` | API key for LMStudio | `lm-studio` |
| `LMSTUDIO_MODEL` | Model name to use | `local-model` |

## 💡 How It Works

### Agno Framework

Agno is a high-performance multi-agent framework that provides:

- **Fast**: 529× faster than LangGraph, 57× faster than PydanticAI
- **Model-Agnostic**: Works with any OpenAI-compatible endpoint (including LMStudio)
- **Multi-Agent**: Built-in support for agent teams and workflows
- **Tools**: Easy integration of custom tools and capabilities

### Agent Architecture

```
┌─────────────────┐
│  Team Leader    │
│   (Coordinator) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │         │
┌───▼──┐  ┌──▼───┐  ┌──▼───┐
│Research│ │Writer│ │Critic│
│ Agent  │ │Agent │ │Agent │
└────────┘ └──────┘ └──────┘
```

Each agent has:
- **Role**: Specialized function
- **Instructions**: Behavior guidelines
- **Tools**: Optional capabilities
- **Model**: LLM backend (LMStudio)

## 🎯 Use Cases

- **Content Creation**: Research → Write → Review pipeline
- **Code Analysis**: Multiple agents analyzing different aspects
- **Task Automation**: Agents handling different workflow steps
- **Decision Making**: Collaborative agent decision-making
- **Interactive Assistants**: Multi-skilled conversational agents

## 🚧 Extending the System

### Adding New Agents

Create a new agent in any example file:

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from config import Config

def create_custom_agent():
    lm_config = Config.get_lmstudio_config()

    agent = Agent(
        name="Custom Agent",
        role="Your agent's role",
        model=OpenAIChat(
            id=lm_config["model"],
            api_key=lm_config["api_key"],
            base_url=lm_config["base_url"]
        ),
        instructions=[
            "Your custom instructions",
        ],
        markdown=True,
    )

    return agent
```

### Adding Custom Tools

Define tools using the `@tool` decorator:

```python
from agno.tools import tool

@tool
def your_custom_tool(input: str) -> str:
    """
    Description of your tool.

    Args:
        input: Description of input parameter

    Returns:
        Description of return value
    """
    # Your tool logic here
    return "result"
```

Then add it to your agent:

```python
agent = Agent(
    name="Tool Agent",
    model=...,
    tools=[your_custom_tool],
)
```

## 📚 Resources

- [Agno Documentation](https://docs.agno.com/)
- [Agno GitHub](https://github.com/agno-agi/agno)
- [LMStudio](https://lmstudio.ai/)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new agent examples
- Create custom tools
- Improve documentation
- Report issues

## 📄 License

MIT License - feel free to use this project however you like!

## 🙋 Support

If you encounter issues:
1. Check your `.env` configuration
2. Verify LMStudio is running and accessible
3. Ensure all dependencies are installed
4. Check the model name matches your LMStudio setup

---

**Built with ❤️ using [Agno](https://github.com/agno-agi/agno)**
