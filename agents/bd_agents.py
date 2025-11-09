"""
Business Development Agents for Recruitment

Agents that acquire new clients:
1. Company Research Agent - Finds companies hiring
2. BD Outreach Agent - Reaches hiring managers
3. Relationship Manager - Nurtures client relationships

This automates the client acquisition side of recruitment.
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from config import Config


@dataclass
class CompanyProfile:
    """Profile of a potential client company"""
    company_id: str
    company_name: str
    industry: str
    size_employees: str  # "50-200", "200-1000", etc.
    funding_stage: str  # "Seed", "Series A", "Series B", etc.
    recent_funding_amount: Optional[str] = None
    growth_indicators: List[str] = field(default_factory=list)  # ["Hiring 20+ roles", "Just raised Series B"]
    hiring_signals: List[str] = field(default_factory=list)  # ["Posted 15 jobs on LinkedIn"]
    tech_stack: List[str] = field(default_factory=list)
    target_score: float = 0.0  # 0-1, how good a target
    notes: str = ""


@dataclass
class HiringManager:
    """Profile of a hiring manager at target company"""
    manager_id: str
    name: str
    title: str
    company_name: str
    linkedin_url: str
    email: Optional[str] = None
    phone: Optional[str] = None
    hiring_for_roles: List[str] = field(default_factory=list)
    connection_status: str = "not_connected"  # not_connected, request_sent, connected
    outreach_history: List[Dict[str, Any]] = field(default_factory=list)
    last_contact_date: Optional[str] = None
    relationship_strength: str = "cold"  # cold, warm, hot


@dataclass
class OutreachCampaign:
    """BD outreach campaign"""
    campaign_id: str
    campaign_name: str
    target_companies: List[str]  # Company IDs
    message_template: str
    channel: str  # email, linkedin, phone
    status: str  # draft, active, completed
    sent_count: int = 0
    response_count: int = 0
    meeting_booked_count: int = 0
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())


class CompanyResearchAgent:
    """
    Researches companies to find hiring needs

    Data sources:
    - LinkedIn (job postings, company updates, employee growth)
    - Crunchbase (funding, growth stage)
    - Company websites (careers pages)
    - News (expansion announcements)
    """

    def __init__(self):
        self.lm_config = Config.get_lmstudio_config()
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the company research agent"""

        @tool
        def find_companies_hiring(
            industry: str,
            location: str,
            min_employees: int = 50,
            funding_stage: Optional[str] = None
        ) -> str:
            """
            Find companies that are actively hiring

            Searches for companies with strong hiring signals:
            - Multiple job postings
            - Recent funding
            - Headcount growth
            - Expansion announcements
            """
            # TODO: Actual integration with LinkedIn, Crunchbase APIs
            # For now, return mock data

            companies = [
                {
                    "company_name": "TechStartup Inc",
                    "industry": "SaaS",
                    "employees": "200-500",
                    "funding_stage": "Series B",
                    "recent_funding": "$25M Series B (3 months ago)",
                    "hiring_signals": [
                        "15 open positions on LinkedIn",
                        "Announced expansion to Miami office",
                        "Headcount grew 40% in last 6 months"
                    ],
                    "open_roles": [
                        "Senior Backend Engineer (Python)",
                        "Frontend Engineer (React)",
                        "DevOps Engineer",
                        "Product Manager"
                    ],
                    "target_score": 0.92,
                    "why_good_target": "Strong hiring signals, well-funded, growing fast"
                },
                {
                    "company_name": "FinTech Solutions",
                    "industry": "FinTech",
                    "employees": "100-200",
                    "funding_stage": "Series A",
                    "recent_funding": "$12M Series A (6 months ago)",
                    "hiring_signals": [
                        "8 open positions",
                        "Just announced new product launch"
                    ],
                    "open_roles": [
                        "Full Stack Engineer",
                        "Data Engineer"
                    ],
                    "target_score": 0.78,
                    "why_good_target": "Growing team, technical hiring needs"
                }
            ]

            return json.dumps(companies, indent=2)

        @tool
        def analyze_company_hiring_need(
            company_name: str,
            company_website: str
        ) -> str:
            """
            Analyze a specific company's hiring needs

            Looks at:
            - Current job openings
            - Growth trajectory
            - Tech stack
            - Hiring urgency signals
            """
            # TODO: Scrape careers page, analyze LinkedIn

            analysis = {
                "company_name": company_name,
                "hiring_urgency": "HIGH",
                "open_positions": 12,
                "hard_to_fill_roles": [
                    "Senior Backend Engineer (6 months open)",
                    "Staff Engineer (3 months open)"
                ],
                "tech_stack": ["Python", "Django", "React", "AWS", "PostgreSQL"],
                "ideal_approach": "Contact VP Engineering directly - they're struggling to fill senior roles",
                "pain_points": [
                    "Slow hiring process (positions open for months)",
                    "Competing with larger companies for talent",
                    "Need senior engineers, not junior"
                ],
                "value_proposition": "We specialize in senior engineer placements with 22-day avg time-to-fill"
            }

            return json.dumps(analysis, indent=2)

        @tool
        def find_hiring_managers(
            company_name: str,
            department: str = "Engineering"
        ) -> str:
            """
            Find hiring managers at a target company

            Searches LinkedIn for:
            - VP Engineering
            - Engineering Managers
            - CTOs
            - Recruiters
            """
            # TODO: LinkedIn API or web scraping

            managers = [
                {
                    "name": "Sarah Chen",
                    "title": "VP of Engineering",
                    "linkedin_url": "https://linkedin.com/in/sarahchen",
                    "likely_hiring_for": ["Senior Engineers", "Staff Engineers"],
                    "connection_path": "2nd degree (connected via John Smith)",
                    "recent_activity": "Posted about team growth 2 weeks ago",
                    "best_approach": "Warm intro via John Smith"
                },
                {
                    "name": "Michael Rodriguez",
                    "title": "Engineering Manager - Backend",
                    "linkedin_url": "https://linkedin.com/in/mrodriguez",
                    "likely_hiring_for": ["Backend Engineers"],
                    "connection_path": "3rd degree",
                    "best_approach": "Cold outreach on LinkedIn"
                }
            ]

            return json.dumps(managers, indent=2)

        agent = Agent(
            name="Company Research Agent",
            role="BD research specialist finding companies with hiring needs",
            model=OpenAIChat(
                id=self.lm_config["model"],
                api_key=self.lm_config["api_key"],
                base_url=self.lm_config["base_url"],
                http_client=Config.get_http_client()
            ),
            tools=[
                find_companies_hiring,
                analyze_company_hiring_need,
                find_hiring_managers
            ],
            instructions=[
                "You are a BD research specialist for a recruitment agency.",
                "",
                "Your role:",
                "1. Find companies that are actively hiring",
                "2. Analyze their hiring needs and urgency",
                "3. Identify decision-makers (VPs, Hiring Managers)",
                "4. Assess how good of a target they are",
                "",
                "Strong hiring signals:",
                "- Multiple job postings (especially hard-to-fill roles)",
                "- Recent funding (indicates hiring budget)",
                "- Headcount growth",
                "- Expansion announcements",
                "- Job posts open for >60 days (struggling to hire)",
                "",
                "Best targets:",
                "- Series A-C startups (have budget, need speed)",
                "- Tech companies with 100-500 employees",
                "- Companies with senior/specialized roles",
                "- Growing teams in competitive markets",
                "",
                "Research approach:",
                "1. Start broad (industry, location filters)",
                "2. Narrow to high-signal companies",
                "3. Deep dive on top targets",
                "4. Find specific hiring managers",
                "5. Identify best outreach approach (warm intro vs cold)",
                "",
                "Provide actionable intelligence:",
                "- Why is this a good target?",
                "- What are their pain points?",
                "- Who should we contact?",
                "- What's our value proposition for them?"
            ],
            markdown=True
        )

        return agent


class BDOutreachAgent:
    """
    Reaches out to hiring managers to acquire clients

    Channels:
    - LinkedIn (connection requests, InMail)
    - Email (cold outreach)
    - Phone (warm calls)

    Strategies:
    - Personalized messaging
    - Value-first approach
    - Multi-touch sequences
    """

    def __init__(self):
        self.lm_config = Config.get_lmstudio_config()
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the BD outreach agent"""

        @tool
        def create_personalized_outreach(
            hiring_manager_name: str,
            hiring_manager_title: str,
            company_name: str,
            company_pain_points: List[str],
            channel: str = "linkedin"
        ) -> str:
            """
            Create personalized outreach message

            Principles:
            - Lead with value, not your service
            - Reference specific company context
            - Clear, concise ask
            - Professional but friendly tone
            """
            # Template varies by channel

            if channel == "linkedin":
                return json.dumps({
                    "connection_request": f"Hi {hiring_manager_name.split()[0]}, I help {company_name.split()[0]} companies scale engineering teams quickly. Would love to connect!",
                    "follow_up_message": f"""Hi {hiring_manager_name.split()[0]},

I noticed {company_name} has been hiring for senior engineering roles. I specialize in placing senior Python/React engineers with 22-day avg time-to-fill.

One of our recent placements was similar to what you're building - happy to share details if helpful.

Would you be open to a brief call this week?

Best,
[Your Name]""",
                    "timing": "Send connection request now, wait 2 days, then send message if accepted"
                }, indent=2)

            elif channel == "email":
                return json.dumps({
                    "subject_line": f"Senior engineer placements for {company_name}",
                    "email_body": f"""Hi {hiring_manager_name.split()[0]},

I see {company_name} is hiring for [{', '.join(['Senior Backend Engineer', 'Staff Engineer'])}].

We specialize in these exact roles - our avg time-to-fill is 22 days vs industry avg of 45 days.

Recent placement: Placed a Senior Python Engineer with similar tech stack ({company_name} uses Django/AWS) at a Series B startup in 18 days.

Would you be open to a 15-min call to discuss your hiring needs?

Best regards,
[Your Name]
[Agency Name]
[Phone]""",
                    "follow_up_sequence": [
                        {"day": 3, "subject": "Quick follow-up", "message": "Bumping this up - would love to help with your senior eng hires"},
                        {"day": 7, "subject": "Final follow-up", "message": "Last note - if timing isn't right now, happy to connect for future hiring needs"}
                    ]
                }, indent=2)

            else:  # phone
                return json.dumps({
                    "call_script": f"""
Opening: "Hi {hiring_manager_name.split()[0]}, this is [Your Name] from [Agency]. Is this a good time for a quick call?"

If yes: "I noticed you're hiring for [role]. I specialize in placing senior engineers - we've helped companies like [similar company] fill these roles in under 3 weeks. Is hiring for this role a priority right now?"

Value prop: "We work on contingency, so you only pay if we successfully place someone. And our average time-to-fill is 22 days."

Ask: "Would it make sense to have a brief call to understand your hiring needs?"

If no/busy: "No problem! Would [day/time] work better? Or I can send an email with more details?"
""",
                    "objection_handling": {
                        "We have internal recruiters": "Great! We often work alongside internal teams on hard-to-fill senior roles. Want to discuss?",
                        "We're not hiring right now": "Understood! Mind if I follow up in [timeframe]? Or happy to connect for future needs.",
                        "We already have agencies": "That's fine - we specialize in senior engineer placements. Happy to be a backup resource."
                    }
                }, indent=2)

        @tool
        def analyze_outreach_performance(
            campaign_id: str,
            sent_count: int,
            response_count: int,
            meeting_booked_count: int
        ) -> str:
            """
            Analyze outreach campaign performance

            Provides optimization recommendations
            """
            response_rate = (response_count / sent_count * 100) if sent_count > 0 else 0
            meeting_rate = (meeting_booked_count / response_count * 100) if response_count > 0 else 0

            benchmarks = {
                "linkedin": {"response_rate": 15, "meeting_rate": 30},
                "email": {"response_rate": 8, "meeting_rate": 25}
            }

            analysis = {
                "performance": {
                    "sent": sent_count,
                    "responses": response_count,
                    "meetings_booked": meeting_booked_count,
                    "response_rate": f"{response_rate:.1f}%",
                    "meeting_rate": f"{meeting_rate:.1f}%"
                },
                "vs_benchmark": {
                    "response_rate": "Above average" if response_rate > 12 else "Below average",
                    "meeting_rate": "Above average" if meeting_rate > 27 else "Below average"
                },
                "recommendations": []
            }

            if response_rate < 10:
                analysis["recommendations"].append("Low response rate - try more personalization, better targeting")
            if meeting_rate < 25:
                analysis["recommendations"].append("Low meeting conversion - improve value proposition in messages")

            return json.dumps(analysis, indent=2)

        agent = Agent(
            name="BD Outreach Agent",
            role="Client acquisition specialist reaching hiring managers",
            model=OpenAIChat(
                id=self.lm_config["model"],
                api_key=self.lm_config["api_key"],
                base_url=self.lm_config["base_url"],
                http_client=Config.get_http_client()
            ),
            tools=[
                create_personalized_outreach,
                analyze_outreach_performance
            ],
            instructions=[
                "You are a BD specialist for a recruitment agency acquiring new clients.",
                "",
                "Your goal: Get meetings with hiring managers who need recruiting help.",
                "",
                "Outreach principles:",
                "1. Personalization: Reference company-specific context",
                "2. Value-first: Lead with how you can help, not what you sell",
                "3. Brevity: Keep messages short and scannable",
                "4. Clear CTA: Specific ask (15-min call, not 'let me know')",
                "5. Timing: Multi-touch sequences, not one-and-done",
                "",
                "Best practices by channel:",
                "",
                "LinkedIn:",
                "- Connection request: Short, friendly, value-focused",
                "- Follow-up message: Wait 2-3 days after connection",
                "- InMail: Use for decision-makers who haven't accepted connection",
                "",
                "Email:",
                "- Subject line: Specific and benefit-focused",
                "- Body: 3-5 sentences max",
                "- Include social proof (similar placements)",
                "- Follow up 2-3 times (days 3, 7)",
                "",
                "Phone:",
                "- Ask permission for time first",
                "- Have a clear value prop ready",
                "- Handle objections smoothly",
                "- Book next step immediately",
                "",
                "Key metrics:",
                "- Response rate: Target >12% (email), >15% (LinkedIn)",
                "- Meeting booking rate: Target >25% of responses",
                "- Meeting-to-client rate: Target >40%",
                "",
                "Red flags to avoid:",
                "- Generic templates (personalize everything)",
                "- Talking about yourself first (lead with their needs)",
                "- Multiple asks in one message (one clear CTA)",
                "- No follow-up (80% of meetings come after follow-ups)"
            ],
            markdown=True
        )

        return agent


if __name__ == "__main__":
    # Demo
    from rich.console import Console
    console = Console()

    console.print("\n[bold cyan]BD Agents Demo[/bold cyan]\n")

    # Company Research Agent
    console.print("[yellow]1. Company Research Agent[/yellow]\n")
    research_agent = CompanyResearchAgent()

    research_prompt = """
    Find me 5 tech startups in Miami that are actively hiring for engineering roles.
    Focus on Series A-B companies with 100-500 employees.
    """

    research_result = research_agent.agent.run(research_prompt)
    console.print("[green]Research Results:[/green]")
    console.print(research_result.content[:500] + "...\n")

    # BD Outreach Agent
    console.print("[yellow]2. BD Outreach Agent[/yellow]\n")
    outreach_agent = BDOutreachAgent()

    outreach_prompt = """
    Create a personalized LinkedIn outreach message for:
    - Hiring Manager: Sarah Chen, VP of Engineering at TechStartup Inc
    - Company is hiring for Senior Backend Engineers (roles open for 4+ months)
    - They're Series B, growing fast, struggling to fill senior roles
    """

    outreach_result = outreach_agent.agent.run(outreach_prompt)
    console.print("[green]Outreach Message:[/green]")
    console.print(outreach_result.content[:500] + "...\n")
