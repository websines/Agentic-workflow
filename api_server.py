"""
FastAPI Server for Agentic Workflow System

Provides REST API for:
- Workflow execution
- Knowledge management
- Agent monitoring
- Event streaming
- RL training management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

from workflow_engine import WorkflowEngine
from domain_workflow_engine import DomainWorkflowEngine
from domain_config import DomainRegistry
from knowledge_center import KnowledgeCenter, KnowledgeManager
from event_bus import EventBus, Event, EventType
from storage import WorkflowStorage
from models import RunStatus

# Initialize FastAPI
app = FastAPI(
    title="Agentic Workflow API",
    description="Multi-agent workflow system with RL training and knowledge management",
    version="1.0.0"
)

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
workflow_engine = WorkflowEngine()
knowledge_center = KnowledgeCenter()
knowledge_manager = KnowledgeManager(knowledge_center)
event_bus = EventBus(enable_async=True)
storage = WorkflowStorage()

# WebSocket connections for real-time event streaming
websocket_connections: List[WebSocket] = []


# ==================== Pydantic Models ====================

class WorkflowRequest(BaseModel):
    """Request to execute a workflow"""
    user_input: str
    workflow_type: str = "general"
    domain: Optional[str] = None


class KnowledgeUpload(BaseModel):
    """Upload knowledge document"""
    title: str
    content: str
    doc_type: str  # policy, faq, process, guideline
    domain: str
    uploaded_by: str


class FeedbackSubmission(BaseModel):
    """User feedback on a workflow run"""
    run_id: str
    rating: int  # 1-5
    comments: Optional[str] = None
    user_satisfaction: float = 3.0  # 0-5


class DomainWorkflowRequest(BaseModel):
    """Request for domain-specific workflow"""
    domain: str
    user_input: str
    workflow_type: str


# ==================== Workflow Endpoints ====================

@app.post("/api/workflow/execute")
async def execute_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """
    Execute a workflow

    Examples:
    - General workflow: {"user_input": "Create blog outline", "workflow_type": "content_creation"}
    - Domain workflow: {"user_input": "Review contract", "workflow_type": "contract_review", "domain": "legal"}
    """
    try:
        # Emit event
        event_bus.publish(Event(
            event_type=EventType.WORKFLOW_STARTED,
            source="API",
            data={"user_input": request.user_input, "workflow_type": request.workflow_type}
        ))

        # Execute workflow (domain-specific or general)
        if request.domain:
            # Domain-specific workflow
            domain_config = DomainRegistry.get_domain(request.domain)
            if not domain_config:
                raise HTTPException(status_code=404, detail=f"Domain '{request.domain}' not found")

            domain_engine = DomainWorkflowEngine(domain_config)
            run = domain_engine.execute(request.user_input, request.workflow_type)
        else:
            # General workflow
            run = workflow_engine.execute(request.user_input, request.workflow_type)

        # Emit completion event
        event_bus.publish(Event(
            event_type=EventType.WORKFLOW_COMPLETED if run.status == RunStatus.COMPLETED else EventType.WORKFLOW_FAILED,
            source="API",
            data={"run_id": run.run_id, "status": run.status.value}
        ))

        return {
            "success": True,
            "run_id": run.run_id,
            "status": run.status.value,
            "result": run.result,
            "steps_count": len(run.steps)
        }

    except Exception as e:
        # Emit error event
        event_bus.publish(Event(
            event_type=EventType.SYSTEM_ERROR,
            source="API",
            data={"error": str(e)}
        ))

        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/status/{run_id}")
async def get_workflow_status(run_id: str):
    """Get status of a workflow run"""
    try:
        run = storage.load_run(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        return {
            "run_id": run.run_id,
            "status": run.status.value,
            "workflow_type": run.workflow_type,
            "result": run.result,
            "steps": [
                {
                    "agent": step.agent_name,
                    "action": step.action_type.value,
                    "reasoning": step.reasoning
                }
                for step in run.steps
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/history")
async def get_workflow_history(
    workflow_type: Optional[str] = None,
    limit: int = 50
):
    """Get workflow execution history"""
    try:
        runs = storage.get_recent_runs(workflow_type, limit)

        return {
            "total": len(runs),
            "runs": [
                {
                    "run_id": run.run_id,
                    "workflow_type": run.workflow_type,
                    "status": run.status.value,
                    "timestamp": run.timestamp,
                    "duration_ms": run.duration_ms
                }
                for run in runs
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Knowledge Management Endpoints ====================

@app.post("/api/knowledge/upload")
async def upload_knowledge(upload: KnowledgeUpload):
    """
    Upload knowledge document

    For lawyer: Upload contracts, policies, precedents
    For SMB: Upload FAQs, processes, guidelines
    """
    try:
        doc_id = knowledge_center.add_document(
            title=upload.title,
            content=upload.content,
            doc_type=upload.doc_type,
            domain=upload.domain,
            tags=[upload.doc_type, upload.domain],
            created_by=upload.uploaded_by
        )

        # Emit event
        event_bus.publish(Event(
            event_type=EventType.KNOWLEDGE_UPLOADED,
            source="API",
            data={"doc_id": doc_id, "domain": upload.domain}
        ))

        return {
            "success": True,
            "doc_id": doc_id,
            "message": f"Knowledge document '{upload.title}' uploaded successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge/search")
async def search_knowledge(
    query: str,
    domain: Optional[str] = None,
    doc_type: Optional[str] = None,
    limit: int = 5
):
    """Search the knowledge base"""
    try:
        results = knowledge_center.search(query, domain, doc_type, limit)

        # Emit event
        event_bus.publish(Event(
            event_type=EventType.KNOWLEDGE_SEARCHED,
            source="API",
            data={"query": query, "results_count": len(results)}
        ))

        return {
            "query": query,
            "results": [
                {
                    "doc_id": doc.doc_id,
                    "title": doc.title,
                    "content_preview": doc.content[:200],
                    "doc_type": doc.doc_type,
                    "domain": doc.domain,
                    "score": score
                }
                for doc, score in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        stats = knowledge_center.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Agent Management Endpoints ====================

@app.get("/api/agents/list")
async def list_agents():
    """List all active agents"""
    try:
        # Get agents from supervisor
        supervisor = workflow_engine.supervisor
        agents = list(supervisor.worker_agents.keys())

        return {
            "agents": [
                {
                    "name": name,
                    "metrics": supervisor.agent_metrics.get(name, {})
                }
                for name in agents
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/performance/{agent_name}")
async def get_agent_performance(agent_name: str):
    """Get performance metrics for an agent"""
    try:
        supervisor = workflow_engine.supervisor
        metrics = supervisor.agent_metrics.get(agent_name)

        if not metrics:
            raise HTTPException(status_code=404, detail="Agent not found")

        return {
            "agent_name": agent_name,
            "metrics": metrics
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== RL Training Endpoints ====================

@app.post("/api/rl/train")
async def trigger_rl_training(background_tasks: BackgroundTasks, collect_limit: int = 100):
    """Trigger RL training cycle"""
    try:
        # Run in background
        background_tasks.add_task(
            _run_rl_training,
            collect_limit
        )

        return {
            "success": True,
            "message": f"RL training started (collecting {collect_limit} experiences)"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _run_rl_training(collect_limit: int):
    """Background task for RL training"""
    try:
        # Emit start event
        event_bus.publish(Event(
            event_type=EventType.RL_TRAINING_STARTED,
            source="API",
            data={"collect_limit": collect_limit}
        ))

        # Run training
        workflow_engine.rl_system.run_full_training_cycle(collect_limit)

        # Emit completion event
        event_bus.publish(Event(
            event_type=EventType.RL_TRAINING_COMPLETED,
            source="API",
            data={"status": "completed"}
        ))

    except Exception as e:
        event_bus.publish(Event(
            event_type=EventType.SYSTEM_ERROR,
            source="RL Training",
            data={"error": str(e)}
        ))


@app.get("/api/rl/stats")
async def get_rl_stats():
    """Get RL training statistics"""
    try:
        rl_system = workflow_engine.rl_system

        return {
            "total_experiences": len(rl_system.experience_buffer.experiences),
            "policy_patterns": len(rl_system.policy_optimizer.policy),
            "supervisor_version": 1,  # TODO: Track versions
            "last_training": "N/A"  # TODO: Track last training time
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Feedback Endpoints ====================

@app.post("/api/feedback/submit")
async def submit_feedback(feedback: FeedbackSubmission):
    """Submit user feedback on a workflow run"""
    try:
        from models import Feedback

        feedback_obj = Feedback(
            run_id=feedback.run_id,
            rating=feedback.rating,
            comments=feedback.comments or "",
            user_satisfaction=feedback.user_satisfaction
        )

        storage.save_feedback(feedback_obj)

        return {
            "success": True,
            "message": "Feedback submitted successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Event Streaming (WebSocket) ====================

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """
    WebSocket endpoint for real-time event streaming

    Frontend can connect to this to receive live updates
    """
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()

    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


def broadcast_event_to_websockets(event: Event):
    """Broadcast event to all connected WebSocket clients"""
    for ws in websocket_connections:
        try:
            import asyncio
            asyncio.create_task(ws.send_json(event.to_dict()))
        except:
            pass


# Subscribe event bus to broadcast events
event_bus.subscribe(EventType.WORKFLOW_STARTED, broadcast_event_to_websockets)
event_bus.subscribe(EventType.WORKFLOW_COMPLETED, broadcast_event_to_websockets)
event_bus.subscribe(EventType.AGENT_COMPLETED, broadcast_event_to_websockets)


# ==================== System Status ====================

@app.get("/api/system/status")
async def get_system_status():
    """Get overall system status"""
    try:
        event_stats = event_bus.get_statistics()
        knowledge_stats = knowledge_center.get_statistics()

        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "workflow_engine": "active",
                "event_bus": "active",
                "knowledge_center": "active"
            },
            "statistics": {
                "events": event_stats,
                "knowledge": knowledge_stats
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/events")
async def get_event_history(
    event_type: Optional[str] = None,
    limit: int = 100
):
    """Get event history"""
    try:
        if event_type:
            event_type_enum = EventType(event_type)
            events = event_bus.get_event_history(event_type_enum, limit)
        else:
            events = event_bus.get_event_history(None, limit)

        return {
            "total": len(events),
            "events": [event.to_dict() for event in events]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*50)
    print("🚀 Agentic Workflow API Server")
    print("="*50)
    print("\nStarting server...")
    print("  API docs: http://localhost:8000/docs")
    print("  Health: http://localhost:8000/health")
    print("\n" + "="*50 + "\n")

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
