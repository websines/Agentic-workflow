"""
Supervisor Agent - Team Orchestration and Evolution
Manages specialized agents, orchestrates workflows, and drives evolution
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from config import Config
from storage import WorkflowStorage
from models import Run, RunStatus, Step, ActionType, Workflow
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_factory import AgentFactory, AgentSpecification


class SupervisorAgent:
    """
    Supervisor Agent - Team Orchestration and Evolution

    Responsibilities:
    - Break down tasks into subtasks
    - Assign work to specialized agents
    - Monitor progress and handle failures
    - Synthesize results
    - Track agent performance
    - Drive evolutionary improvements
    - Kill underperforming agents
    - Spawn new agents when needed
    """

    def __init__(self, storage: WorkflowStorage):
        self.storage = storage
        self.agent = self._create_agent()
        self.worker_agents: Dict[str, Agent] = {}
        self.agent_metrics: Dict[str, Dict[str, Any]] = {}
        self.agent_factory = AgentFactory()  # For auto-creating agents

    def _create_agent(self) -> Agent:
        """Create the Supervisor agent"""
        lm_config = Config.get_lmstudio_config()

        @tool
        def get_agent_performance(agent_name: str) -> str:
            """Get performance metrics for an agent"""
            if agent_name in self.agent_metrics:
                return json.dumps(self.agent_metrics[agent_name], indent=2)
            return f"No metrics available for {agent_name}"

        @tool
        def list_active_agents() -> str:
            """List all currently active agents"""
            agents = list(self.worker_agents.keys())
            return json.dumps(agents, indent=2)

        @tool
        def get_workflow_template(workflow_type: str) -> str:
            """Get the template for a workflow type"""
            workflow = self.storage.load_workflow(workflow_type)
            if workflow:
                return json.dumps(workflow.to_dict(), indent=2)
            return f"No template found for {workflow_type}"

        agent = Agent(
            name="Supervisor",
            role="Team orchestration, workflow execution, and evolutionary management",
            model=OpenAIChat(
                id=lm_config["model"],
                api_key=lm_config["api_key"],
                base_url=lm_config["base_url"]
            ),
            tools=[get_agent_performance, list_active_agents, get_workflow_template],
            instructions=[
                "You are the Supervisor - the orchestrator of the multi-agent system.",
                "",
                "Your responsibilities:",
                "1. ORCHESTRATION:",
                "   - Break down complex tasks into subtasks",
                "   - Assign subtasks to appropriate specialized agents",
                "   - Monitor progress and handle failures",
                "   - Synthesize results from multiple agents",
                "",
                "2. EVOLUTION:",
                "   - Track performance of each agent",
                "   - Identify underperforming agents",
                "   - Recommend agent modifications or replacements",
                "   - Optimize workflow efficiency",
                "",
                "3. ADAPTATION:",
                "   - Modify workflows based on performance",
                "   - Create new workflows when needed",
                "   - Learn from past runs",
                "",
                "You have the power to:",
                "- Delegate to specialized worker agents",
                "- Request agent performance data",
                "- Recommend agent lifecycle changes (create/modify/kill)",
                "",
                "Always think strategically about:",
                "- Which agents should handle which tasks",
                "- How to best combine agent outputs",
                "- How to improve the system over time",
                "",
                "Be efficient, strategic, and evolutionary.",
            ],
            markdown=True,
        )

        return agent

    def register_worker(self, name: str, agent: Agent) -> None:
        """Register a worker agent"""
        self.worker_agents[name] = agent
        if name not in self.agent_metrics:
            self.agent_metrics[name] = {
                "tasks_completed": 0,
                "tasks_failed": 0,
                "total_duration_ms": 0,
                "success_rate": 1.0,
                "avg_duration_ms": 0,
                "version": 1,
                "created_at": datetime.utcnow().isoformat(),
            }

    def execute_workflow(self, run: Run, workflow: Workflow) -> Run:
        """
        Execute a workflow with the team of agents

        Args:
            run: The run to execute
            workflow: The workflow template to follow

        Returns:
            Updated run with results
        """
        # Log Supervisor taking over
        supervisor_step = Step(
            run_id=run.run_id,
            agent_name="Supervisor",
            action_type=ActionType.REASONING,
            input_data={
                "workflow_type": workflow.name,
                "user_request": run.user_input
            },
            reasoning="Supervisor analyzing task and planning execution"
        )

        try:
            # Supervisor plans the execution
            planning_prompt = f"""
            Workflow Type: {workflow.name}
            User Request: {run.user_input}
            Available Agents: {list(self.worker_agents.keys())}

            Plan the execution:
            1. What subtasks are needed?
            2. Which agents should handle each subtask?
            3. In what order should they execute?
            4. How will you synthesize the results?

            Think step by step.
            """

            start_time = datetime.utcnow()
            planning_response = self.agent.run(planning_prompt)
            planning_duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            supervisor_step.output_data = planning_response.content
            supervisor_step.duration_ms = planning_duration
            run.add_step(supervisor_step)

            # Execute workflow steps
            results = {}
            for step_template in workflow.steps_template:
                agent_name = step_template.get("agent")
                task = step_template.get("task")

                if agent_name in self.worker_agents:
                    result = self._execute_agent_task(run, agent_name, task, results)
                    results[agent_name] = result

            # Supervisor synthesizes results
            synthesis_step = Step(
                run_id=run.run_id,
                agent_name="Supervisor",
                action_type=ActionType.DECISION,
                input_data=results,
                reasoning="Synthesizing results from all agents"
            )

            synthesis_prompt = f"""
            All agent results are in:
            {json.dumps(results, indent=2)}

            Synthesize these into a final result for the user's request:
            "{run.user_input}"

            Provide a coherent, complete response.
            """

            start_time = datetime.utcnow()
            synthesis_response = self.agent.run(synthesis_prompt)
            synthesis_duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            synthesis_step.output_data = synthesis_response.content
            synthesis_step.duration_ms = synthesis_duration
            run.add_step(synthesis_step)

            # Complete the run
            run.complete(synthesis_response.content)

            # Update metrics
            self._update_metrics(run)

            # Save final run
            self.storage.save_run(run)

            return run

        except Exception as e:
            run.fail(str(e))
            self.storage.save_run(run)
            raise

    def _execute_agent_task(self, run: Run, agent_name: str, task: str, context: Dict[str, Any]) -> str:
        """Execute a task with a specific agent"""
        agent = self.worker_agents[agent_name]

        # Log the delegation
        delegation_step = Step(
            run_id=run.run_id,
            agent_name="Supervisor",
            action_type=ActionType.DELEGATION,
            input_data={"agent": agent_name, "task": task},
            reasoning=f"Delegating task to {agent_name}"
        )
        run.add_step(delegation_step)

        # Execute
        task_step = Step(
            run_id=run.run_id,
            agent_name=agent_name,
            action_type=ActionType.TOOL_CALL,
            input_data={"task": task, "context": context},
        )

        try:
            # Format task with context
            formatted_task = task
            if context:
                formatted_task += f"\n\nContext from previous steps:\n{json.dumps(context, indent=2)}"

            start_time = datetime.utcnow()
            response = agent.run(formatted_task)
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            task_step.output_data = response.content
            task_step.duration_ms = duration
            task_step.reasoning = f"{agent_name} completed task successfully"

            # Update agent metrics
            self.agent_metrics[agent_name]["tasks_completed"] += 1
            self.agent_metrics[agent_name]["total_duration_ms"] += duration

            run.add_step(task_step)

            return response.content

        except Exception as e:
            task_step.output_data = f"Error: {str(e)}"
            task_step.reasoning = f"{agent_name} failed to complete task"

            # Update agent metrics
            self.agent_metrics[agent_name]["tasks_failed"] += 1

            run.add_step(task_step)

            raise

    def _update_metrics(self, run: Run):
        """Update agent performance metrics based on run"""
        for agent_name in self.agent_metrics:
            metrics = self.agent_metrics[agent_name]

            total_tasks = metrics["tasks_completed"] + metrics["tasks_failed"]
            if total_tasks > 0:
                metrics["success_rate"] = metrics["tasks_completed"] / total_tasks

            if metrics["tasks_completed"] > 0:
                metrics["avg_duration_ms"] = metrics["total_duration_ms"] / metrics["tasks_completed"]

    def evaluate_agents(self) -> Dict[str, Any]:
        """
        Evaluate all agents and recommend actions

        Returns:
            Dict with recommendations for agent lifecycle (kill/modify/create)
        """
        evaluation_prompt = f"""
        Current Agent Performance Metrics:
        {json.dumps(self.agent_metrics, indent=2)}

        Analyze each agent's performance and recommend:
        1. Which agents should be KEPT (performing well)
        2. Which agents should be MODIFIED (underperforming but salvageable)
        3. Which agents should be KILLED (consistently underperforming)
        4. What NEW agents might be needed

        Consider:
        - Success rate (should be > 0.7)
        - Average duration (should be reasonable)
        - Total tasks completed (more experience = more reliable)

        Respond in JSON format:
        {{
            "keep": ["agent1", "agent2"],
            "modify": [
                {{"agent": "agent3", "reason": "...", "suggestion": "..."}}
            ],
            "kill": [
                {{"agent": "agent4", "reason": "..."}}
            ],
            "create": [
                {{"name": "new_agent", "role": "...", "reason": "..."}}
            ]
        }}
        """

        response = self.agent.run(evaluation_prompt)

        try:
            recommendations = json.loads(response.content)
            return recommendations
        except:
            return {"keep": list(self.worker_agents.keys()), "modify": [], "kill": [], "create": []}

    def kill_agent(self, agent_name: str) -> None:
        """Kill (remove) an underperforming agent"""
        if agent_name in self.worker_agents:
            # Save final version
            metrics = self.agent_metrics.get(agent_name, {})
            self.storage.save_agent_version(
                agent_name,
                metrics.get("version", 1),
                {"status": "killed"},
                metrics
            )

            # Remove from active agents
            del self.worker_agents[agent_name]
            print(f"🪦 Agent '{agent_name}' has been terminated (poor performance)")

    def evolve_agent(self, agent_name: str, modification: str, improvements: Optional[List[str]] = None) -> None:
        """Evolve an agent based on feedback"""
        if agent_name in self.worker_agents:
            metrics = self.agent_metrics.get(agent_name, {})

            # Save old version
            old_version = metrics.get("version", 1)
            self.storage.save_agent_version(agent_name, old_version, {}, metrics)

            # Create evolved version using factory
            current_agent = self.worker_agents[agent_name]

            if improvements:
                evolved_agent = self.agent_factory.evolve_agent(current_agent, improvements)
                self.worker_agents[agent_name] = evolved_agent

            # Update version
            metrics["version"] = old_version + 1

            print(f"🧬 Agent '{agent_name}' evolved to v{metrics['version']}: {modification}")

    def auto_create_agent(self, task_description: str) -> Optional[str]:
        """
        Automatically create a new agent if needed for a task

        Returns:
            Name of created agent, or None if no agent was created
        """
        # Check if we need a new agent
        existing_agents = list(self.worker_agents.keys())

        spec = self.agent_factory.suggest_agent_for_task(task_description, existing_agents)

        if spec:
            # Create the agent
            new_agent = self.agent_factory.create_agent(spec)

            # Register it
            self.register_worker(spec.name, new_agent)

            print(f"✨ Auto-created new agent: {spec.name}")
            print(f"   Role: {spec.role}")

            return spec.name

        return None
