"""
Simple Demo - Direct agent test
Shows the multi-agent system without full workflow complexity
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from rich.console import Console
import ssl
import httpx

console = Console()

def main():
    console.print("\n[bold cyan]🤖 Simple Multi-Agent Demo[/bold cyan]\n")

    try:
        # Create HTTP client that skips SSL verification (for self-signed certs)
        http_client = httpx.Client(verify=False)

        # Create a simple agent
        console.print("[yellow]Creating agent...[/yellow]")

        agent = Agent(
            name="Demo Agent",
            role="Helpful AI assistant",
            model=OpenAIChat(
                id="qwen3-moe",
                api_key="lm-studio",
                base_url="https://lmstudio.subh-dev.xyz/v1",
                http_client=http_client  # Skip SSL verification
            ),
            instructions=[
                "You are a helpful AI assistant.",
                "Provide clear, concise responses.",
                "Be professional and friendly.",
            ],
            markdown=True,
        )

        console.print("[green]✓ Agent created successfully![/green]\n")

        # Test query
        query = "Create a brief 3-point outline for a blog post about multi-agent AI systems"

        console.print(f"[cyan]Query:[/cyan] {query}\n")
        console.print("[yellow]Agent thinking...[/yellow]\n")

        # Run the agent
        response = agent.run(query)

        # Display result
        console.print("[bold green]✅ Agent Response:[/bold green]\n")
        console.print(f"[white]{response.content}[/white]\n")

        console.print("\n[green]🎉 Demo complete![/green]")
        console.print("\n[dim]This demonstrates:")
        console.print("  ✓ Connection to your LMStudio endpoint")
        console.print("  ✓ Agno agent framework")
        console.print("  ✓ Basic agent execution")
        console.print("\nNext: Run full multi-agent workflow with Manager, Supervisor, and team![/dim]\n")

    except Exception as e:
        console.print(f"\n[red]❌ Error:[/red] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
