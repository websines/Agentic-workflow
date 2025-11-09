"""
Demo script to show the agentic workflow system in action
"""

from workflow_engine import WorkflowEngine
from rich.console import Console

console = Console()

def main():
    console.print("\n[bold cyan]🚀 Agentic Workflow System Demo[/bold cyan]\n")

    try:
        # Initialize the workflow engine
        console.print("[yellow]Initializing workflow engine...[/yellow]")
        engine = WorkflowEngine()

        # Example task: Create a blog post outline
        console.print("\n[bold green]Demo Task:[/bold green] Create a brief outline for a blog post about multi-agent AI systems\n")

        # Execute the workflow
        run = engine.execute(
            user_input="Create a brief outline for a blog post about multi-agent AI systems and how they work together",
            workflow_type="content_creation"
        )

        console.print("\n[bold green]✅ Workflow Complete![/bold green]\n")

        # Show some statistics
        console.print("[cyan]Quick Stats:[/cyan]")
        console.print(f"  Run ID: {run.run_id}")
        console.print(f"  Status: {run.status.value}")
        console.print(f"  Total Steps: {len(run.steps)}")
        console.print(f"  Agents Involved: {len(set(step.agent_name for step in run.steps))}")

    except Exception as e:
        console.print(f"\n[red]❌ Error:[/red] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
