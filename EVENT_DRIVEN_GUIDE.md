# Event-Driven Architecture & Web UI Guide

## Overview

The system now includes:
- **Event Bus**: Asynchronous pub/sub pattern for agent coordination
- **FastAPI Backend**: REST API for workflow management
- **Web UI**: Browser-based interface for knowledge upload and monitoring
- **WebSocket Streaming**: Real-time event updates

## Architecture

```
┌─────────────┐
│   Web UI    │ (Browser)
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────┐
│  FastAPI    │ (Port 8000)
│   Server    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      Event Bus                  │
│  (Async Pub/Sub)                │
│                                 │
│  ┌──────────┐  ┌──────────┐   │
│  │ Manager  │  │Supervisor│   │
│  └──────────┘  └──────────┘   │
│                                 │
│  ┌──────────┐  ┌──────────┐   │
│  │ Agents   │  │Knowledge │   │
│  └──────────┘  └──────────┘   │
└─────────────────────────────────┘
       │
       ▼ (Optional)
┌─────────────────────┐
│ External Bridges    │
│ - Kafka             │
│ - RabbitMQ          │
│ - AWS EventBridge   │
└─────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
python api_server.py
```

The server starts on http://localhost:8000

### 3. Open the Web UI

Open `web_ui.html` in your browser or serve it:

```bash
python -m http.server 8080
```

Then navigate to: http://localhost:8080/web_ui.html

### 4. API Documentation

FastAPI provides automatic API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Using the Event Bus

### Standalone Event Bus Demo

```bash
python event_bus.py
```

### In Your Code

```python
from event_bus import EventBus, Event, EventType

# Create event bus
bus = EventBus(enable_async=True)

# Subscribe to events
def my_handler(event: Event):
    print(f"Received: {event.event_type.value}")

bus.subscribe(EventType.WORKFLOW_COMPLETED, my_handler)

# Publish events
bus.publish(Event(
    event_type=EventType.WORKFLOW_COMPLETED,
    source="MyComponent",
    data={"run_id": "123", "status": "success"}
))
```

## API Endpoints

### Workflow Management

**Execute Workflow**
```bash
POST /api/workflow/execute
{
  "user_input": "Review this contract",
  "workflow_type": "contract_review",
  "domain": "legal"
}
```

**Get Workflow Status**
```bash
GET /api/workflow/status/{run_id}
```

**Get Workflow History**
```bash
GET /api/workflow/history?workflow_type=legal&limit=50
```

### Knowledge Management

**Upload Knowledge**
```bash
POST /api/knowledge/upload
{
  "title": "Remote Work Policy",
  "content": "...",
  "doc_type": "policy",
  "domain": "hr",
  "uploaded_by": "HR Manager"
}
```

**Search Knowledge**
```bash
GET /api/knowledge/search?query=remote+work&domain=hr
```

**Knowledge Statistics**
```bash
GET /api/knowledge/stats
```

### Agent Management

**List Agents**
```bash
GET /api/agents/list
```

**Agent Performance**
```bash
GET /api/agents/performance/{agent_name}
```

### RL Training

**Trigger Training**
```bash
POST /api/rl/train?collect_limit=100
```

**RL Statistics**
```bash
GET /api/rl/stats
```

### Event Streaming

**WebSocket Connection**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Event:', data);
};
```

**Get Event History**
```bash
GET /api/system/events?event_type=workflow.completed&limit=100
```

### System Status

**Health Check**
```bash
GET /health
```

**System Status**
```bash
GET /api/system/status
```

## Use Cases

### 1. Lawyer - Document Management

**Upload Contract Template**
```bash
curl -X POST http://localhost:8000/api/knowledge/upload \
  -H "Content-Type: application/json" \
  -d '{
    "title": "FL Property Purchase Agreement",
    "content": "...",
    "doc_type": "policy",
    "domain": "legal",
    "uploaded_by": "Legal Team"
  }'
```

**Trigger Compliance Check**
```bash
curl -X POST http://localhost:8000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Review this contract for Miami property compliance",
    "workflow_type": "compliance_check",
    "domain": "legal"
  }'
```

**Monitor via Web UI**
- Upload documents through the Web UI
- Search company knowledge base
- View compliance check results in real-time
- Monitor agent performance

### 2. SMB (200 Employees) - Support Automation

**Upload Support FAQs**
```bash
curl -X POST http://localhost:8000/api/knowledge/upload \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Return Policy FAQ",
    "content": "...",
    "doc_type": "faq",
    "domain": "customer_support",
    "uploaded_by": "Support Manager"
  }'
```

**Auto-respond to Customer Inquiry**
```bash
curl -X POST http://localhost:8000/api/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Customer asking about return window",
    "workflow_type": "customer_support",
    "domain": "customer_support"
  }'
```

**Event-Driven Workflow**
```python
# When customer submits inquiry
bus.publish(Event(
    event_type=EventType.CUSTOMER_INQUIRY,
    source="SupportPortal",
    data={"inquiry": "How do I return?", "customer_id": "123"}
))

# Support agent automatically handles it
def handle_inquiry(event: Event):
    inquiry = event.data['inquiry']
    # Search knowledge base, generate response

bus.subscribe(EventType.CUSTOMER_INQUIRY, handle_inquiry)
```

### 3. Hospital - Real-Time Coordination

**Deadline Alert Handler**
```python
def deadline_alert(event: Event):
    task = event.data['task']
    deadline = event.data['deadline']
    # Trigger agent to notify relevant staff

bus.subscribe(EventType.DEADLINE_APPROACHING, deadline_alert)

# Surgery deadline approaching
bus.publish(Event(
    event_type=EventType.DEADLINE_APPROACHING,
    source="SchedulerAgent",
    data={
        "task": "Pre-op preparation for Patient #456",
        "deadline": "2024-01-15 08:00"
    }
))
```

## External Event Bridge Integration

### Kafka Integration (Future)

```python
from event_bus import KafkaEventBridge

# Create bridge
kafka_bridge = KafkaEventBridge(
    event_bus=bus,
    bootstrap_servers="localhost:9092"
)

# Forward events to Kafka
bus.subscribe(EventType.WORKFLOW_COMPLETED,
              lambda e: kafka_bridge.forward_to_external(e))
```

### AWS EventBridge (Future)

```python
from event_bus import AWSEventBridge

aws_bridge = AWSEventBridge(event_bus=bus)

# Forward high-priority events to AWS
bus.subscribe(EventType.SYSTEM_ERROR,
              lambda e: aws_bridge.forward_to_external(e))
```

## Event Types

The system emits these event types:

### Workflow Events
- `workflow.started`
- `workflow.completed`
- `workflow.failed`

### Agent Events
- `agent.created`
- `agent.assigned`
- `agent.completed`
- `agent.failed`

### Knowledge Events
- `knowledge.uploaded`
- `knowledge.updated`
- `knowledge.searched`

### Document Events (Lawyer Use Case)
- `document.uploaded`
- `document.reviewed`
- `compliance.check_started`
- `compliance.check_completed`

### Business Events (SMB Use Case)
- `support.ticket_created`
- `customer.inquiry`
- `deadline.approaching`

### System Events
- `system.error`
- `rl.training_started`
- `rl.training_completed`

## Event Handlers

You can create custom event handlers:

```python
from event_bus import EventHandler

def custom_handler(event: Event):
    """Handle workflow completion"""
    if event.event_type == EventType.WORKFLOW_COMPLETED:
        run_id = event.data.get('run_id')
        print(f"Workflow {run_id} completed!")

        # Trigger follow-up actions
        # - Send notification
        # - Update dashboard
        # - Log to external system

bus.subscribe(EventType.WORKFLOW_COMPLETED, custom_handler)
```

## Performance & Scaling

### Async Processing
The event bus processes events asynchronously in a background thread, allowing:
- Non-blocking agent execution
- Parallel event handling
- Scalable workflow coordination

### Statistics
Monitor event bus performance:

```python
stats = bus.get_statistics()
print(f"Total events: {stats['total_events']}")
print(f"Handlers called: {stats['handlers_called']}")
print(f"Queue size: {stats['queue_size']}")
```

### Event History
Query past events:

```python
# All events
events = bus.get_event_history(limit=100)

# Specific event type
workflow_events = bus.get_event_history(
    event_type=EventType.WORKFLOW_COMPLETED,
    limit=50
)
```

## Frontend Integration

The Web UI demonstrates:
- **Workflow Execution**: Submit tasks, see results
- **Knowledge Management**: Upload/search company knowledge
- **Real-time Monitoring**: Live event log via WebSocket
- **Agent Performance**: View active agents and metrics
- **RL Training**: Trigger training cycles

### Customizing the UI

Edit `web_ui.html` to:
- Add domain-specific workflows
- Custom knowledge categories
- Branding and styling
- Additional dashboards

### Production Deployment

For production, use a proper frontend framework:
- **React**: Component-based UI
- **Vue**: Progressive framework
- **Angular**: Full-featured framework

The FastAPI backend provides all necessary API endpoints.

## Security Considerations

For production:

1. **Authentication**: Add JWT tokens
2. **CORS**: Restrict allowed origins
3. **Rate Limiting**: Prevent abuse
4. **HTTPS**: Use SSL certificates
5. **Input Validation**: Sanitize all inputs

## Next Steps

1. **Deploy API Server**: Use Docker, Kubernetes, or cloud platforms
2. **Build Production Frontend**: React/Vue/Angular
3. **Connect External Systems**: Kafka, RabbitMQ, AWS EventBridge
4. **Add Authentication**: JWT, OAuth2
5. **Monitoring**: Prometheus, Grafana
6. **Logging**: ELK stack, CloudWatch

## Questions?

Check the API documentation at http://localhost:8000/docs for interactive testing!
