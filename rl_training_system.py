"""
Complete RL Training System
Orchestrates all RL training components and runs training loops
"""

from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
import json
from pathlib import Path

from rl_trainer import (
    RewardCalculator,
    ExperienceBuffer,
    PolicyOptimizer,
    PromptEvolver,
    Experience
)
from storage import WorkflowStorage
from models import RunStatus


class RLTrainingSystem:
    """
    Complete RL Training System

    Coordinates all RL components:
    - Experience collection from runs
    - Reward calculation
    - Policy optimization
    - Prompt evolution
    - Agent creation/modification
    """

    def __init__(self, storage: WorkflowStorage, save_dir: str = "./workflow_db/rl_models"):
        self.storage = storage
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.console = Console()

        # Initialize RL components
        self.reward_calculator = RewardCalculator()
        self.policy_optimizer = PolicyOptimizer(storage)
        self.prompt_evolver = PromptEvolver()

        # Load existing policy if available
        self.policy_optimizer.load_policy(str(self.save_dir / "policy.json"))

        self.console.print("[green]✓[/green] RL Training System initialized")

    def collect_experiences_from_recent_runs(self, limit: int = 100):
        """
        Collect experiences from recent runs

        This is called periodically to gather new training data
        """
        self.console.print(f"\n[cyan]Collecting experiences from recent runs...[/cyan]")

        runs = self.storage.list_runs(limit=limit)

        total_experiences = 0

        for run in runs:
            # Get feedback if available
            feedbacks = self.storage.load_feedback(run.run_id)
            feedback = feedbacks[0] if feedbacks else None

            # Extract experiences
            experiences = self.policy_optimizer.extract_experiences_from_run(run, feedback)

            # Add to buffer
            for exp in experiences:
                self.policy_optimizer.experience_buffer.add(exp)

            total_experiences += len(experiences)

        self.console.print(f"[green]✓[/green] Collected {total_experiences} experiences from {len(runs)} runs")
        self.console.print(f"  Buffer size: {self.policy_optimizer.experience_buffer.size()}")

        return total_experiences

    def train_supervisor_policy(self, batch_size: int = 32, iterations: int = 50):
        """
        Train the Supervisor's decision-making policy

        This learns:
        - Which agents to assign to which tasks
        - Optimal workflow structures
        - Agent collaboration patterns
        """
        self.console.print(f"\n[bold cyan]🧠 Training Supervisor Policy[/bold cyan]\n")

        if self.policy_optimizer.experience_buffer.size() < batch_size:
            self.console.print("[yellow]⚠️  Not enough experiences yet. Need more runs.[/yellow]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console
        ) as progress:

            task = progress.add_task("[cyan]Training policy...", total=iterations)

            self.policy_optimizer.train_from_experiences(batch_size, iterations)

            progress.update(task, advance=iterations)

        # Save learned policy
        self.policy_optimizer.save_policy(str(self.save_dir / "policy.json"))

        self.console.print("[green]✓[/green] Supervisor policy training complete")

        # Show learned patterns
        self._display_learned_patterns()

    def _display_learned_patterns(self):
        """Display what the system has learned"""
        table = Table(title="Learned Patterns")
        table.add_column("Workflow Type", style="cyan")
        table.add_column("Step", style="yellow")
        table.add_column("Best Agent", style="green")
        table.add_column("Avg Reward", style="magenta")

        for workflow_type, patterns in self.policy_optimizer.learned_patterns.items():
            # Group by step
            by_step: Dict[int, List[Dict]] = {}
            for p in patterns:
                step = p["step"]
                if step not in by_step:
                    by_step[step] = []
                by_step[step].append(p)

            # Show best for each step
            for step, step_patterns in sorted(by_step.items()):
                if step_patterns:
                    best = max(step_patterns, key=lambda x: x["reward"])
                    table.add_row(
                        workflow_type,
                        str(step),
                        best["agent"],
                        f"{best['reward']:.2f}"
                    )

        self.console.print("\n", table)

    def evolve_agent_prompts(self, agent_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Evolve agent prompts based on performance

        Returns: Dict of agent_name -> new_instructions
        """
        self.console.print(f"\n[bold yellow]🧬 Evolving Agent Prompts[/bold yellow]\n")

        evolved_prompts = {}

        for agent_name, metrics in agent_metrics.items():
            self.console.print(f"\n[cyan]Analyzing {agent_name}...[/cyan]")

            # Track current version
            current_version = metrics.get("version", 1)
            current_instructions = metrics.get("instructions", [])

            if not current_instructions:
                continue

            # Evolve based on performance
            new_instructions = self.prompt_evolver.evolve_prompt(
                agent_name,
                current_instructions,
                metrics
            )

            # Track this version
            self.prompt_evolver.track_version(
                agent_name,
                current_version,
                current_instructions,
                metrics
            )

            if new_instructions != current_instructions:
                evolved_prompts[agent_name] = new_instructions
                self.console.print(f"  [green]✓[/green] Evolved {agent_name} to v{current_version + 1}")
                self.console.print(f"    Added {len(new_instructions) - len(current_instructions)} new instructions")
            else:
                self.console.print(f"  [dim]No changes needed (performance is good)[/dim]")

        return evolved_prompts

    def run_full_training_cycle(self, collect_limit: int = 100):
        """
        Run a complete training cycle

        1. Collect experiences from recent runs
        2. Train Supervisor policy
        3. Evolve agent prompts
        4. Generate recommendations
        """
        self.console.print(Panel.fit(
            "[bold cyan]🎓 Starting Full RL Training Cycle[/bold cyan]\n\n"
            "This will:\n"
            "1. Collect experiences from recent runs\n"
            "2. Train Supervisor's decision-making\n"
            "3. Evolve agent prompts\n"
            "4. Generate improvement recommendations",
            border_style="cyan"
        ))

        # 1. Collect experiences
        total_exp = self.collect_experiences_from_recent_runs(limit=collect_limit)

        if total_exp == 0:
            self.console.print("[yellow]⚠️  No experiences collected. Run some workflows first![/yellow]")
            return

        # 2. Train policy
        self.train_supervisor_policy()

        # 3. Get agent metrics from storage
        stats = self.storage.get_run_statistics()

        # 4. Generate report
        self._generate_training_report(total_exp)

        self.console.print("\n[bold green]✅ Training cycle complete![/bold green]\n")

    def _generate_training_report(self, num_experiences: int):
        """Generate a training report"""
        table = Table(title="Training Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Experiences Collected", str(num_experiences))
        table.add_row("Total Experiences in Buffer", str(self.policy_optimizer.experience_buffer.size()))
        table.add_row("Successful Experiences", str(len(self.policy_optimizer.experience_buffer.successful_buffer)))
        table.add_row("Failed Experiences", str(len(self.policy_optimizer.experience_buffer.failed_buffer)))
        table.add_row("Workflow Types Learned", str(len(self.policy_optimizer.learned_patterns)))

        self.console.print("\n", table)

    def get_policy_recommendations(self, task_type: str, task_description: str) -> List[Dict[str, Any]]:
        """
        Get RL-based recommendations for a task

        Returns list of recommended agent assignments
        """
        recommendations = []

        for step in range(5):  # Max 5 steps
            agent = self.policy_optimizer.get_recommended_agent(
                task_type,
                task_description,
                step
            )

            if agent:
                recommendations.append({
                    "step": step,
                    "recommended_agent": agent,
                    "confidence": "high"  # TODO: Add confidence scoring
                })

        return recommendations

    def analyze_performance_trends(self) -> Dict[str, Any]:
        """
        Analyze performance trends over time

        Useful for seeing if the system is improving
        """
        runs = self.storage.list_runs(limit=1000)

        if not runs:
            return {}

        # Group by time periods
        from collections import defaultdict
        from datetime import datetime, timedelta

        by_period = defaultdict(list)

        for run in runs:
            timestamp = datetime.fromisoformat(run.timestamp)
            period = timestamp.strftime("%Y-%m-%d")  # Daily
            by_period[period].append(run)

        # Calculate metrics per period
        trends = {}
        for period, period_runs in sorted(by_period.items()):
            completed = len([r for r in period_runs if r.status == RunStatus.COMPLETED])
            total = len(period_runs)

            trends[period] = {
                "total_runs": total,
                "success_rate": completed / total if total > 0 else 0,
                "avg_duration": sum(r.duration_ms or 0 for r in period_runs) / total if total > 0 else 0
            }

        return trends

    def print_performance_trends(self):
        """Print performance trends over time"""
        trends = self.analyze_performance_trends()

        if not trends:
            self.console.print("[yellow]No trend data available yet[/yellow]")
            return

        table = Table(title="Performance Trends Over Time")
        table.add_column("Date", style="cyan")
        table.add_column("Runs", style="yellow")
        table.add_column("Success Rate", style="green")
        table.add_column("Avg Duration (ms)", style="magenta")

        for date, metrics in sorted(trends.items()):
            table.add_row(
                date,
                str(metrics["total_runs"]),
                f"{metrics['success_rate']:.1%}",
                f"{metrics['avg_duration']:.0f}"
            )

        self.console.print("\n", table)

        # Show improvement
        dates = sorted(trends.keys())
        if len(dates) >= 2:
            first = trends[dates[0]]
            last = trends[dates[-1]]

            improvement = last["success_rate"] - first["success_rate"]
            if improvement > 0:
                self.console.print(f"\n[bold green]📈 Success rate improved by {improvement:.1%}![/bold green]")
            elif improvement < 0:
                self.console.print(f"\n[bold yellow]📉 Success rate decreased by {abs(improvement):.1%}[/bold yellow]")
            else:
                self.console.print(f"\n[bold]➡️  Success rate stable[/bold]")


def create_training_example():
    """Example of how to use the RL training system"""
    from storage import WorkflowStorage

    storage = WorkflowStorage()
    rl_system = RLTrainingSystem(storage)

    # Run a full training cycle
    rl_system.run_full_training_cycle(collect_limit=100)

    # Get recommendations for a new task
    recommendations = rl_system.get_policy_recommendations(
        "content_creation",
        "Create a blog post about AI agents"
    )

    print("\nRecommendations for new task:")
    print(json.dumps(recommendations, indent=2))

    # Show performance trends
    rl_system.print_performance_trends()


if __name__ == "__main__":
    create_training_example()
