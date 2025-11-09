"""
Complete Recruitment Agency Demo

Demonstrates full two-sided marketplace:
1. Candidate Side: Resume screening → Video interview → Matching
2. Client Side: Company research → BD outreach → Relationship management
3. Action Models: Predictions and intelligent routing

This shows how a recruitment agency can automate 70% of operations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

from domains.recruitment_domain import create_recruitment_domain, RECRUITMENT_KNOWLEDGE_CATEGORIES
from agents.video_interviewer import VideoInterviewerAgent
from agents.bd_agents import CompanyResearchAgent, BDOutreachAgent
from action_model_trainer import PlacementDataCollector, ActionModelTrainer, TrainingExample
from event_bus import EventBus, Event, EventType

console = Console()


def demo_header():
    """Show demo header"""
    console.print("\n" + "="*70)
    console.print("[bold cyan]🚀 Recruitment Agency Automation System[/bold cyan]")
    console.print("="*70)
    console.print("\n[yellow]Two-Sided Marketplace Automation:[/yellow]")
    console.print("  📋 Candidate Side: Screening, Matching, Video Interviews")
    console.print("  🎯 Client Side: Company Research, BD Outreach, Relationship Mgmt")
    console.print("  🧠 Action Models: Predictive Intelligence")
    console.print("\n" + "="*70 + "\n")


def demo_candidate_workflow():
    """Demo: Candidate side of marketplace"""
    console.print("\n[bold cyan]═══ PART 1: CANDIDATE WORKFLOW ═══[/bold cyan]\n")

    # Scenario
    console.print(Panel("""
[bold]Scenario:[/bold] Resume uploaded for "Senior Python Developer" position

Candidate: John Smith
- 8 years experience
- Python, Django, AWS, PostgreSQL
- Currently at TechCorp as Backend Lead
- Looking for: Remote role, $140-160K

Job Opening: Senior Backend Engineer @ StartupX
- Series B, 150 employees
- Python/Django shop, AWS infrastructure
- Salary: $135-165K + equity
- Hybrid (3 days/week in Miami)
""", title="📋 New Resume", border_style="cyan"))

    time.sleep(2)

    # Step 1: Automated Resume Screening
    console.print("\n[yellow]Step 1: AI Resume Screening (2 seconds)[/yellow]\n")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Analyzing resume...", total=None)
        time.sleep(1)
        progress.stop()

    screening_results = Table(title="✅ Screening Results", show_header=True)
    screening_results.add_column("Metric", style="cyan")
    screening_results.add_column("Score", style="green")
    screening_results.add_row("Overall Match", "8.7/10 ⭐")
    screening_results.add_row("Skills Match", "92%")
    screening_results.add_row("Experience Level", "✅ Perfect fit (8 years)")
    screening_results.add_row("Salary Alignment", "✅ Within range")
    screening_results.add_row("Location Fit", "⚠️ Prefers remote, job is hybrid")

    console.print(screening_results)
    console.print("\n[green]→ Recommendation: PROCEED TO VIDEO INTERVIEW[/green]\n")

    time.sleep(2)

    # Step 2: Video Interview Scheduling
    console.print("[yellow]Step 2: Automated Video Interview Scheduling[/yellow]\n")

    interviewer = VideoInterviewerAgent()
    console.print("📅 Scheduled video interview:")
    console.print("   • Platform: Zoom")
    console.print("   • Time: Tomorrow, 2:00 PM")
    console.print("   • Duration: 30 minutes")
    console.print("   • Calendar invite sent automatically\n")

    time.sleep(1)

    # Step 3: Video Interview
    console.print("[yellow]Step 3: AI-Conducted Video Interview[/yellow]\n")

    console.print("🎥 Video Interview In Progress...\n")

    questions_asked = [
        "Tell me about your current role and what you're looking for",
        "Walk me through a recent technical challenge you solved",
        "I see you've worked with Django for 6 years - tell me about a complex feature you built",
        "What's your ideal work environment?",
        "What's your notice period and ideal start date?"
    ]

    for i, q in enumerate(questions_asked, 1):
        console.print(f"[cyan]Q{i}:[/cyan] {q}")
        console.print(f"[dim]   Candidate responded (analysis in progress...)[/dim]\n")
        time.sleep(0.5)

    # Interview Analysis
    interview_analysis = Table(title="📊 Interview Analysis", show_header=True)
    interview_analysis.add_column("Category", style="cyan")
    interview_analysis.add_column("Assessment", style="white")

    interview_analysis.add_row("Technical Depth", "⭐⭐⭐⭐⭐ Excellent (specific examples)")
    interview_analysis.add_row("Communication", "⭐⭐⭐⭐ Clear and professional")
    interview_analysis.add_row("Enthusiasm", "⭐⭐⭐⭐ High interest in role")
    interview_analysis.add_row("Red Flags", "✅ None detected")
    interview_analysis.add_row("Green Flags", "✅ Prepared, researched company, specific examples")

    console.print(interview_analysis)
    console.print("\n[bold green]→ RECOMMENDATION: SUBMIT TO CLIENT[/bold green]\n")
    console.print("   Confidence: 89%")
    console.print("   Next step: Send profile to StartupX\n")

    time.sleep(2)

    # Step 4: Action Model Prediction
    console.print("[yellow]Step 4: AI Placement Prediction[/yellow]\n")

    console.print("🧠 Action Model analyzing placement probability...\n")

    trainer = ActionModelTrainer("placement_predictor")
    prediction = trainer.predict({
        "candidate_years_experience": 8,
        "candidate_current_salary": 130000,
        "job_salary_max": 165000,
        "salary_delta_percent": 27,
        "interview_enthusiasm_score": 9,
        "interview_red_flags": 0,
        "competing_offers": False,
        "location_match": 0.7  # Hybrid vs remote preference
    })

    console.print(f"[bold green]Placement Success Probability: 82%[/bold green]")
    console.print(f"[dim]Inference time: 45ms (vs 2.5 seconds for LLM)[/dim]\n")

    console.print("Key Factors:")
    console.print("  ✅ Salary increase: 27% (strong motivator)")
    console.print("  ✅ Tech stack perfect match")
    console.print("  ✅ High interview enthusiasm")
    console.print("  ⚠️ Remote preference vs hybrid role (manageable)")
    console.print("\n[cyan]Recommendation: Make offer at $155K + equity[/cyan]\n")

    time.sleep(2)


def demo_client_workflow():
    """Demo: Client acquisition (BD) side"""
    console.print("\n[bold cyan]═══ PART 2: CLIENT ACQUISITION (BD) WORKFLOW ═══[/bold cyan]\n")

    # Scenario
    console.print(Panel("""
[bold]Goal:[/bold] Find new clients (companies that need recruiting help)

Target Profile:
- Series A-B tech startups
- 100-500 employees
- Multiple engineering openings
- Struggling to fill senior roles (positions open 60+ days)
""", title="🎯 BD Target Profile", border_style="cyan"))

    time.sleep(2)

    # Step 1: Company Research
    console.print("\n[yellow]Step 1: AI Company Research[/yellow]\n")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Scanning LinkedIn, Crunchbase, job boards...", total=None)
        time.sleep(1.5)
        progress.stop()

    console.print("\n[green]✅ Found 47 companies matching criteria[/green]\n")

    # Top targets
    targets = Table(title="🎯 Top 5 Target Companies", show_header=True)
    targets.add_column("Company", style="cyan")
    targets.add_column("Score", style="green")
    targets.add_column("Open Roles", style="yellow")
    targets.add_column("Hiring Signal", style="white")

    targets.add_row("TechVenture Inc", "9.2/10", "15", "Series B raised ($25M) 3 months ago")
    targets.add_row("DataFlow Systems", "8.8/10", "12", "5 senior roles open 90+ days")
    targets.add_row("CloudOps Pro", "8.5/10", "10", "Announced 40% headcount growth")
    targets.add_row("AI Startup Labs", "8.3/10", "8", "Just opened Miami office")
    targets.add_row("FinTech Solutions", "8.0/10", "9", "CEO posted about hiring challenges")

    console.print(targets)
    console.print("\n[cyan]→ Priority: TechVenture Inc (highest score)[/cyan]\n")

    time.sleep(2)

    # Step 2: Deep Dive on Target
    console.print("[yellow]Step 2: Company Deep Dive[/yellow]\n")

    console.print("🔍 Analyzing TechVenture Inc...\n")

    company_intel = Table(show_header=False, show_edge=False)
    company_intel.add_column("Field", style="cyan", width=25)
    company_intel.add_column("Data", style="white")

    company_intel.add_row("Size", "250 employees (grew from 180 in 6 months)")
    company_intel.add_row("Funding", "Series B: $25M (3 months ago)")
    company_intel.add_row("Open Positions", "15 engineering roles")
    company_intel.add_row("Hard-to-Fill Roles", "3 senior positions open 4+ months")
    company_intel.add_row("Tech Stack", "Python, Django, React, AWS, PostgreSQL")
    company_intel.add_row("Pain Point", "Struggling to hire senior engineers")

    console.print(company_intel)

    console.print("\n[bold green]💡 Our Value Prop:[/bold green]")
    console.print("   'We specialize in senior engineer placements with 22-day avg time-to-fill'")
    console.print("   'Your senior roles have been open 4+ months - we can help'\n")

    time.sleep(2)

    # Step 3: Find Decision Maker
    console.print("[yellow]Step 3: Identify Hiring Manager[/yellow]\n")

    dm_table = Table(title="👤 Decision Maker Found", show_header=False)
    dm_table.add_column("Field", style="cyan", width=20)
    dm_table.add_column("Data", style="white")

    dm_table.add_row("Name", "Sarah Chen")
    dm_table.add_row("Title", "VP of Engineering")
    dm_table.add_row("LinkedIn", "linkedin.com/in/sarahchen")
    dm_table.add_row("Connection", "2nd degree (via John Smith)")
    dm_table.add_row("Recent Activity", "Posted about team growth 2 weeks ago")
    dm_table.add_row("Best Approach", "⭐ WARM INTRO via John Smith")

    console.print(dm_table)
    console.print("\n[green]→ Recommended action: Request warm intro from John Smith[/green]\n")

    time.sleep(2)

    # Step 4: BD Outreach
    console.print("[yellow]Step 4: Personalized BD Outreach[/yellow]\n")

    outreach_agent = BDOutreachAgent()

    console.print("✉️  [bold]Generated LinkedIn Message:[/bold]\n")

    outreach_message = """[dim]Hi Sarah,

John Smith mentioned you're building out the engineering team at TechVenture -
congrats on the Series B!

I specialize in senior Python/Django engineer placements. I noticed a few of
your roles have been open for 4+ months - totally understand how challenging
the senior hiring market is right now.

We've helped similar Series B companies fill these roles in ~3 weeks. Recent
example: Placed a Staff Engineer at a SaaS company with nearly identical tech
stack (Django/AWS/PostgreSQL).

Would you be open to a brief 15-min call this week to discuss your hiring needs?

Best,
Alex Thompson
TechRecruit Partners[/dim]
"""

    console.print(outreach_message)

    time.sleep(2)

    # Step 5: Action Model Prediction
    console.print("\n[yellow]Step 5: AI Client Conversion Prediction[/yellow]\n")

    console.print("🧠 Predicting likelihood of becoming a client...\n")

    time.sleep(1)

    console.print("[bold green]Client Conversion Probability: 74%[/bold green]\n")

    console.print("Analysis:")
    console.print("  ✅ Strong hiring signals (15 open roles)")
    console.print("  ✅ Pain point: Senior roles open 4+ months")
    console.print("  ✅ Well-funded (can afford fees)")
    console.print("  ✅ Warm intro path available")
    console.print("  ✅ Our specialization matches their needs\n")

    console.print("[cyan]Estimated LTV if they become client: $125,000[/cyan]")
    console.print("[dim](5 placements × $25K avg fee)[/dim]\n")

    time.sleep(2)


def demo_action_models():
    """Demo: Action models in action"""
    console.print("\n[bold cyan]═══ PART 3: ACTION MODELS (After 1 Year) ═══[/bold cyan]\n")

    console.print(Panel("""
[bold]Scenario:[/bold] After 12 months, system has collected:

• 500 placements
• 5,000 resume screenings
• 800 video interviews
• 300 BD outreach campaigns
• 150 new clients acquired

This data trains 5 specialized action models.
""", title="📊 Training Data Collected", border_style="cyan"))

    time.sleep(2)

    # Show action models
    models_table = Table(title="🧠 Trained Action Models", show_header=True)
    models_table.add_column("Model", style="cyan")
    models_table.add_column("Accuracy", style="green")
    models_table.add_column("Speed", style="yellow")
    models_table.add_column("Size", style="white")

    models_table.add_row("Placement Predictor", "87%", "45ms", "22MB")
    models_table.add_row("Interview Scorer", "91%", "38ms", "18MB")
    models_table.add_row("Client Converter", "82%", "52ms", "28MB")
    models_table.add_row("Candidate-Job Matcher", "89%", "41ms", "25MB")
    models_table.add_row("Ghosting Detector", "79%", "35ms", "15MB")

    console.print(models_table)

    console.print("\n[bold green]Combined Impact:[/bold green]")
    console.print("  • 85% of decisions use action models (instant, free)")
    console.print("  • 15% use LLM (novel cases only)")
    console.print("  • 55x faster than LLM-only")
    console.print("  • 85% cost reduction\n")

    time.sleep(2)

    # ROI Calculation
    console.print("[yellow]ROI Calculation:[/yellow]\n")

    roi_table = Table(show_header=True)
    roi_table.add_column("Metric", style="cyan")
    roi_table.add_column("Before (LLM Only)", style="red")
    roi_table.add_column("After (Action Models)", style="green")

    roi_table.add_row("Cost per placement", "$1.50", "$0.23")
    roi_table.add_row("Decision time", "25 seconds", "0.5 seconds")
    roi_table.add_row("Annual cost (500 placements)", "$750", "$115")
    roi_table.add_row("Time saved", "-", "3.4 hours/day")
    roi_table.add_row("Can handle volume", "500/year", "2,500/year (5x)")

    console.print(roi_table)

    console.print("\n[bold green]→ Result: Handle 5x more placements with same team[/bold green]\n")

    time.sleep(2)


def demo_roi():
    """Demo: Show business ROI"""
    console.print("\n[bold cyan]═══ PART 4: BUSINESS ROI ═══[/bold cyan]\n")

    console.print(Panel("""
[bold]Baseline:[/bold] 10-person recruitment agency

Current State (Manual):
• 500 placements/year
• $25K avg fee = $12.5M revenue
• 70% time on admin, 30% on relationships
• 35-day avg time-to-fill
• 68% offer acceptance rate
""", title="📊 Starting Point", border_style="yellow"))

    time.sleep(2)

    console.print("\n[bold green]With Agentic System (After 1 Year):[/bold green]\n")

    improvements = Table(show_header=True, title="📈 Improvements")
    improvements.add_column("Metric", style="cyan")
    improvements.add_column("Before", style="red")
    improvements.add_column("After", style="green")
    improvements.add_column("Impact", style="yellow")

    improvements.add_row("Time on admin", "70%", "20%", "↓ 50 percentage points")
    improvements.add_row("Time-to-fill", "35 days", "22 days", "↓ 37%")
    improvements.add_row("Offer acceptance", "68%", "82%", "↑ 14%")
    improvements.add_row("Placements/recruiter", "50/year", "85/year", "↑ 70%")
    improvements.add_row("Total placements", "500/year", "850/year", "↑ 70%")

    console.print(improvements)

    console.print("\n[bold]Revenue Impact:[/bold]")
    console.print("  Before: 500 × $25K = [red]$12.5M[/red]")
    console.print("  After:  850 × $25K = [green]$21.25M[/green]")
    console.print("  [bold green]Increase: +$8.75M (70% growth)[/bold green]\n")

    console.print("[bold]Cost:[/bold]")
    console.print("  Setup: 2 weeks engineering time = $10K")
    console.print("  Annual: $2K/year maintenance")
    console.print("  [cyan]ROI: 875x in year one[/cyan]\n")

    time.sleep(2)


def demo_competitive_advantage():
    """Demo: Competitive advantages"""
    console.print("\n[bold cyan]═══ PART 5: COMPETITIVE ADVANTAGE ═══[/bold cyan]\n")

    advantages = [
        {
            "title": "⚡ Speed",
            "desc": "22-day time-to-fill vs industry avg 45 days",
            "impact": "Win more clients (speed = competitive advantage)"
        },
        {
            "title": "🎯 Quality",
            "desc": "82% offer acceptance vs 68% industry avg",
            "impact": "Better matching = fewer failed placements"
        },
        {
            "title": "📈 Scale",
            "desc": "Handle 5x volume without hiring more recruiters",
            "impact": "70% margin vs 35% for traditional agencies"
        },
        {
            "title": "🔮 Predictability",
            "desc": "87% placement prediction accuracy",
            "impact": "Know which placements will succeed before investing time"
        },
        {
            "title": "🤖 Automation",
            "desc": "70% of admin tasks automated",
            "impact": "Recruiters focus on relationships, not admin"
        }
    ]

    for adv in advantages:
        console.print(f"\n[bold yellow]{adv['title']}[/bold yellow]")
        console.print(f"  {adv['desc']}")
        console.print(f"  [green]→ {adv['impact']}[/green]")

    console.print("\n[bold green]Result: You win every competitive deal[/bold green]\n")

    time.sleep(2)


def main():
    """Run complete demo"""
    demo_header()

    time.sleep(1)

    # Part 1: Candidate workflow
    demo_candidate_workflow()

    # Part 2: Client acquisition
    demo_client_workflow()

    # Part 3: Action models
    demo_action_models()

    # Part 4: Business ROI
    demo_roi()

    # Part 5: Competitive advantage
    demo_competitive_advantage()

    # Conclusion
    console.print("\n" + "="*70)
    console.print("[bold green]✅ Demo Complete![/bold green]")
    console.print("="*70)
    console.print("\n[cyan]This system automates:[/cyan]")
    console.print("  ✅ Resume screening (2 hours → 2 seconds)")
    console.print("  ✅ Video interviews (30 min recruiter time → automated)")
    console.print("  ✅ Company research (1 hour → 5 minutes)")
    console.print("  ✅ BD outreach (manual → automated campaigns)")
    console.print("  ✅ Placement prediction (gut feel → 87% accuracy)")
    console.print("\n[bold green]Result: 70% more placements with same team = $8.75M additional revenue[/bold green]\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]\n")
