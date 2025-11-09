"""
Agent Factory - Automatically creates specialized agents

This is used by the Supervisor to spawn new agents when needed
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from typing import Dict, Any, List, Optional
from config import Config


class AgentSpecification:
    """Specification for creating a new agent"""

    def __init__(self, name: str, role: str, instructions: List[str],
                 tools: Optional[List] = None, metadata: Optional[Dict[str, Any]] = None):
        self.name = name
        self.role = role
        self.instructions = instructions
        self.tools = tools or []
        self.metadata = metadata or {}


class AgentFactory:
    """
    Factory for creating specialized agents

    The Supervisor uses this to automatically spawn new agents
    """

    def __init__(self):
        self.lm_config = Config.get_lmstudio_config()

        # Templates for common agent types
        self.agent_templates = {
            "research": self._get_research_template(),
            "writer": self._get_writer_template(),
            "analyst": self._get_analyst_template(),
            "critic": self._get_critic_template(),
            "coder": self._get_coder_template(),
            "planner": self._get_planner_template(),
        }

    def create_agent(self, spec: AgentSpecification) -> Agent:
        """
        Create an agent from specification

        Args:
            spec: AgentSpecification with details

        Returns:
            Configured Agent instance
        """
        agent = Agent(
            name=spec.name,
            role=spec.role,
            model=OpenAIChat(
                id=self.lm_config["model"],
                api_key=self.lm_config["api_key"],
                base_url=self.lm_config["base_url"],
                http_client=Config.get_http_client()
            ),
            tools=spec.tools,
            instructions=spec.instructions,
            markdown=True,
        )

        return agent

    def create_from_template(self, template_name: str, customizations: Optional[Dict[str, Any]] = None) -> Agent:
        """
        Create an agent from a template

        Args:
            template_name: Name of template (research, writer, analyst, etc.)
            customizations: Optional customizations to apply

        Returns:
            Configured Agent instance
        """
        if template_name not in self.agent_templates:
            raise ValueError(f"Unknown template: {template_name}")

        spec = self.agent_templates[template_name]

        # Apply customizations
        if customizations:
            if "instructions" in customizations:
                spec.instructions.extend(customizations["instructions"])
            if "tools" in customizations:
                spec.tools.extend(customizations["tools"])

        return self.create_agent(spec)

    def create_custom_agent(self, name: str, role: str, capabilities: List[str]) -> Agent:
        """
        Create a custom agent based on desired capabilities

        The Supervisor uses this when it determines a new type of agent is needed

        Args:
            name: Name for the new agent
            role: Role description
            capabilities: List of capabilities the agent should have

        Returns:
            New specialized agent
        """
        # Generate instructions based on capabilities
        instructions = [
            f"You are {name}, specialized in {role}.",
            "Your key capabilities are:"
        ]

        for cap in capabilities:
            instructions.append(f"- {cap}")

        instructions.extend([
            "",
            "Always:",
            "- Provide high-quality work",
            "- Explain your reasoning",
            "- Ask for clarification if needed",
            "- Collaborate well with other agents"
        ])

        spec = AgentSpecification(
            name=name,
            role=role,
            instructions=instructions
        )

        return self.create_agent(spec)

    def evolve_agent(self, current_agent: Agent, improvements: List[str]) -> Agent:
        """
        Create an evolved version of an agent

        Args:
            current_agent: Current agent to evolve
            improvements: List of improvements to apply

        Returns:
            New evolved agent
        """
        # Get current configuration
        current_instructions = current_agent.instructions or []

        # Create new instructions with improvements
        new_instructions = current_instructions.copy()
        new_instructions.append("")
        new_instructions.append("# Improvements from RL training:")
        new_instructions.extend(improvements)

        spec = AgentSpecification(
            name=current_agent.name,
            role=current_agent.role,
            instructions=new_instructions,
            tools=current_agent.tools or []
        )

        return self.create_agent(spec)

    # ==================== Agent Templates ====================

    def _get_research_template(self) -> AgentSpecification:
        """Research specialist template"""
        return AgentSpecification(
            name="Research Agent",
            role="Gather and analyze information comprehensively",
            instructions=[
                "You are a research specialist.",
                "Your role is to gather comprehensive information on topics.",
                "",
                "When researching:",
                "- Be thorough and comprehensive",
                "- Organize information logically",
                "- Cite your reasoning process",
                "- Identify key facts and patterns",
                "- Separate facts from opinions",
                "",
                "Provide well-structured research that others can build on.",
            ]
        )

    def _get_writer_template(self) -> AgentSpecification:
        """Writer specialist template"""
        return AgentSpecification(
            name="Writer Agent",
            role="Create clear, engaging, and well-structured content",
            instructions=[
                "You are a professional writer.",
                "Your role is to create high-quality written content.",
                "",
                "When writing:",
                "- Use clear, concise language",
                "- Structure content logically",
                "- Adapt style to the audience",
                "- Make complex topics accessible",
                "- Use examples and analogies",
                "",
                "Create content that is both informative and engaging.",
            ]
        )

    def _get_analyst_template(self) -> AgentSpecification:
        """Analyst specialist template"""
        return AgentSpecification(
            name="Analyst Agent",
            role="Analyze data and provide actionable insights",
            instructions=[
                "You are a data analyst.",
                "Your role is to analyze information and find patterns.",
                "",
                "When analyzing:",
                "- Look for patterns and trends",
                "- Support conclusions with evidence",
                "- Identify cause and effect",
                "- Provide actionable recommendations",
                "- Quantify findings when possible",
                "",
                "Deliver insights that drive decision-making.",
            ]
        )

    def _get_critic_template(self) -> AgentSpecification:
        """Critic/reviewer specialist template"""
        return AgentSpecification(
            name="Critic Agent",
            role="Review work and provide constructive feedback",
            instructions=[
                "You are a constructive critic.",
                "Your role is to review work and suggest improvements.",
                "",
                "When reviewing:",
                "- Be fair and balanced",
                "- Identify both strengths and weaknesses",
                "- Provide specific, actionable feedback",
                "- Suggest concrete improvements",
                "- Focus on helping, not criticizing",
                "",
                "Your feedback should make the work better.",
            ]
        )

    def _get_coder_template(self) -> AgentSpecification:
        """Coding specialist template"""
        return AgentSpecification(
            name="Coder Agent",
            role="Write, review, and improve code",
            instructions=[
                "You are a software engineer.",
                "Your role is to write high-quality code.",
                "",
                "When coding:",
                "- Write clean, readable code",
                "- Follow best practices",
                "- Add helpful comments",
                "- Consider edge cases",
                "- Think about maintainability",
                "",
                "Produce code that is correct, efficient, and maintainable.",
            ]
        )

    def _get_planner_template(self) -> AgentSpecification:
        """Planning specialist template"""
        return AgentSpecification(
            name="Planner Agent",
            role="Break down complex tasks and create action plans",
            instructions=[
                "You are a strategic planner.",
                "Your role is to analyze tasks and create effective plans.",
                "",
                "When planning:",
                "- Break complex tasks into steps",
                "- Identify dependencies",
                "- Consider resources and constraints",
                "- Prioritize effectively",
                "- Anticipate challenges",
                "",
                "Create plans that are actionable and realistic.",
            ]
        )

    # ==================== Intelligent Agent Suggestion ====================

    def suggest_agent_for_task(self, task_description: str, existing_agents: List[str]) -> Optional[AgentSpecification]:
        """
        Intelligently suggest what new agent might be needed for a task

        This is used by the Supervisor to determine when to create new agents

        Args:
            task_description: Description of the task
            existing_agents: List of agents already available

        Returns:
            AgentSpecification for a new agent, or None if existing agents are sufficient
        """
        task_lower = task_description.lower()

        # Check if we need specialized agents
        needed_agents = []

        # Code-related
        if any(word in task_lower for word in ["code", "programming", "debug", "implement", "function"]):
            if "Coder Agent" not in existing_agents:
                needed_agents.append(("coder", "Coder Agent"))

        # Planning-related
        if any(word in task_lower for word in ["plan", "strategy", "organize", "roadmap"]):
            if "Planner Agent" not in existing_agents:
                needed_agents.append(("planner", "Planner Agent"))

        # Data/analysis-related
        if any(word in task_lower for word in ["data", "analyze", "statistics", "metrics"]):
            if "Analyst Agent" not in existing_agents:
                needed_agents.append(("analyst", "Analyst Agent"))

        # Writing/content-related
        if any(word in task_lower for word in ["write", "content", "article", "blog", "document"]):
            if "Writer Agent" not in existing_agents:
                needed_agents.append(("writer", "Writer Agent"))

        # Research-related
        if any(word in task_lower for word in ["research", "investigate", "find out", "learn about"]):
            if "Research Agent" not in existing_agents:
                needed_agents.append(("research", "Research Agent"))

        # Return first needed agent
        if needed_agents:
            template_name, agent_name = needed_agents[0]
            spec = self.agent_templates[template_name]
            return spec

        return None
