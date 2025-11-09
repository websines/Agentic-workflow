"""
Agent with Custom Tools Example
Demonstrates how to create custom tools for agents
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from config import Config
import json


# Define custom tools
@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")

    Returns:
        The result of the calculation
    """
    try:
        # Safe evaluation - only allow basic math operations
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic math operations are allowed"

        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
def get_system_info() -> str:
    """
    Get basic system information.

    Returns:
        System information in JSON format
    """
    import platform
    import sys

    info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": sys.version,
        "architecture": platform.machine(),
    }

    return json.dumps(info, indent=2)


@tool
def count_words(text: str) -> str:
    """
    Count words, characters, and lines in text.

    Args:
        text: The text to analyze

    Returns:
        Statistics about the text
    """
    lines = text.split('\n')
    words = text.split()
    chars = len(text)

    stats = {
        "lines": len(lines),
        "words": len(words),
        "characters": chars,
        "characters_no_spaces": len(text.replace(' ', '')),
    }

    return json.dumps(stats, indent=2)


def create_tool_agent():
    """Create an agent with custom tools"""

    # Validate configuration
    Config.validate()

    # Get LMStudio configuration
    lm_config = Config.get_lmstudio_config()

    # Create agent with custom tools
    agent = Agent(
        name="Tool Agent",
        model=OpenAIChat(
            id=lm_config["model"],
            api_key=lm_config["api_key"],
            base_url=lm_config["base_url"]
        ),
        tools=[calculate, get_system_info, count_words],
        instructions=[
            "You are a helpful assistant with access to tools.",
            "Use the tools when appropriate to answer user questions.",
            "Always explain what you're doing when using a tool.",
        ],
        markdown=True,
        show_tool_calls=True,
    )

    return agent


def main():
    """Run the agent with tools example"""
    print("=" * 60)
    print("Agent with Custom Tools Example")
    print("=" * 60)
    print()

    # Create the agent
    agent = create_tool_agent()

    print("\n🤖 Agent: I have access to calculation, system info, and text analysis tools!\n")

    # Example queries that use different tools
    queries = [
        "What's 15 multiplied by 7, then add 23?",
        "Count the words in this sentence: 'The quick brown fox jumps over the lazy dog'",
        "What system are you running on?",
    ]

    for query in queries:
        print(f"👤 User: {query}\n")
        agent.print_response(query, stream=True)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()
