"""
Manager Agent - User-Facing Interface
Handles user interactions and delegates to Supervisor
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from typing import Dict, Any
import json

from config import Config
from storage import WorkflowStorage
from models import Run, RunStatus, Step, ActionType


class ManagerAgent:
    """
    Manager Agent - The user-facing interface

    Responsibilities:
    - Understand user requests
    - Select or create appropriate workflows
    - Delegate to Supervisor
    - Present results to user
    - Collect feedback
    """

    def __init__(self, storage: WorkflowStorage):
        self.storage = storage
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the Manager agent"""
        lm_config = Config.get_lmstudio_config()

        @tool
        def list_available_workflows() -> str:
            """List all available workflow types"""
            workflows = self.storage.list_workflows()
            return json.dumps(workflows, indent=2)

        @tool
        def get_workflow_stats(workflow_type: str) -> str:
            """Get performance statistics for a workflow type"""
            stats = self.storage.get_run_statistics(workflow_type)
            return json.dumps(stats, indent=2)

        agent = Agent(
            name="Manager",
            role="User-facing interface and workflow coordinator",
            model=OpenAIChat(
                id=lm_config["model"],
                api_key=lm_config["api_key"],
                base_url=lm_config["base_url"],
                http_client=Config.get_http_client()
            ),
            tools=[list_available_workflows, get_workflow_stats],
            instructions=[
                "You are the Manager - the user-facing interface of the agentic system.",
                "Your role is to:",
                "1. Understand user requests clearly",
                "2. Identify the appropriate workflow type (or create a new one)",
                "3. Explain what you'll do before delegating to the Supervisor",
                "4. Present results clearly to the user",
                "5. Ask for feedback to improve the system",
                "",
                "You coordinate with the Supervisor agent who handles the actual execution.",
                "Be professional, clear, and helpful.",
                "Always explain your reasoning to the user.",
            ],
            markdown=True,
        )

        return agent

    def handle_request(self, user_input: str, workflow_type: str = "general") -> Run:
        """
        Handle a user request

        Args:
            user_input: The user's request
            workflow_type: Type of workflow to use

        Returns:
            Run object with complete execution log
        """
        # Create a new run
        run = Run(
            workflow_type=workflow_type,
            user_input=user_input,
            status=RunStatus.RUNNING
        )

        # Save initial run
        self.storage.save_run(run)

        # Log Manager's analysis
        analysis_step = Step(
            run_id=run.run_id,
            agent_name="Manager",
            action_type=ActionType.REASONING,
            input_data=user_input,
            reasoning="Analyzing user request and determining workflow"
        )
        run.add_step(analysis_step)

        try:
            # Manager analyzes the request
            analysis_prompt = f"""
            User Request: {user_input}

            Analyze this request and determine:
            1. What is the user asking for?
            2. What workflow type would be best?
            3. What should the Supervisor focus on?

            Provide a clear analysis.
            """

            response = self.agent.run(analysis_prompt)

            analysis_step.output_data = response.content
            analysis_step.reasoning = "Request analyzed, ready to delegate to Supervisor"

            # Save updated run
            self.storage.save_run(run)

            return run

        except Exception as e:
            run.fail(str(e))
            self.storage.save_run(run)
            raise

    def present_result(self, run: Run) -> str:
        """Present the final result to the user"""
        if run.status == RunStatus.COMPLETED:
            presentation_prompt = f"""
            The workflow has completed successfully.

            User's Original Request: {run.user_input}
            Result: {run.result}

            Present this result to the user in a clear, professional manner.
            Highlight key points and ask if they need anything else.
            """

            response = self.agent.run(presentation_prompt)
            return response.content

        elif run.status == RunStatus.FAILED:
            return f"I apologize, but there was an error: {run.error}"

        else:
            return f"The workflow is still {run.status.value}..."

    def collect_feedback(self, run: Run, user_feedback: str) -> None:
        """Collect user feedback on a run"""
        from models import Feedback

        feedback = Feedback(
            run_id=run.run_id,
            human_feedback=user_feedback
        )

        # Ask agent to rate the run based on feedback
        rating_prompt = f"""
        User Request: {run.user_input}
        Result: {run.result}
        User Feedback: {user_feedback}

        Based on the feedback, rate the run from 0.0 to 1.0 (1.0 being perfect).
        Also suggest what corrections should be made.

        Respond in JSON format:
        {{
            "rating": 0.8,
            "corrections": ["suggestion 1", "suggestion 2"]
        }}
        """

        response = self.agent.run(rating_prompt)

        try:
            rating_data = json.loads(response.content)
            feedback.rating = rating_data.get("rating", 0.5)
            feedback.corrections = rating_data.get("corrections", [])
        except:
            feedback.rating = 0.5

        self.storage.save_feedback(feedback)
