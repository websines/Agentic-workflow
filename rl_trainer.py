"""
Reinforcement Learning Training System
Trains the Supervisor, workflows, and agent behaviors

What gets trained:
1. Supervisor's decision-making (which agents for which tasks)
2. Workflow structure (order of steps, agent selection)
3. Agent prompts/instructions (how they approach tasks)
4. Eventually: Small action models
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import numpy as np
from collections import deque

from models import Run, RunStatus, Step, Feedback
from storage import WorkflowStorage


@dataclass
class State:
    """
    State representation for RL

    Represents the current situation when making a decision
    """
    task_type: str
    task_description: str
    available_agents: List[str]
    agent_performance_history: Dict[str, float]  # agent_name -> success_rate
    workflow_step: int
    context: Dict[str, Any]

    def to_vector(self) -> np.ndarray:
        """Convert state to vector for neural network (future)"""
        # TODO: Implement proper state encoding
        # For now, return placeholder
        return np.zeros(128)


@dataclass
class Action:
    """
    Action taken by the Supervisor

    Represents a decision made during workflow execution
    """
    agent_selected: str
    task_assigned: str
    parameters: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "agent_selected": self.agent_selected,
            "task_assigned": self.task_assigned,
            "parameters": self.parameters,
            "timestamp": self.timestamp
        }


@dataclass
class Experience:
    """
    Single experience tuple for RL: (state, action, reward, next_state)

    This is what we learn from
    """
    state: State
    action: Action
    reward: float
    next_state: Optional[State]
    done: bool
    run_id: str

    def to_dict(self) -> dict:
        return {
            "state": {
                "task_type": self.state.task_type,
                "workflow_step": self.state.workflow_step,
                "available_agents": self.state.available_agents,
            },
            "action": self.action.to_dict(),
            "reward": self.reward,
            "done": self.done,
            "run_id": self.run_id
        }


class RewardCalculator:
    """
    Calculates rewards for RL training

    Reward signal is crucial - it determines what the system learns to optimize
    """

    def __init__(self):
        # Reward weights - these determine what we optimize for
        self.weights = {
            "success": 10.0,          # Completing successfully is most important
            "user_satisfaction": 5.0,  # User feedback matters
            "speed": 2.0,             # Faster is better
            "cost": -1.0,             # Fewer LLM calls = lower cost
            "quality": 3.0,           # Quality of output
        }

    def calculate_reward(self, run: Run, feedback: Optional[Feedback] = None) -> float:
        """
        Calculate total reward for a run

        Components:
        1. Success/failure (binary)
        2. User satisfaction (from feedback)
        3. Speed (duration)
        4. Cost (number of LLM calls)
        5. Quality (from feedback rating)
        """
        reward = 0.0

        # 1. Success reward
        if run.status == RunStatus.COMPLETED:
            reward += self.weights["success"]
        elif run.status == RunStatus.FAILED:
            reward -= self.weights["success"]

        # 2. User satisfaction (from feedback)
        if feedback:
            if feedback.rating:
                # Rating is 0.0 to 1.0, scale to reward
                satisfaction = (feedback.rating - 0.5) * 2  # Scale to -1 to 1
                reward += satisfaction * self.weights["user_satisfaction"]

        # 3. Speed reward (normalize by baseline)
        if run.duration_ms:
            # Assume 5000ms is baseline, faster is better
            baseline_duration = 5000
            speed_factor = max(0, 1 - (run.duration_ms / baseline_duration))
            reward += speed_factor * self.weights["speed"]

        # 4. Cost penalty (number of steps = number of LLM calls)
        num_steps = len(run.steps)
        # Penalize for too many steps
        if num_steps > 5:
            reward += (5 - num_steps) * abs(self.weights["cost"])

        # 5. Quality (from feedback)
        if feedback and feedback.rating:
            quality = feedback.rating  # 0.0 to 1.0
            reward += quality * self.weights["quality"]

        return reward

    def calculate_step_reward(self, step: Step, step_success: bool) -> float:
        """
        Calculate reward for a single step

        Used for intermediate rewards during workflow execution
        """
        reward = 0.0

        # Success of the step
        if step_success:
            reward += 1.0
        else:
            reward -= 1.0

        # Speed of the step
        if step.duration_ms:
            # Assume 1000ms is baseline for a step
            baseline = 1000
            speed_factor = max(0, 1 - (step.duration_ms / baseline))
            reward += speed_factor * 0.5

        return reward


class ExperienceBuffer:
    """
    Replay buffer for storing and sampling experiences

    We learn from past experiences by replaying them during training
    """

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer: deque = deque(maxlen=max_size)
        self.successful_buffer: deque = deque(maxlen=max_size // 2)
        self.failed_buffer: deque = deque(maxlen=max_size // 2)

    def add(self, experience: Experience):
        """Add an experience to the buffer"""
        self.buffer.append(experience)

        # Also add to success/fail specific buffers
        if experience.reward > 0:
            self.successful_buffer.append(experience)
        else:
            self.failed_buffer.append(experience)

    def sample(self, batch_size: int, prioritize_successful: bool = True) -> List[Experience]:
        """
        Sample a batch of experiences

        If prioritize_successful=True, oversample successful experiences
        This helps the system learn what works
        """
        if len(self.buffer) < batch_size:
            return list(self.buffer)

        if prioritize_successful and len(self.successful_buffer) > 0:
            # Sample 70% from successful, 30% from failed
            n_success = int(batch_size * 0.7)
            n_fail = batch_size - n_success

            success_samples = list(np.random.choice(
                list(self.successful_buffer),
                size=min(n_success, len(self.successful_buffer)),
                replace=False
            ))

            fail_samples = list(np.random.choice(
                list(self.failed_buffer),
                size=min(n_fail, len(self.failed_buffer)),
                replace=False
            ))

            return success_samples + fail_samples
        else:
            # Random sampling
            indices = np.random.choice(len(self.buffer), size=batch_size, replace=False)
            return [self.buffer[i] for i in indices]

    def get_successful_experiences(self, task_type: str, limit: int = 10) -> List[Experience]:
        """Get successful experiences for a specific task type"""
        relevant = [
            exp for exp in self.successful_buffer
            if exp.state.task_type == task_type
        ]
        return relevant[-limit:]

    def size(self) -> int:
        return len(self.buffer)


class PolicyOptimizer:
    """
    Optimizes the Supervisor's decision-making policy

    For now, this uses prompt engineering + pattern matching
    Eventually, this will train a small neural network
    """

    def __init__(self, storage: WorkflowStorage):
        self.storage = storage
        self.reward_calculator = RewardCalculator()
        self.experience_buffer = ExperienceBuffer()

        # Current policy (represented as learned patterns)
        self.learned_patterns: Dict[str, List[Dict[str, Any]]] = {}

    def extract_experiences_from_run(self, run: Run, feedback: Optional[Feedback] = None) -> List[Experience]:
        """
        Extract RL experiences from a completed run

        Each step becomes an experience with its reward
        """
        experiences = []

        # Calculate overall reward
        overall_reward = self.reward_calculator.calculate_reward(run, feedback)

        # Extract state-action-reward for each step
        for i, step in enumerate(run.steps):
            if step.agent_name == "Supervisor":
                continue  # Skip supervisor's reasoning steps

            # Reconstruct state at this step
            state = State(
                task_type=run.workflow_type,
                task_description=run.user_input,
                available_agents=[],  # TODO: Track available agents
                agent_performance_history={},  # TODO: Get from storage
                workflow_step=i,
                context=step.metadata
            )

            # Extract action
            action = Action(
                agent_selected=step.agent_name,
                task_assigned=str(step.input_data),
                parameters={},
                timestamp=step.timestamp
            )

            # Calculate step reward
            step_success = step.output_data is not None and "error" not in str(step.output_data).lower()
            step_reward = self.reward_calculator.calculate_step_reward(step, step_success)

            # Add bonus from overall success
            step_reward += overall_reward / len(run.steps)

            # Next state
            next_state = None
            if i < len(run.steps) - 1:
                next_state = State(
                    task_type=run.workflow_type,
                    task_description=run.user_input,
                    available_agents=[],
                    agent_performance_history={},
                    workflow_step=i + 1,
                    context={}
                )

            experience = Experience(
                state=state,
                action=action,
                reward=step_reward,
                next_state=next_state,
                done=(i == len(run.steps) - 1),
                run_id=run.run_id
            )

            experiences.append(experience)

        return experiences

    def train_from_experiences(self, batch_size: int = 32, iterations: int = 10):
        """
        Train the policy from accumulated experiences

        For now: Extract patterns from successful experiences
        Future: Train neural network policy
        """
        print(f"\n🧠 Training policy from {self.experience_buffer.size()} experiences...")

        for iteration in range(iterations):
            # Sample batch
            batch = self.experience_buffer.sample(batch_size, prioritize_successful=True)

            if not batch:
                print("No experiences to learn from yet")
                return

            # Extract patterns from successful experiences
            self._extract_patterns(batch)

        print(f"✓ Training complete. Learned {len(self.learned_patterns)} patterns")

    def _extract_patterns(self, experiences: List[Experience]):
        """
        Extract successful patterns from experiences

        Patterns like:
        - "For content_creation tasks, use Research → Writer → Analyst"
        - "Agent X works well for task type Y"
        - "When task contains 'analyze', use Analyst agent"
        """
        for exp in experiences:
            if exp.reward > 0:  # Only learn from successful experiences
                task_type = exp.state.task_type

                if task_type not in self.learned_patterns:
                    self.learned_patterns[task_type] = []

                pattern = {
                    "agent": exp.action.agent_selected,
                    "step": exp.state.workflow_step,
                    "reward": exp.reward,
                    "task_keywords": self._extract_keywords(exp.state.task_description)
                }

                self.learned_patterns[task_type].append(pattern)

        # Keep only top patterns (by reward)
        for task_type in self.learned_patterns:
            patterns = self.learned_patterns[task_type]
            # Sort by reward, keep top 20
            patterns.sort(key=lambda x: x["reward"], reverse=True)
            self.learned_patterns[task_type] = patterns[:20]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from task description"""
        # Simple keyword extraction
        keywords = ["research", "write", "analyze", "create", "review", "data", "content"]
        return [kw for kw in keywords if kw in text.lower()]

    def get_recommended_agent(self, task_type: str, task_description: str, step: int) -> Optional[str]:
        """
        Get recommended agent based on learned patterns

        This is how the learned policy is used
        """
        if task_type not in self.learned_patterns:
            return None

        patterns = self.learned_patterns[task_type]

        # Find patterns for this step
        step_patterns = [p for p in patterns if p["step"] == step]

        if not step_patterns:
            return None

        # Return agent from highest reward pattern
        return step_patterns[0]["agent"]

    def save_policy(self, path: str):
        """Save learned policy to disk"""
        with open(path, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)

    def load_policy(self, path: str):
        """Load learned policy from disk"""
        try:
            with open(path, 'r') as f:
                self.learned_patterns = json.load(f)
        except FileNotFoundError:
            pass


class PromptEvolver:
    """
    Evolves agent prompts/instructions based on performance

    This is a form of prompt optimization through RL
    """

    def __init__(self):
        self.prompt_versions: Dict[str, List[Dict[str, Any]]] = {}

    def evolve_prompt(self, agent_name: str, current_instructions: List[str],
                     performance_metrics: Dict[str, float]) -> List[str]:
        """
        Evolve an agent's instructions based on performance

        Uses performance data to modify prompts
        """
        success_rate = performance_metrics.get("success_rate", 0.5)

        # If performance is good, keep instructions
        if success_rate > 0.8:
            return current_instructions

        # If performance is poor, try mutations
        new_instructions = current_instructions.copy()

        # Add specific improvements based on metrics
        if success_rate < 0.5:
            new_instructions.append("Double-check your work before responding")
            new_instructions.append("If unsure, ask for clarification")

        if performance_metrics.get("avg_duration_ms", 0) > 3000:
            new_instructions.append("Be concise and efficient")

        return new_instructions

    def track_version(self, agent_name: str, version: int, instructions: List[str],
                     metrics: Dict[str, float]):
        """Track a prompt version and its performance"""
        if agent_name not in self.prompt_versions:
            self.prompt_versions[agent_name] = []

        self.prompt_versions[agent_name].append({
            "version": version,
            "instructions": instructions,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_best_prompt(self, agent_name: str) -> Optional[List[str]]:
        """Get the best performing prompt for an agent"""
        if agent_name not in self.prompt_versions:
            return None

        versions = self.prompt_versions[agent_name]
        if not versions:
            return None

        # Find version with highest success rate
        best = max(versions, key=lambda v: v["metrics"].get("success_rate", 0))
        return best["instructions"]
