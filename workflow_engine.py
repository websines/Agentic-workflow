"""
Workflow Execution Engine
Orchestrates the entire agentic system with evolution
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from config import Config
from storage import WorkflowStorage
from models import Run, Workflow, RunStatus
from agents.manager import ManagerAgent
from agents.supervisor import SupervisorAgent


class WorkflowEngine:
    """
    Main Workflow Execution Engine

    Coordinates Manager, Supervisor, and Worker agents
    Handles evolution and self-improvement
    """

    def __init__(self):
        self.console = Console()
        self.storage = WorkflowStorage()

        # Initialize core agents
        self.manager = ManagerAgent(self.storage)
        self.supervisor = SupervisorAgent(self.storage)

        # Register default worker agents
        self._register_default_workers()

        self.console.print("\n[green]✓[/green] Workflow Engine initialized")
        self._print_system_status()

    def _register_default_workers(self):
        """Register default worker agents"""
        lm_config = Config.get_lmstudio_config()

        # Research Agent
        research_agent = Agent(
            name="Research Agent",
            role="Gather and analyze information",
            model=OpenAIChat(
                id=lm_config["model"],
                api_key=lm_config["api_key"],
                base_url=lm_config["base_url"]
            ),
            instructions=[
                "You are a research specialist.",
                "Gather comprehensive information on topics.",
                "Provide well-organized, detailed research.",
                "Always cite your reasoning process.",
            ],
            markdown=True,
        )
        self.supervisor.register_worker("Research Agent", research_agent)

        # Writer Agent
        writer_agent = Agent(
            name="Writer Agent",
            role="Create well-written content",
            model=OpenAIChat(
                id=lm_config["model"],
                api_key=lm_config["api_key"],
                base_url=lm_config["base_url"]
            ),
            instructions=[
                "You are a professional writer.",
                "Create clear, engaging, well-structured content.",
                "Adapt your style to the audience and purpose.",
                "Focus on clarity and impact.",
            ],
            markdown=True,
        )
        self.supervisor.register_worker("Writer Agent", writer_agent)

        # Analyst Agent
        analyst_agent = Agent(
            name="Analyst Agent",
            role="Analyze data and provide insights",
            model=OpenAIChat(
                id=lm_config["model"],
                api_key=lm_config["api_key"],
                base_url=lm_config["base_url"]
            ),
            instructions=[
                "You are a data analyst.",
                "Analyze information critically and find patterns.",
                "Provide actionable insights.",
                "Support conclusions with evidence.",
            ],
            markdown=True,
        )
        self.supervisor.register_worker("Analyst Agent", analyst_agent)

    def _print_system_status(self):
        """Print current system status"""
        table = Table(title="System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        table.add_row("Manager Agent", "✓ Active")
        table.add_row("Supervisor Agent", "✓ Active")

        for agent_name in self.supervisor.worker_agents.keys():
            metrics = self.supervisor.agent_metrics.get(agent_name, {})
            version = metrics.get("version", 1)
            success_rate = metrics.get("success_rate", 1.0)
            table.add_row(f"  {agent_name}", f"✓ Active (v{version}, {success_rate:.1%} success)")

        self.console.print(table)

    def execute(self, user_input: str, workflow_type: str = "content_creation") -> Run:
        """
        Execute a complete workflow

        Args:
            user_input: User's request
            workflow_type: Type of workflow to execute

        Returns:
            Completed Run object
        """
        self.console.print(f"\n[bold cyan]🚀 Starting Workflow: {workflow_type}[/bold cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:

            # Phase 1: Manager analyzes request
            task1 = progress.add_task("[cyan]Manager analyzing request...", total=None)
            run = self.manager.handle_request(user_input, workflow_type)
            progress.update(task1, description="[green]✓ Manager analysis complete")

            # Phase 2: Load or create workflow
            task2 = progress.add_task("[cyan]Loading workflow template...", total=None)
            workflow = self._get_or_create_workflow(workflow_type)
            progress.update(task2, description="[green]✓ Workflow loaded")

            # Phase 3: Supervisor executes workflow
            task3 = progress.add_task("[cyan]Supervisor orchestrating team...", total=None)
            run = self.supervisor.execute_workflow(run, workflow)
            progress.update(task3, description="[green]✓ Workflow execution complete")

            # Phase 4: Manager presents result
            task4 = progress.add_task("[cyan]Manager preparing result...", total=None)
            presentation = self.manager.present_result(run)
            progress.update(task4, description="[green]✓ Result ready")

        # Print result
        self.console.print(Panel(
            presentation,
            title="[bold green]Result[/bold green]",
            border_style="green"
        ))

        # Print run statistics
        self._print_run_stats(run)

        return run

    def _get_or_create_workflow(self, workflow_type: str) -> Workflow:
        """Get existing workflow or create a new one"""
        workflow = self.storage.load_workflow(workflow_type)

        if workflow:
            return workflow

        # Create default workflows
        if workflow_type == "content_creation":
            workflow = Workflow(
                name="content_creation",
                description="Create high-quality content",
                steps_template=[
                    {"agent": "Research Agent", "task": "Research the topic thoroughly"},
                    {"agent": "Writer Agent", "task": "Write engaging content based on research"},
                    {"agent": "Analyst Agent", "task": "Review and suggest improvements"},
                ],
                required_agents=["Research Agent", "Writer Agent", "Analyst Agent"]
            )

        elif workflow_type == "data_analysis":
            workflow = Workflow(
                name="data_analysis",
                description="Analyze data and provide insights",
                steps_template=[
                    {"agent": "Research Agent", "task": "Gather relevant data and context"},
                    {"agent": "Analyst Agent", "task": "Analyze the data and find patterns"},
                    {"agent": "Writer Agent", "task": "Create a clear report of findings"},
                ],
                required_agents=["Research Agent", "Analyst Agent", "Writer Agent"]
            )

        else:
            # General workflow
            workflow = Workflow(
                name=workflow_type,
                description=f"General workflow for {workflow_type}",
                steps_template=[
                    {"agent": "Research Agent", "task": "Understand the request"},
                    {"agent": "Analyst Agent", "task": "Determine best approach"},
                    {"agent": "Writer Agent", "task": "Create the final output"},
                ],
                required_agents=["Research Agent", "Analyst Agent", "Writer Agent"]
            )

        # Save for future use
        self.storage.save_workflow(workflow)

        return workflow

    def _print_run_stats(self, run: Run):
        """Print statistics about the run"""
        table = Table(title="Run Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Run ID", run.run_id)
        table.add_row("Status", run.status.value)
        table.add_row("Total Steps", str(len(run.steps)))

        if run.duration_ms:
            table.add_row("Duration", f"{run.duration_ms:.2f}ms")

        # Agent breakdown
        agent_steps = {}
        for step in run.steps:
            agent_steps[step.agent_name] = agent_steps.get(step.agent_name, 0) + 1

        table.add_row("", "")
        table.add_row("Agent Breakdown", "")
        for agent, count in agent_steps.items():
            table.add_row(f"  {agent}", str(count))

        self.console.print("\n", table)

    def evolve_system(self):
        """
        Trigger system evolution
        Evaluate agents and apply evolutionary pressure
        """
        self.console.print("\n[bold yellow]🧬 Starting System Evolution[/bold yellow]\n")

        # Get recommendations from Supervisor
        recommendations = self.supervisor.evaluate_agents()

        self.console.print("[cyan]Evolution Recommendations:[/cyan]")
        self.console.print(recommendations)

        # Apply evolution
        for agent_info in recommendations.get("kill", []):
            agent_name = agent_info.get("agent")
            reason = agent_info.get("reason")
            self.console.print(f"\n[red]🪦 Terminating {agent_name}:[/red] {reason}")
            self.supervisor.kill_agent(agent_name)

        for agent_info in recommendations.get("modify", []):
            agent_name = agent_info.get("agent")
            suggestion = agent_info.get("suggestion")
            self.console.print(f"\n[yellow]🧬 Evolving {agent_name}:[/yellow] {suggestion}")
            self.supervisor.evolve_agent(agent_name, suggestion)

        for new_agent_info in recommendations.get("create", []):
            name = new_agent_info.get("name")
            role = new_agent_info.get("role")
            self.console.print(f"\n[green]✨ Creating new agent {name}:[/green] {role}")
            # Placeholder - would need actual agent creation logic

        self.console.print("\n[green]✓ Evolution complete[/green]")
        self._print_system_status()

    def get_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        stats = self.storage.get_run_statistics()

        return {
            "runs": stats,
            "agents": self.supervisor.agent_metrics,
            "workflows": self.storage.list_workflows(),
        }

    def print_statistics(self):
        """Print system statistics"""
        stats = self.get_statistics()

        self.console.print("\n[bold cyan]📊 System Statistics[/bold cyan]\n")

        # Run statistics
        run_table = Table(title="Run Statistics")
        run_table.add_column("Metric", style="cyan")
        run_table.add_column("Value", style="yellow")

        run_stats = stats["runs"]
        run_table.add_row("Total Runs", str(run_stats.get("total_runs", 0)))
        run_table.add_row("Completed", str(run_stats.get("completed", 0)))
        run_table.add_row("Failed", str(run_stats.get("failed", 0)))
        run_table.add_row("Success Rate", f"{run_stats.get('success_rate', 0):.1%}")

        if run_stats.get("avg_duration_ms"):
            run_table.add_row("Avg Duration", f"{run_stats['avg_duration_ms']:.2f}ms")

        self.console.print(run_table)

        # Agent metrics
        agent_table = Table(title="\nAgent Performance")
        agent_table.add_column("Agent", style="cyan")
        agent_table.add_column("Success Rate", style="green")
        agent_table.add_column("Tasks", style="yellow")
        agent_table.add_column("Version", style="magenta")

        for agent_name, metrics in stats["agents"].items():
            agent_table.add_row(
                agent_name,
                f"{metrics.get('success_rate', 0):.1%}",
                str(metrics.get('tasks_completed', 0)),
                f"v{metrics.get('version', 1)}"
            )

        self.console.print("\n", agent_table)
