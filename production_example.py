"""
Production Workflow Example
Demonstrates the complete self-evolving agentic system
"""

from workflow_engine import WorkflowEngine
from config import Config
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import sys


def main():
    """Run the production workflow example"""
    console = Console()

    # Print welcome banner
    console.print(Panel.fit(
        "[bold cyan]🤖 Agentic Workflow System[/bold cyan]\n"
        "Self-Evolving Multi-Agent System\n\n"
        "[dim]Manager → Supervisor → Worker Agents[/dim]\n"
        "[dim]with RL Training & Evolutionary Selection[/dim]",
        border_style="cyan"
    ))

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"\n[red]❌ Configuration Error:[/red] {e}")
        console.print("\nPlease create a .env file based on .env.example")
        sys.exit(1)

    # Initialize the workflow engine
    console.print("\n[cyan]Initializing Workflow Engine...[/cyan]\n")
    engine = WorkflowEngine()

    # Main loop
    while True:
        console.print("\n" + "=" * 60)
        console.print("[bold]What would you like to do?[/bold]\n")
        console.print("1. Execute a workflow")
        console.print("2. View system statistics")
        console.print("3. Trigger system evolution")
        console.print("4. Run example workflows")
        console.print("5. Exit")
        console.print("=" * 60)

        choice = Prompt.ask("\nYour choice", choices=["1", "2", "3", "4", "5"])

        if choice == "1":
            execute_custom_workflow(engine, console)

        elif choice == "2":
            engine.print_statistics()

        elif choice == "3":
            trigger_evolution(engine, console)

        elif choice == "4":
            run_examples(engine, console)

        elif choice == "5":
            console.print("\n[cyan]👋 Goodbye![/cyan]\n")
            break


def execute_custom_workflow(engine: WorkflowEngine, console: Console):
    """Execute a custom workflow"""
    console.print("\n[bold cyan]Execute Custom Workflow[/bold cyan]\n")

    # Get user input
    user_request = Prompt.ask("What would you like the agents to do?")

    # Choose workflow type
    console.print("\n[bold]Available workflow types:[/bold]")
    console.print("1. content_creation - Research, write, and review content")
    console.print("2. data_analysis - Analyze data and provide insights")
    console.print("3. general - General-purpose workflow")

    workflow_choice = Prompt.ask("Choose workflow type", choices=["1", "2", "3"], default="3")

    workflow_types = {
        "1": "content_creation",
        "2": "data_analysis",
        "3": "general"
    }
    workflow_type = workflow_types[workflow_choice]

    # Execute
    run = engine.execute(user_request, workflow_type)

    # Ask for feedback
    console.print("\n[bold]How was the result?[/bold]")
    feedback = Prompt.ask("Your feedback (or press Enter to skip)", default="")

    if feedback:
        engine.manager.collect_feedback(run, feedback)
        console.print("[green]✓ Feedback recorded for RL training[/green]")


def trigger_evolution(engine: WorkflowEngine, console: Console):
    """Trigger system evolution"""
    console.print("\n[bold yellow]⚠️  System Evolution[/bold yellow]")
    console.print("This will evaluate all agents and may:")
    console.print("- Kill underperforming agents")
    console.print("- Modify existing agents")
    console.print("- Create new agents\n")

    if Confirm.ask("Proceed with evolution?", default=False):
        engine.evolve_system()
    else:
        console.print("[dim]Evolution cancelled[/dim]")


def run_examples(engine: WorkflowEngine, console: Console):
    """Run example workflows"""
    console.print("\n[bold cyan]Example Workflows[/bold cyan]\n")

    examples = [
        {
            "name": "Content Creation",
            "request": "Create a blog post about the benefits of multi-agent AI systems for businesses",
            "workflow": "content_creation"
        },
        {
            "name": "Data Analysis",
            "request": "Analyze the key factors that make agentic workflows successful",
            "workflow": "data_analysis"
        },
        {
            "name": "General Task",
            "request": "Explain how evolutionary algorithms can improve AI agent performance",
            "workflow": "general"
        }
    ]

    for i, example in enumerate(examples, 1):
        console.print(f"{i}. {example['name']}")
        console.print(f"   [dim]{example['request']}[/dim]")

    choice = Prompt.ask("\nChoose an example", choices=["1", "2", "3"])
    example = examples[int(choice) - 1]

    console.print(f"\n[cyan]Running: {example['name']}[/cyan]")

    run = engine.execute(example['request'], example['workflow'])

    # Simulate positive feedback for examples
    engine.manager.collect_feedback(run, "Great result! Very helpful.")


def run_batch_demo(engine: WorkflowEngine, console: Console):
    """
    Run multiple workflows to demonstrate evolution

    This shows how the system:
    1. Executes multiple workflows
    2. Collects metrics
    3. Identifies patterns
    4. Evolves agents based on performance
    """
    console.print("\n[bold cyan]🚀 Batch Demo - Evolution in Action[/bold cyan]\n")
    console.print("Running multiple workflows to demonstrate evolution...\n")

    tasks = [
        ("Create a technical blog post about AI agents", "content_creation"),
        ("Analyze successful patterns in agent collaboration", "data_analysis"),
        ("Write a product description for an AI workflow tool", "content_creation"),
        ("Research best practices for multi-agent systems", "general"),
        ("Create a comparison of different agent architectures", "content_creation"),
    ]

    for i, (task, workflow_type) in enumerate(tasks, 1):
        console.print(f"\n[cyan]Task {i}/{len(tasks)}:[/cyan] {task}")
        run = engine.execute(task, workflow_type)

        # Simulate varied feedback
        feedbacks = [
            "Excellent work!",
            "Good, but could be better",
            "Very thorough and helpful",
            "Missing some key points",
            "Perfect!"
        ]
        engine.manager.collect_feedback(run, feedbacks[i % len(feedbacks)])

    console.print("\n[green]✓ Batch execution complete[/green]")

    # Show statistics
    engine.print_statistics()

    # Trigger evolution
    if Confirm.ask("\nTrigger evolution based on these runs?", default=True):
        engine.evolve_system()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n\n[cyan]👋 Goodbye![/cyan]\n")
        sys.exit(0)
    except Exception as e:
        console = Console()
        console.print(f"\n[red]❌ Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
