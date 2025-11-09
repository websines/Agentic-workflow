"""
Video Interviewer Agent

Conducts automated screening interviews via video call:
- Schedules and joins video calls
- Asks screening questions
- Analyzes responses via speech-to-text
- Detects red flags and green flags
- Provides hiring recommendation

Integrations:
- Zoom API (meeting creation, joining)
- Speech-to-text (Whisper, Google Speech, etc.)
- Sentiment analysis
- Action model for response quality scoring
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from config import Config


@dataclass
class InterviewQuestion:
    """A single interview question"""
    question_id: str
    question_text: str
    question_type: str  # technical, behavioral, culture_fit, red_flag_detection
    expected_response_time_seconds: int = 120
    follow_up_questions: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    green_flags: List[str] = field(default_factory=list)


@dataclass
class InterviewResponse:
    """Candidate's response to a question"""
    question_id: str
    response_text: str
    response_duration_seconds: int
    sentiment_score: float  # -1 to 1
    confidence_score: float  # 0 to 1
    detected_red_flags: List[str] = field(default_factory=list)
    detected_green_flags: List[str] = field(default_factory=list)


@dataclass
class InterviewSession:
    """Complete interview session"""
    session_id: str
    candidate_id: str
    candidate_name: str
    job_id: str
    job_title: str
    scheduled_time: str
    video_platform: str  # zoom, teams, meet
    meeting_url: str
    status: str  # scheduled, in_progress, completed, no_show
    questions: List[InterviewQuestion] = field(default_factory=list)
    responses: List[InterviewResponse] = field(default_factory=list)
    overall_score: float = 0.0
    recommendation: str = ""
    notes: str = ""
    transcript: str = ""


class VideoInterviewerAgent:
    """
    Agent that conducts video screening interviews

    Capabilities:
    - Schedule video meetings
    - Join calls automatically
    - Ask screening questions
    - Analyze responses in real-time
    - Detect red flags (inconsistencies, job hopping, attitude issues)
    - Provide hiring recommendation
    """

    def __init__(self):
        self.lm_config = Config.get_lmstudio_config()
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the video interviewer agent"""

        @tool
        def schedule_video_interview(
            candidate_email: str,
            candidate_name: str,
            job_title: str,
            duration_minutes: int = 30
        ) -> str:
            """
            Schedule a video screening interview

            Returns meeting URL and details
            """
            # TODO: Actual integration with Zoom/Teams API
            # For now, return mock data

            scheduled_time = (datetime.now() + timedelta(days=1)).isoformat()
            meeting_url = f"https://zoom.us/j/mock-{candidate_name.replace(' ', '')}"

            session = InterviewSession(
                session_id=f"interview_{datetime.now().timestamp()}",
                candidate_id="",
                candidate_name=candidate_name,
                job_id="",
                job_title=job_title,
                scheduled_time=scheduled_time,
                video_platform="zoom",
                meeting_url=meeting_url,
                status="scheduled"
            )

            return json.dumps({
                "meeting_url": meeting_url,
                "scheduled_time": scheduled_time,
                "duration_minutes": duration_minutes,
                "calendar_invite": "Would be sent via email integration",
                "reminder": "Automated reminder 1 hour before"
            }, indent=2)

        @tool
        def generate_screening_questions(
            job_title: str,
            job_description: str,
            focus_areas: List[str]
        ) -> str:
            """
            Generate tailored screening questions for the role

            Args:
                job_title: Role being hired for
                job_description: Full JD
                focus_areas: Key skills/attributes to assess
            """
            # Standard question templates by category
            questions = []

            # Always ask basic questions
            questions.extend([
                InterviewQuestion(
                    question_id="intro_1",
                    question_text="Tell me about your current role and what you're looking for in your next opportunity.",
                    question_type="behavioral",
                    expected_response_time_seconds=90
                ),
                InterviewQuestion(
                    question_id="motivation_1",
                    question_text=f"What interests you about this {job_title} position?",
                    question_type="culture_fit",
                    expected_response_time_seconds=60
                ),
            ])

            # Technical questions based on job
            if "engineer" in job_title.lower() or "developer" in job_title.lower():
                questions.append(InterviewQuestion(
                    question_id="tech_1",
                    question_text="Walk me through a recent technical challenge you faced and how you solved it.",
                    question_type="technical",
                    expected_response_time_seconds=120,
                    follow_up_questions=[
                        "What would you do differently now?",
                        "How did you decide on that approach?"
                    ]
                ))

            # Red flag detection questions
            questions.extend([
                InterviewQuestion(
                    question_id="redflag_1",
                    question_text="I notice you've had X jobs in Y years. Can you walk me through your career progression?",
                    question_type="red_flag_detection",
                    expected_response_time_seconds=90,
                    red_flags=[
                        "defensive tone",
                        "blames previous employers",
                        "vague or inconsistent answers"
                    ]
                ),
                InterviewQuestion(
                    question_id="availability_1",
                    question_text="What's your current notice period and ideal start date?",
                    question_type="behavioral",
                    expected_response_time_seconds=30
                ),
            ])

            return json.dumps([
                {
                    "question_id": q.question_id,
                    "question_text": q.question_text,
                    "question_type": q.question_type
                }
                for q in questions
            ], indent=2)

        @tool
        def analyze_interview_response(
            question_text: str,
            response_text: str,
            response_duration_seconds: int
        ) -> str:
            """
            Analyze a candidate's interview response

            Detects:
            - Red flags (defensiveness, inconsistency, negativity)
            - Green flags (specific examples, enthusiasm, preparation)
            - Response quality
            """
            # TODO: Use action model trained on past interviews
            # For now, use LLM to analyze

            analysis_prompt = f"""
Analyze this interview response:

Question: {question_text}
Candidate Response: {response_text}
Duration: {response_duration_seconds} seconds

Provide analysis in JSON format:
{{
    "response_quality": 1-10,
    "red_flags": ["list", "of", "concerns"],
    "green_flags": ["list", "of", "positive", "signals"],
    "key_insights": "summary",
    "follow_up_needed": true/false,
    "follow_up_question": "if needed"
}}
"""

            # Mock analysis (would use actual LLM/action model)
            return json.dumps({
                "response_quality": 7,
                "red_flags": [],
                "green_flags": ["specific examples", "enthusiasm for role"],
                "key_insights": "Candidate shows genuine interest and has relevant experience",
                "follow_up_needed": False,
                "follow_up_question": None
            }, indent=2)

        @tool
        def generate_interview_recommendation(
            overall_score: float,
            red_flags: List[str],
            green_flags: List[str],
            transcript_summary: str
        ) -> str:
            """
            Generate final interview recommendation

            Returns: Recommend, Maybe, Not Recommended
            """
            if overall_score >= 7.5 and len(red_flags) == 0:
                recommendation = "RECOMMEND"
                reasoning = "Strong candidate with no red flags. Proceed to client interview."

            elif overall_score >= 6.0 and len(red_flags) <= 1:
                recommendation = "MAYBE"
                reasoning = "Decent candidate but has some concerns. Discuss with recruiter before proceeding."

            else:
                recommendation = "NOT RECOMMENDED"
                reasoning = "Candidate does not meet requirements or has multiple red flags."

            return json.dumps({
                "recommendation": recommendation,
                "confidence": 0.85,
                "reasoning": reasoning,
                "next_steps": {
                    "RECOMMEND": "Send to client for technical interview",
                    "MAYBE": "Recruiter review required",
                    "NOT RECOMMENDED": "Send rejection email with feedback"
                }[recommendation],
                "summary": transcript_summary
            }, indent=2)

        agent = Agent(
            name="Video Interviewer",
            role="Automated screening interview conductor and analyzer",
            model=OpenAIChat(
                id=self.lm_config["model"],
                api_key=self.lm_config["api_key"],
                base_url=self.lm_config["base_url"],
                http_client=Config.get_http_client()
            ),
            tools=[
                schedule_video_interview,
                generate_screening_questions,
                analyze_interview_response,
                generate_interview_recommendation
            ],
            instructions=[
                "You are an expert technical recruiter conducting video screening interviews.",
                "",
                "Your role:",
                "1. Schedule video interviews with candidates",
                "2. Generate appropriate screening questions based on the role",
                "3. Conduct interviews following a structured approach",
                "4. Analyze responses for quality, red flags, and green flags",
                "5. Provide hiring recommendations with clear reasoning",
                "",
                "Interview best practices:",
                "- Create a comfortable environment (start with small talk)",
                "- Ask open-ended questions that require specific examples",
                "- Listen for STAR responses (Situation, Task, Action, Result)",
                "- Detect red flags: Negativity about past employers, vague answers, inconsistencies",
                "- Detect green flags: Preparation, specific examples, enthusiasm, cultural fit",
                "",
                "Red flags to watch for:",
                "- Job hopping without clear progression",
                "- Blaming previous employers or colleagues",
                "- Unable to provide specific technical examples",
                "- Defensive or aggressive tone",
                "- Inconsistent information (dates, responsibilities)",
                "- Unprofessional behavior (late to call, unprepared)",
                "",
                "Green flags to look for:",
                "- Clear career progression and learning",
                "- Specific, detailed examples of accomplishments",
                "- Asks thoughtful questions about the role",
                "- Research on the company",
                "- Positive attitude and communication skills",
                "",
                "After the interview:",
                "- Provide a clear recommendation (Recommend, Maybe, Not Recommended)",
                "- Include specific evidence from the interview",
                "- Suggest next steps",
                "- Flag any critical concerns immediately"
            ],
            markdown=True
        )

        return agent

    def conduct_interview(
        self,
        candidate_name: str,
        candidate_resume: str,
        job_title: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Conduct a complete screening interview

        Args:
            candidate_name: Candidate's name
            candidate_resume: Resume text
            job_title: Position being hired for
            job_description: Full job description

        Returns:
            Interview results with recommendation
        """
        interview_prompt = f"""
Conduct a screening interview for this candidate:

Candidate: {candidate_name}
Position: {job_title}

Resume Summary:
{candidate_resume[:500]}...

Job Description:
{job_description[:500]}...

Steps:
1. Generate appropriate screening questions for this role
2. Simulate the interview (you can create realistic responses based on the resume)
3. Analyze each response for quality and flags
4. Provide final recommendation

Provide your analysis in JSON format with:
- questions_asked
- response_analysis
- overall_score (1-10)
- red_flags
- green_flags
- recommendation (RECOMMEND/MAYBE/NOT RECOMMENDED)
- reasoning
"""

        response = self.agent.run(interview_prompt)

        return {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "interview_completed": True,
            "agent_analysis": response.content
        }


# Speech-to-text integration (stub for actual implementation)
class SpeechToTextService:
    """
    Converts speech to text during video interviews

    Integrations:
    - OpenAI Whisper (local or API)
    - Google Speech-to-Text
    - Azure Speech Services
    """

    def __init__(self, service: str = "whisper"):
        self.service = service

    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio to text

        Args:
            audio_file_path: Path to audio file

        Returns:
            Transcribed text
        """
        # TODO: Implement actual speech-to-text
        # For Whisper: import whisper; model = whisper.load_model("base"); result = model.transcribe(audio_file_path)

        return "Mock transcription: Candidate provided detailed examples of their experience..."

    def transcribe_realtime(self, audio_stream) -> str:
        """
        Real-time transcription during video call

        Used for live interview analysis
        """
        # TODO: Implement streaming transcription
        return "Real-time transcription..."


# Video platform integration (stub)
class VideoPlatformIntegration:
    """
    Integration with video platforms for automated interviews

    Platforms:
    - Zoom
    - Microsoft Teams
    - Google Meet
    """

    def __init__(self, platform: str = "zoom"):
        self.platform = platform

    def create_meeting(
        self,
        title: str,
        duration_minutes: int,
        scheduled_time: datetime
    ) -> Dict[str, Any]:
        """
        Create a video meeting

        Returns:
            Meeting URL and details
        """
        # TODO: Actual Zoom API integration
        # from zoom import ZoomClient; client = ZoomClient(api_key, api_secret)

        return {
            "meeting_url": f"https://{self.platform}.us/j/mock-meeting",
            "meeting_id": "123456789",
            "password": "abc123",
            "scheduled_time": scheduled_time.isoformat()
        }

    def join_meeting(self, meeting_url: str):
        """
        Bot joins meeting to conduct interview

        This would use a video bot service
        """
        # TODO: Use service like Recall.ai or build custom bot
        pass

    def record_meeting(self, meeting_id: str):
        """Start recording the meeting"""
        pass

    def end_meeting(self, meeting_id: str):
        """End the meeting"""
        pass


if __name__ == "__main__":
    # Demo
    from rich.console import Console
    console = Console()

    console.print("\n[bold cyan]Video Interviewer Agent Demo[/bold cyan]\n")

    interviewer = VideoInterviewerAgent()

    console.print("[yellow]Conducting screening interview...[/yellow]\n")

    result = interviewer.conduct_interview(
        candidate_name="John Smith",
        candidate_resume="""
        Senior Software Engineer with 8 years experience.
        Currently at TechCorp building Python microservices.
        Skills: Python, Django, AWS, PostgreSQL, Docker.
        Led team of 4 engineers, migrated monolith to microservices.
        """,
        job_title="Senior Python Developer",
        job_description="""
        We're looking for a Senior Python Developer to join our backend team.
        Requirements: 5+ years Python, Django/Flask, AWS, microservices architecture.
        """
    )

    console.print("[green]Interview Results:[/green]")
    console.print(json.dumps(result, indent=2))
