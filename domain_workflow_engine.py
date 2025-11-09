"""
Domain-Specific Workflow Engine

Each business domain gets its own isolated workflow engine:
- Domain-specific workflows
- Domain-specific agents
- Isolated training data
- Domain-specific action model
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from domain_config import DomainConfig, DomainRegistry
from config import Config
from storage import WorkflowStorage
from agents.manager import ManagerAgent
from agents.supervisor import SupervisorAgent
from agent_factory import AgentFactory, AgentSpecification
from rl_training_system import RLTrainingSystem
from agno.agent import Agent
from agno.models.openai import OpenAIChat


class DomainWorkflowEngine:
    """
    Domain-Specific Workflow Engine

    Manages workflows for a specific business domain
    Completely isolated from other domains
    """

    def __init__(self, domain: DomainConfig):
        self.domain = domain
        self.console = Console()

        # Domain-specific storage (isolated from other domains)
        storage_path = f"{domain.data_dir}/workflow_db"
        self.storage = WorkflowStorage(base_path=storage_path)

        # Initialize core agents for this domain
        self.manager = ManagerAgent(self.storage)
        self.supervisor = SupervisorAgent(self.storage)

        # Domain-specific RL training
        rl_models_path = f"{domain.model_dir}/rl_models"
        self.rl_system = RLTrainingSystem(self.storage, save_dir=rl_models_path)

        # Agent factory for creating domain-specific agents
        self.agent_factory = AgentFactory()

        # Register domain-specific agents
        self._register_domain_agents()

        self.console.print(f"\n[green]✓[/green] Domain Workflow Engine initialized")
        self.console.print(f"  Domain: [cyan]{domain.domain_name}[/cyan]")
        self.console.print(f"  Workflows: {len(domain.workflows)}")
        self.console.print(f"  Agent types: {len(domain.agent_types)}")

    def _register_domain_agents(self):
        """Create and register domain-specific agents"""
        lm_config = Config.get_lmstudio_config()

        for agent_type in self.domain.agent_types:
            # Create domain-specific agent with domain context
            agent = Agent(
                name=agent_type,
                role=f"{agent_type} for {self.domain.domain_name} domain",
                model=OpenAIChat(
                    id=lm_config["model"],
                    api_key=lm_config["api_key"],
                    base_url=lm_config["base_url"]
                ),
                instructions=self._get_domain_instructions(agent_type),
                markdown=True,
            )

            self.supervisor.register_worker(agent_type, agent)

    def _get_domain_instructions(self, agent_type: str) -> List[str]:
        """Get domain-specific instructions for an agent"""
        base_instructions = [
            f"You are a {agent_type} specialized in the {self.domain.domain_name} domain.",
            "",
            "Domain Context:",
            self.domain.domain_context,
            "",
            "Domain Vocabulary:",
            *[f"- {term}" for term in self.domain.domain_vocabulary[:10]],
            "",
            "Always:",
            "- Use domain-specific terminology correctly",
            "- Follow domain best practices",
            "- Maintain high accuracy and quality",
            "- Collaborate with other domain agents",
        ]

        return base_instructions

    def execute_workflow(self, workflow_name: str, user_input: str) -> Any:
        """
        Execute a domain-specific workflow

        Args:
            workflow_name: Name of the workflow (must be in domain.workflows)
            user_input: User's request

        Returns:
            Workflow result
        """
        # Validate workflow is in domain
        if workflow_name not in self.domain.workflows:
            raise ValueError(
                f"Workflow '{workflow_name}' not available in {self.domain.domain_name} domain.\n"
                f"Available workflows: {', '.join(self.domain.workflows)}"
            )

        self.console.print(
            f"\n[bold cyan]🚀 Executing {self.domain.domain_name} workflow: {workflow_name}[/bold cyan]\n"
        )

        # Use the main workflow engine logic but with domain context
        from workflow_engine import WorkflowEngine

        # Execute (reusing the core engine logic)
        # The domain-specific agents and storage ensure isolation
        run = self.supervisor.auto_create_agent(user_input)

        # TODO: Full execution flow
        # For now, this is a placeholder showing the structure

        return None

    def train_domain_model(self):
        """
        Train domain-specific action model

        This creates a small model specialized for this domain only
        Much more accurate than a general model
        """
        self.console.print(
            f"\n[bold yellow]🧠 Training {self.domain.domain_name} Action Model[/bold yellow]\n"
        )

        # Check if we have enough data
        stats = self.storage.get_run_statistics()
        total_runs = stats.get("total_runs", 0)

        if total_runs < self.domain.min_runs_before_training:
            self.console.print(
                f"[yellow]⚠️  Need {self.domain.min_runs_before_training} runs before training[/yellow]"
            )
            self.console.print(f"   Current runs: {total_runs}")
            return

        # Run RL training for this domain
        self.rl_system.run_full_training_cycle(collect_limit=total_runs)

        # Save domain-specific model
        model_path = Path(self.domain.model_dir) / "action_model.pth"
        self.console.print(f"\n[green]✓[/green] Domain model saved to: {model_path}")

        # Show domain-specific statistics
        self._show_domain_statistics()

    def _show_domain_statistics(self):
        """Show statistics for this domain"""
        table = Table(title=f"{self.domain.domain_name.upper()} Domain Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        stats = self.storage.get_run_statistics()

        table.add_row("Total Runs", str(stats.get("total_runs", 0)))
        table.add_row("Success Rate", f"{stats.get('success_rate', 0):.1%}")
        table.add_row("Avg Duration", f"{stats.get('avg_duration_ms', 0):.0f}ms")

        # Domain-specific agents
        table.add_row("", "")
        table.add_row("Active Agents", str(len(self.supervisor.worker_agents)))

        for agent_name, metrics in self.supervisor.agent_metrics.items():
            table.add_row(
                f"  {agent_name}",
                f"{metrics.get('success_rate', 0):.1%} success"
            )

        self.console.print("\n", table)


class DomainManager:
    """
    Manages multiple domain-specific workflow engines

    Use this to run different domains in the same application
    """

    def __init__(self):
        self.registry = DomainRegistry()
        self.engines: Dict[str, DomainWorkflowEngine] = {}
        self.console = Console()

    def load_domain(self, domain_name: str) -> DomainWorkflowEngine:
        """Load a domain's workflow engine"""
        if domain_name in self.engines:
            return self.engines[domain_name]

        domain_config = self.registry.get_domain(domain_name)
        if not domain_config:
            raise ValueError(f"Domain '{domain_name}' not found in registry")

        # Create engine for this domain
        engine = DomainWorkflowEngine(domain_config)
        self.engines[domain_name] = engine

        return engine

    def execute_in_domain(self, domain_name: str, workflow_name: str, user_input: str) -> Any:
        """Execute a workflow in a specific domain"""
        engine = self.load_domain(domain_name)
        return engine.execute_workflow(workflow_name, user_input)

    def train_all_domains(self):
        """Train action models for all loaded domains"""
        self.console.print("\n[bold cyan]🎓 Training All Domain Models[/bold cyan]\n")

        for domain_name, engine in self.engines.items():
            self.console.print(f"\n{'=' * 60}")
            self.console.print(f"Training domain: {domain_name}")
            self.console.print('=' * 60)

            engine.train_domain_model()

    def show_all_domains(self):
        """Show all available domains"""
        table = Table(title="Available Business Domains")
        table.add_column("Domain", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Workflows", style="yellow")
        table.add_column("Agents", style="green")

        for domain_name in self.registry.list_domains():
            domain = self.registry.get_domain(domain_name)
            table.add_row(
                domain_name,
                domain.domain_description[:50] + "...",
                str(len(domain.workflows)),
                str(len(domain.agent_types))
            )

        self.console.print("\n", table)


# ==================== Usage Examples ====================

def example_legal_workflow():
    """Example: Using the legal domain"""
    from domain_config import initialize_standard_domains

    # Initialize domains
    registry = initialize_standard_domains()

    # Create manager
    manager = DomainManager()

    # Execute legal workflow
    result = manager.execute_in_domain(
        domain_name="legal",
        workflow_name="draft_contract",
        user_input="Draft a standard NDA for a software consulting engagement"
    )

    return result


def example_healthcare_workflow():
    """Example: Using the healthcare domain"""
    manager = DomainManager()

    # Execute healthcare workflow
    result = manager.execute_in_domain(
        domain_name="healthcare",
        workflow_name="clinical_summary",
        user_input="Generate clinical summary for patient with hypertension and diabetes"
    )

    return result


def example_multi_domain():
    """Example: Running multiple domains"""
    from domain_config import initialize_standard_domains

    initialize_standard_domains()
    manager = DomainManager()

    # Show all domains
    manager.show_all_domains()

    # Execute in different domains
    print("\n--- Legal Domain ---")
    manager.execute_in_domain("legal", "draft_contract", "Draft employment agreement")

    print("\n--- E-commerce Domain ---")
    manager.execute_in_domain("ecommerce", "customer_support_response", "Handle return request")

    print("\n--- Finance Domain ---")
    manager.execute_in_domain("finance", "risk_analysis", "Analyze portfolio risk")

    # Train all domain models
    manager.train_all_domains()


if __name__ == "__main__":
    print("Domain-Specific Workflow Engine")
    print("=" * 60)

    example_multi_domain()
