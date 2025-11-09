"""
Agentic Workflow - Main Entry Point
Select and run different agent examples
"""

import sys
from config import Config


def print_menu():
    """Display the main menu"""
    print("\n" + "=" * 60)
    print("🤖 Agentic Workflow - Multi-Agent System")
    print("=" * 60)
    print("\nChoose an example to run:\n")
    print("1. Basic Agent - Simple conversational agent")
    print("2. Multi-Agent Team - Collaborative agents (Research, Writer, Critic)")
    print("3. Agent with Tools - Agent with custom tool capabilities")
    print("4. Exit")
    print("\n" + "=" * 60)


def run_basic_agent():
    """Run the basic agent example"""
    from basic_agent import main
    main()


def run_multi_agent_team():
    """Run the multi-agent team example"""
    from multi_agent_team import main
    main()


def run_tool_agent():
    """Run the agent with tools example"""
    from agent_with_tools import main
    main()


def main():
    """Main entry point"""

    # Validate configuration first
    try:
        Config.validate()
        print("\n✓ Ready to run agents!\n")
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease create a .env file based on .env.example")
        sys.exit(1)

    while True:
        print_menu()

        try:
            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                run_basic_agent()
            elif choice == "2":
                run_multi_agent_team()
            elif choice == "3":
                run_tool_agent()
            elif choice == "4":
                print("\n👋 Goodbye!\n")
                break
            else:
                print("\n❌ Invalid choice. Please select 1-4.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
