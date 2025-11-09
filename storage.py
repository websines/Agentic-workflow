"""
Git-style Storage Layer for Agentic Workflow
Handles persistence of runs, steps, feedback, and agent versions
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import Run, Step, Feedback, Workflow, ToolCall, RunStatus


class WorkflowStorage:
    """Git-style storage for workflow data"""

    def __init__(self, base_path: str = "./workflow_db"):
        self.base_path = Path(base_path)
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories"""
        (self.base_path / "runs").mkdir(parents=True, exist_ok=True)
        (self.base_path / "steps").mkdir(parents=True, exist_ok=True)
        (self.base_path / "feedback").mkdir(parents=True, exist_ok=True)
        (self.base_path / "workflows").mkdir(parents=True, exist_ok=True)
        (self.base_path / "agents").mkdir(parents=True, exist_ok=True)
        (self.base_path / "models").mkdir(parents=True, exist_ok=True)

    # ==================== Run Storage ====================

    def save_run(self, run: Run) -> str:
        """Save a run to storage (like git commit)"""
        # Organize by date
        date_str = datetime.fromisoformat(run.timestamp).strftime("%Y-%m-%d")
        date_dir = self.base_path / "runs" / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Save run
        run_file = date_dir / f"run_{run.run_id}.json"
        with open(run_file, 'w') as f:
            json.dump(run.to_dict(), f, indent=2)

        # Save steps separately for better organization
        self._save_steps(run)

        return str(run_file)

    def _save_steps(self, run: Run):
        """Save steps for a run"""
        if not run.steps:
            return

        steps_dir = self.base_path / "steps" / run.run_id
        steps_dir.mkdir(parents=True, exist_ok=True)

        for i, step in enumerate(run.steps):
            step_file = steps_dir / f"step_{i:03d}_{step.step_id}.json"
            with open(step_file, 'w') as f:
                json.dump(step.to_dict(), f, indent=2)

    def load_run(self, run_id: str) -> Optional[Run]:
        """Load a run by ID"""
        # Search through date directories
        runs_dir = self.base_path / "runs"
        for date_dir in runs_dir.iterdir():
            if not date_dir.is_dir():
                continue

            run_file = date_dir / f"run_{run_id}.json"
            if run_file.exists():
                with open(run_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct Run object
                    run = Run(
                        run_id=data['run_id'],
                        timestamp=data['timestamp'],
                        workflow_type=data['workflow_type'],
                        user_input=data['user_input'],
                        parent_run_id=data.get('parent_run_id'),
                        status=RunStatus(data['status']),
                        result=data.get('result'),
                        error=data.get('error'),
                        metadata=data.get('metadata', {}),
                        duration_ms=data.get('duration_ms'),
                        completed_at=data.get('completed_at')
                    )
                    # Load steps
                    run.steps = self._load_steps(run_id)
                    return run

        return None

    def _load_steps(self, run_id: str) -> List[Step]:
        """Load steps for a run"""
        steps_dir = self.base_path / "steps" / run_id
        if not steps_dir.exists():
            return []

        steps = []
        for step_file in sorted(steps_dir.iterdir()):
            if step_file.suffix == '.json':
                with open(step_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct Step object
                    from models import ActionType
                    step = Step(
                        step_id=data['step_id'],
                        run_id=data['run_id'],
                        agent_name=data['agent_name'],
                        action_type=ActionType(data['action_type']),
                        input_data=data.get('input_data'),
                        output_data=data.get('output_data'),
                        reasoning=data.get('reasoning', ''),
                        timestamp=data['timestamp'],
                        duration_ms=data.get('duration_ms'),
                        metadata=data.get('metadata', {})
                    )
                    steps.append(step)

        return steps

    def list_runs(self, limit: int = 100, status: Optional[RunStatus] = None) -> List[Run]:
        """List recent runs"""
        runs = []
        runs_dir = self.base_path / "runs"

        # Get all run files sorted by date (newest first)
        run_files = []
        for date_dir in sorted(runs_dir.iterdir(), reverse=True):
            if not date_dir.is_dir():
                continue
            for run_file in sorted(date_dir.iterdir(), reverse=True):
                if run_file.suffix == '.json':
                    run_files.append(run_file)

        # Load runs
        for run_file in run_files[:limit]:
            run_id = run_file.stem.replace('run_', '')
            run = self.load_run(run_id)
            if run and (status is None or run.status == status):
                runs.append(run)

        return runs

    # ==================== Feedback Storage ====================

    def save_feedback(self, feedback: Feedback) -> str:
        """Save feedback for a run"""
        feedback_file = self.base_path / "feedback" / f"{feedback.run_id}_feedback.json"

        # Load existing feedback if any
        existing = []
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                existing = json.load(f)

        # Append new feedback
        existing.append(feedback.to_dict())

        # Save
        with open(feedback_file, 'w') as f:
            json.dump(existing, f, indent=2)

        return str(feedback_file)

    def load_feedback(self, run_id: str) -> List[Feedback]:
        """Load all feedback for a run"""
        feedback_file = self.base_path / "feedback" / f"{run_id}_feedback.json"

        if not feedback_file.exists():
            return []

        with open(feedback_file, 'r') as f:
            data = json.load(f)
            return [Feedback(**item) for item in data]

    # ==================== Workflow Storage ====================

    def save_workflow(self, workflow: Workflow) -> str:
        """Save a workflow template"""
        workflow_file = self.base_path / "workflows" / f"{workflow.name}.json"

        with open(workflow_file, 'w') as f:
            json.dump(workflow.to_dict(), f, indent=2)

        return str(workflow_file)

    def load_workflow(self, name: str) -> Optional[Workflow]:
        """Load a workflow by name"""
        workflow_file = self.base_path / "workflows" / f"{name}.json"

        if not workflow_file.exists():
            return None

        with open(workflow_file, 'r') as f:
            data = json.load(f)
            return Workflow(**data)

    def list_workflows(self) -> List[str]:
        """List all available workflows"""
        workflows_dir = self.base_path / "workflows"
        return [f.stem for f in workflows_dir.iterdir() if f.suffix == '.json']

    # ==================== Agent Versioning (For Evolution) ====================

    def save_agent_version(self, agent_name: str, version: int, config: Dict[str, Any], metrics: Dict[str, Any]):
        """Save an agent version (for evolutionary tracking)"""
        agent_dir = self.base_path / "agents" / agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)

        version_file = agent_dir / f"v{version}.json"

        data = {
            "agent_name": agent_name,
            "version": version,
            "config": config,
            "metrics": metrics,
            "created_at": datetime.utcnow().isoformat(),
        }

        with open(version_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_agent_versions(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all versions of an agent (for comparing evolution)"""
        agent_dir = self.base_path / "agents" / agent_name

        if not agent_dir.exists():
            return []

        versions = []
        for version_file in sorted(agent_dir.iterdir()):
            if version_file.suffix == '.json':
                with open(version_file, 'r') as f:
                    versions.append(json.load(f))

        return sorted(versions, key=lambda x: x['version'])

    def get_best_agent_version(self, agent_name: str, metric: str = "success_rate") -> Optional[Dict[str, Any]]:
        """Get the best performing version of an agent"""
        versions = self.get_agent_versions(agent_name)

        if not versions:
            return None

        # Sort by metric
        return max(versions, key=lambda x: x.get('metrics', {}).get(metric, 0))

    # ==================== Analytics ====================

    def get_run_statistics(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about runs"""
        runs = self.list_runs(limit=1000)

        if workflow_type:
            runs = [r for r in runs if r.workflow_type == workflow_type]

        total = len(runs)
        completed = len([r for r in runs if r.status == RunStatus.COMPLETED])
        failed = len([r for r in runs if r.status == RunStatus.FAILED])

        avg_duration = None
        if runs:
            durations = [r.duration_ms for r in runs if r.duration_ms]
            if durations:
                avg_duration = sum(durations) / len(durations)

        return {
            "total_runs": total,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
            "avg_duration_ms": avg_duration,
        }
