"""
Data Models for Agentic Workflow System
Git-style logging for runs, steps, tool calls, and feedback
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class RunStatus(Enum):
    """Status of a workflow run"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActionType(Enum):
    """Type of action taken by an agent"""
    TOOL_CALL = "tool_call"
    DECISION = "decision"
    DELEGATION = "delegation"
    REASONING = "reasoning"
    RESPONSE = "response"


@dataclass
class ToolCall:
    """Detailed log of a tool call (like git operations)"""
    tool_call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step_id: str = ""
    tool_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    success: bool = True
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    duration_ms: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Step:
    """A single step in a workflow run (like operations within a commit)"""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = ""
    agent_name: str = ""
    action_type: ActionType = ActionType.DECISION
    input_data: Any = None
    output_data: Any = None
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    duration_ms: Optional[float] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['action_type'] = self.action_type.value
        return data


@dataclass
class Run:
    """A complete workflow run (like a git commit)"""
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    workflow_type: str = ""
    user_input: str = ""
    parent_run_id: Optional[str] = None
    status: RunStatus = RunStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    steps: List[Step] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    def add_step(self, step: Step):
        """Add a step to this run"""
        step.run_id = self.run_id
        self.steps.append(step)

    def complete(self, result: Any):
        """Mark run as completed"""
        self.status = RunStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow().isoformat()

    def fail(self, error: str):
        """Mark run as failed"""
        self.status = RunStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow().isoformat()


@dataclass
class Feedback:
    """Feedback for a run (for RL training)"""
    feedback_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    rating: Optional[float] = None  # 0.0 to 1.0
    corrections: List[str] = field(default_factory=list)
    human_feedback: Optional[str] = None
    implicit_metrics: Dict[str, Any] = field(default_factory=dict)  # success rate, time, etc.
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Workflow:
    """Definition of a workflow template"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    steps_template: List[Dict[str, Any]] = field(default_factory=list)
    required_agents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
