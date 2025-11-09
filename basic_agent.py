"""
Basic Agent Example with LMStudio
Demonstrates a simple agent using your local LMStudio endpoint
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from config import Config

def create_basic_agent():
    """Create a basic agent using LMStudio endpoint"""

    # Validate configuration
    Config.validate()

    # Get LMStudio configuration
    lm_config = Config.get_lmstudio_config()

    # Create agent with LMStudio as the model provider
    agent = Agent(
        name="Assistant",
        model=OpenAIChat(
            id=lm_config["model"],
            api_key=lm_config["api_key"],
            base_url=lm_config["base_url"]
        ),
        instructions=[
            "You are a helpful AI assistant.",
            "Provide clear and concise responses.",
            "If you're unsure, admit it honestly.",
        ],
        markdown=True,
        show_tool_calls=True,
    )

    return agent


def main():
    """Run the basic agent example"""
    print("=" * 60)
    print("Basic Agent Example with LMStudio")
    print("=" * 60)
    print()

    # Create the agent
    agent = create_basic_agent()

    # Example conversation
    print("\n🤖 Agent: Ready! Ask me anything.\n")

    # Example queries
    queries = [
        "Hello! What can you help me with?",
        "Explain what an agentic workflow is in 2 sentences.",
    ]

    for query in queries:
        print(f"👤 User: {query}\n")
        agent.print_response(query, stream=True)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()
