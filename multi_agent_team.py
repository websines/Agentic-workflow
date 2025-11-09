"""
Multi-Agent Team Example with LMStudio
Demonstrates multiple specialized agents working together
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from config import Config


def create_lmstudio_model():
    """Helper to create LMStudio model instance"""
    lm_config = Config.get_lmstudio_config()
    return OpenAIChat(
        id=lm_config["model"],
        api_key=lm_config["api_key"],
        base_url=lm_config["base_url"]
    )


def create_research_agent():
    """Create a research specialist agent"""
    return Agent(
        name="Research Agent",
        role="Research and gather information on topics",
        model=create_lmstudio_model(),
        instructions=[
            "You are a research specialist.",
            "Provide detailed, well-researched information.",
            "Always cite your reasoning process.",
            "Break down complex topics into understandable parts.",
        ],
        markdown=True,
    )


def create_writer_agent():
    """Create a writing specialist agent"""
    return Agent(
        name="Writer Agent",
        role="Create well-written content and documentation",
        model=create_lmstudio_model(),
        instructions=[
            "You are a professional writer.",
            "Create clear, engaging, and well-structured content.",
            "Use proper formatting and organization.",
            "Adapt your writing style to the audience.",
        ],
        markdown=True,
    )


def create_critic_agent():
    """Create a critic/reviewer agent"""
    return Agent(
        name="Critic Agent",
        role="Review and provide constructive feedback",
        model=create_lmstudio_model(),
        instructions=[
            "You are a constructive critic.",
            "Review content for accuracy, clarity, and completeness.",
            "Provide specific, actionable feedback.",
            "Highlight both strengths and areas for improvement.",
        ],
        markdown=True,
    )


def create_agent_team():
    """Create a team of agents with a leader"""

    # Validate configuration
    Config.validate()

    # Create specialized agents
    research_agent = create_research_agent()
    writer_agent = create_writer_agent()
    critic_agent = create_critic_agent()

    # Create team leader that coordinates the agents
    team_leader = Agent(
        name="Team Leader",
        team=[research_agent, writer_agent, critic_agent],
        model=create_lmstudio_model(),
        instructions=[
            "You coordinate a team of specialized agents.",
            "Delegate tasks to the appropriate team member.",
            "Research Agent: for gathering information and research",
            "Writer Agent: for creating content and documentation",
            "Critic Agent: for reviewing and providing feedback",
            "Synthesize the team's outputs into a coherent response.",
        ],
        markdown=True,
    )

    return team_leader


def main():
    """Run the multi-agent team example"""
    print("=" * 60)
    print("Multi-Agent Team Example with LMStudio")
    print("=" * 60)
    print()

    # Create the agent team
    team = create_agent_team()

    print("\n🤖 Agent Team: Ready! We have a Research Agent, Writer Agent, and Critic Agent.\n")

    # Example task that requires multiple agents
    task = """
    Create a brief explanation of 'multi-agent systems' suitable for a technical blog post.
    Make sure it's well-researched, well-written, and reviewed for quality.
    """

    print(f"👤 User: {task}\n")
    print("🔄 Team is collaborating...\n")

    team.print_response(task, stream=True)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
