"""
Recruitment Agency Domain Configuration

Complete two-sided marketplace automation:
- Candidate side: Screening, matching, nurturing
- Client side: Business development, relationship management
- Video interviews: Automated screening calls

This domain handles the full recruitment lifecycle.
"""

from domain_config import DomainConfig
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class RecruitmentWorkflows:
    """Pre-built workflows for recruitment agencies"""

    # Candidate-side workflows
    RESUME_SCREENING = "resume_screening"
    CANDIDATE_MATCHING = "candidate_matching"
    VIDEO_SCREENING = "video_screening"
    CANDIDATE_NURTURING = "candidate_nurturing"
    OFFER_NEGOTIATION = "offer_negotiation"

    # Client-side workflows (BD)
    CLIENT_RESEARCH = "client_research"
    CLIENT_OUTREACH = "client_outreach"
    JOB_INTAKE = "job_intake"
    CLIENT_RELATIONSHIP = "client_relationship"

    # Pipeline management
    PIPELINE_ANALYSIS = "pipeline_analysis"
    PLACEMENT_PREDICTION = "placement_prediction"
    GHOSTING_PREVENTION = "ghosting_prevention"


def create_recruitment_domain() -> DomainConfig:
    """
    Create recruitment agency domain

    Features:
    - Two-sided marketplace (candidates + clients)
    - Video screening interviews
    - BD automation
    - Placement prediction
    """

    return DomainConfig(
        domain_name="recruitment",

        workflows=[
            # Candidate workflows
            RecruitmentWorkflows.RESUME_SCREENING,
            RecruitmentWorkflows.CANDIDATE_MATCHING,
            RecruitmentWorkflows.VIDEO_SCREENING,
            RecruitmentWorkflows.CANDIDATE_NURTURING,
            RecruitmentWorkflows.OFFER_NEGOTIATION,

            # Client workflows
            RecruitmentWorkflows.CLIENT_RESEARCH,
            RecruitmentWorkflows.CLIENT_OUTREACH,
            RecruitmentWorkflows.JOB_INTAKE,
            RecruitmentWorkflows.CLIENT_RELATIONSHIP,

            # Analytics
            RecruitmentWorkflows.PIPELINE_ANALYSIS,
            RecruitmentWorkflows.PLACEMENT_PREDICTION,
            RecruitmentWorkflows.GHOSTING_PREVENTION,
        ],

        agent_types=[
            # Candidate-side agents
            "Resume Screener",
            "Candidate Matcher",
            "Video Interviewer",
            "Salary Negotiator",
            "Candidate Relationship Manager",

            # Client-side agents (BD)
            "Company Research Agent",
            "BD Outreach Agent",
            "Job Intake Specialist",
            "Client Relationship Manager",
            "Hiring Manager Profiler",

            # Analytics agents
            "Pipeline Analyst",
            "Placement Predictor",
            "Ghosting Detector",
            "Market Intelligence Agent",
        ],

        domain_vocabulary=[
            # Candidate terms
            "resume", "CV", "candidate", "skills", "experience",
            "job seeker", "applicant", "background check",
            "reference check", "portfolio",

            # Client terms
            "hiring manager", "job description", "JD",
            "client", "employer", "job opening", "vacancy",
            "requisition", "req", "headcount",

            # Process terms
            "ATS", "applicant tracking system",
            "phone screen", "video interview", "technical assessment",
            "take-home test", "offer letter", "background check",
            "onboarding", "start date",

            # Metrics
            "time-to-fill", "time-to-hire",
            "offer acceptance rate", "candidate satisfaction",
            "client satisfaction", "placement fee",
            "fill rate", "submission-to-interview ratio",
            "interview-to-offer ratio",

            # BD terms
            "cold outreach", "warm intro", "referral",
            "LinkedIn sourcing", "boolean search",
            "hiring need", "growth stage", "hiring plan",
            "exclusive agreement", "contingent search",
        ],

        domain_context="""
        Recruitment agency specializing in tech placements.

        Business Model:
        - Contingent search (paid on placement)
        - Average placement fee: $25,000 (20% of first-year salary)
        - Focus: Software engineers, product managers, designers

        Key Metrics:
        - Time-to-fill: Target <25 days
        - Offer acceptance rate: Target >75%
        - Candidate satisfaction: Target >4.2/5
        - Client retention: Target >80%

        Two-Sided Marketplace:
        1. Candidate Side: Source, screen, match, present, negotiate
        2. Client Side: Research companies, outreach, build relationships, intake jobs

        Competitive Advantages:
        - Speed (faster time-to-fill)
        - Quality (better candidate-job matching)
        - Automation (lower cost structure)
        - Predictability (placement success prediction)
        """,

        data_dir="./workflow_db/domains/recruitment"
    )


# Knowledge base structure for recruitment
RECRUITMENT_KNOWLEDGE_CATEGORIES = {
    "candidate_outreach_templates": [
        "software_engineer_outreach",
        "product_manager_outreach",
        "designer_outreach",
        "executive_outreach",
    ],

    "client_bd_templates": [
        "cold_outreach_to_hiring_manager",
        "linkedin_connection_request",
        "follow_up_after_no_response",
        "job_intake_call_script",
        "negotiating_terms_and_fees",
    ],

    "interview_question_banks": [
        "technical_screening_questions",
        "behavioral_questions",
        "culture_fit_questions",
        "red_flag_detection_questions",
    ],

    "salary_data": [
        "software_engineer_salary_by_location",
        "startup_vs_corporate_compensation",
        "equity_negotiation_guidelines",
    ],

    "company_profiles": [
        "past_client_companies",
        "target_client_companies",
        "company_culture_notes",
        "hiring_manager_preferences",
    ],

    "placement_history": [
        "successful_placements",
        "failed_placements_learnings",
        "candidate_feedback",
        "client_feedback",
    ],
}


# Integration points for recruitment tech stack
RECRUITMENT_INTEGRATIONS = {
    "ats": {
        "bullhorn": {"api_available": True, "priority": "high"},
        "greenhouse": {"api_available": True, "priority": "high"},
        "lever": {"api_available": True, "priority": "medium"},
        "workable": {"api_available": True, "priority": "medium"},
    },

    "sourcing": {
        "linkedin_recruiter": {"api_available": True, "priority": "high"},
        "github": {"api_available": True, "priority": "medium"},
        "stackoverflow": {"api_available": True, "priority": "low"},
    },

    "video_platforms": {
        "zoom": {"api_available": True, "priority": "high"},
        "microsoft_teams": {"api_available": True, "priority": "high"},
        "google_meet": {"api_available": True, "priority": "medium"},
    },

    "communication": {
        "email": {"smtp": True, "priority": "high"},
        "sms": {"twilio": True, "priority": "medium"},
        "whatsapp": {"api_available": True, "priority": "low"},
    },

    "background_check": {
        "checkr": {"api_available": True, "priority": "medium"},
        "sterling": {"api_available": True, "priority": "medium"},
    },
}


if __name__ == "__main__":
    # Demo: Create recruitment domain
    from rich.console import Console
    console = Console()

    console.print("\n[bold cyan]Recruitment Domain Configuration[/bold cyan]\n")

    domain = create_recruitment_domain()

    console.print(f"[green]Domain:[/green] {domain.domain_name}")
    console.print(f"[green]Workflows:[/green] {len(domain.workflows)} workflows")
    console.print(f"[green]Agent Types:[/green] {len(domain.agent_types)} specialized agents")
    console.print(f"[green]Vocabulary:[/green] {len(domain.domain_vocabulary)} domain terms\n")

    console.print("[yellow]Candidate Workflows:[/yellow]")
    for wf in domain.workflows[:5]:
        console.print(f"  • {wf}")

    console.print("\n[yellow]Client (BD) Workflows:[/yellow]")
    for wf in domain.workflows[5:9]:
        console.print(f"  • {wf}")

    console.print("\n[yellow]Key Agent Types:[/yellow]")
    console.print("  [cyan]Candidate Side:[/cyan]")
    for agent in domain.agent_types[:5]:
        console.print(f"    • {agent}")

    console.print("  [cyan]Client Side (BD):[/cyan]")
    for agent in domain.agent_types[5:10]:
        console.print(f"    • {agent}")

    console.print("\n[green]✓ Recruitment domain ready for deployment[/green]\n")
