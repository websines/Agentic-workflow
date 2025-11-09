"""
Demo: Agents Using Company Knowledge Base

Shows how agents search and use company-specific knowledge
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from knowledge_center import KnowledgeCenter, KnowledgeManager, create_knowledge_retrieval_tool
from rich.console import Console
from rich.panel import Panel
import httpx

console = Console()

def setup_company_knowledge():
    """Manager uploads company knowledge"""
    console.print("\n[bold cyan]Step 1: Manager Uploads Company Knowledge[/bold cyan]\n")

    kc = KnowledgeCenter()
    manager = KnowledgeManager(kc)

    # HR uploads policies
    console.print("[yellow]HR Manager uploading policies...[/yellow]")
    manager.upload_policy(
        title="Remote Work Policy",
        content="""
        Employees may work remotely with manager approval.

        Special provisions:
        - Sick child care: Work from home without PTO for up to 5 days/year
        - Equipment: Company provides laptop and monitor
        - Hours: Maintain 9 AM - 5 PM availability
        - Performance: Same standards as office work
        """,
        domain="hr",
        uploaded_by="HR Manager"
    )

    # Support uploads FAQs
    console.print("[yellow]Support Manager uploading FAQs...[/yellow]")
    manager.upload_faq(
        title="Return & Refund Policy",
        qa_pairs=[
            {"question": "Return window?", "answer": "30 days for full refund"},
            {"question": "Return shipping?", "answer": "Free prepaid label provided"},
            {"question": "Damaged items?", "answer": "Accepted anytime, priority processing"},
            {"question": "Exchanges?", "answer": "Processed immediately without waiting"}
        ],
        domain="customer_support",
        uploaded_by="Support Manager"
    )

    # Sales uploads processes
    console.print("[yellow]Sales VP uploading processes...[/yellow]")
    manager.upload_process(
        title="Pricing Guidelines",
        steps=[
            "Base price: $100/unit",
            "Volume discount: 100-499 units = 10% off",
            "Volume discount: 500+ units = 15% off",
            "New customer discount: Additional 5% off first order",
            "Requires approval: Discounts above 20% total"
        ],
        domain="sales",
        uploaded_by="Sales VP"
    )

    console.print("[green]✓ Knowledge uploaded![/green]\n")

    return kc


def create_smart_agent_with_knowledge(domain: str, kc: KnowledgeCenter):
    """Create an agent with access to company knowledge"""

    # Create knowledge retrieval tool
    knowledge_tool = create_knowledge_retrieval_tool(kc, domain)

    # Create HTTP client that skips SSL verification
    http_client = httpx.Client(verify=False)

    agent = Agent(
        name=f"{domain.title()} Agent",
        role=f"Specialized agent for {domain} with company knowledge access",
        model=OpenAIChat(
            id="qwen3-moe",
            api_key="lm-studio",
            base_url="https://lmstudio.subh-dev.xyz/v1",
            http_client=http_client
        ),
        tools=[knowledge_tool],  # Agent can search company knowledge!
        instructions=[
            f"You are a {domain} specialist with access to company knowledge.",
            "Always search the company knowledge base for accurate, official information.",
            "Use the search_company_knowledge tool for company policies, processes, and guidelines.",
            "Cite the knowledge base when providing answers.",
            "Be professional and helpful.",
        ],
        markdown=True,
    )

    return agent


def demo_hr_agent(kc: KnowledgeCenter):
    """Demo: HR agent answers employee question using knowledge base"""
    console.print("\n[bold cyan]Step 2: HR Agent Answers Employee Question[/bold cyan]\n")

    agent = create_smart_agent_with_knowledge("hr", kc)

    question = "Can I work from home if my child is sick? Do I need to use PTO?"

    console.print(f"[yellow]Employee Question:[/yellow] {question}\n")
    console.print("[cyan]HR Agent searching knowledge base...[/cyan]\n")

    response = agent.run(question)

    console.print(Panel(
        response.content,
        title="[bold green]HR Agent Response (Using Company Knowledge)[/bold green]",
        border_style="green"
    ))


def demo_support_agent(kc: KnowledgeCenter):
    """Demo: Support agent handles customer inquiry using knowledge base"""
    console.print("\n[bold cyan]Step 3: Support Agent Handles Customer Inquiry[/bold cyan]\n")

    agent = create_smart_agent_with_knowledge("customer_support", kc)

    question = "I received a damaged product. Can I still return it after 30 days?"

    console.print(f"[yellow]Customer Question:[/yellow] {question}\n")
    console.print("[cyan]Support Agent searching knowledge base...[/cyan]\n")

    response = agent.run(question)

    console.print(Panel(
        response.content,
        title="[bold green]Support Agent Response (Using Company Knowledge)[/bold green]",
        border_style="green"
    ))


def demo_sales_agent(kc: KnowledgeCenter):
    """Demo: Sales agent creates quote using pricing guidelines"""
    console.print("\n[bold cyan]Step 4: Sales Agent Creates Quote[/bold cyan]\n")

    agent = create_smart_agent_with_knowledge("sales", kc)

    question = "Customer wants to buy 500 units. What's the price? They're a new customer."

    console.print(f"[yellow]Sales Request:[/yellow] {question}\n")
    console.print("[cyan]Sales Agent checking pricing guidelines...[/cyan]\n")

    response = agent.run(question)

    console.print(Panel(
        response.content,
        title="[bold green]Sales Agent Quote (Using Company Knowledge)[/bold green]",
        border_style="green"
    ))


def main():
    console.print(Panel.fit(
        "[bold cyan]🎓 Company Knowledge Center Demo[/bold cyan]\n\n"
        "Demonstrates:\n"
        "1. Manager uploads company knowledge\n"
        "2. Agents search knowledge base\n"
        "3. Agents use company-specific information\n"
        "4. Consistent, accurate responses",
        border_style="cyan"
    ))

    try:
        # Setup
        kc = setup_company_knowledge()

        # Run demos
        demo_hr_agent(kc)
        demo_support_agent(kc)
        demo_sales_agent(kc)

        # Show final stats
        console.print("\n[bold cyan]Knowledge Base Stats:[/bold cyan]\n")
        stats = kc.get_statistics()
        console.print(f"  Total documents: {stats['total_documents']}")
        console.print(f"  Domains covered: {list(stats['by_domain'].keys())}")
        console.print(f"  Document types: {list(stats['by_type'].keys())}\n")

        console.print("[bold green]✅ Demo Complete![/bold green]")
        console.print("\n[dim]Key Benefits:")
        console.print("  ✓ Agents have company-specific knowledge")
        console.print("  ✓ Consistent answers across all agents")
        console.print("  ✓ Easy for managers to update knowledge")
        console.print("  ✓ No more 'I don't know' responses[/dim]\n")

    except Exception as e:
        console.print(f"\n[red]❌ Error:[/red] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
