"""
Event-Driven Architecture for Agentic Workflow

Provides:
- Asynchronous event processing
- Pub/Sub pattern for agent communication
- Integration with external event bridges (Kafka, RabbitMQ, AWS EventBridge)
- Real-time event streaming
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional
from enum import Enum
import asyncio
import json
import uuid
from queue import Queue
from threading import Thread, Lock


class EventType(Enum):
    """Types of events in the system"""
    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    # Agent events
    AGENT_CREATED = "agent.created"
    AGENT_ASSIGNED = "agent.assigned"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"

    # Knowledge events
    KNOWLEDGE_UPLOADED = "knowledge.uploaded"
    KNOWLEDGE_UPDATED = "knowledge.updated"
    KNOWLEDGE_SEARCHED = "knowledge.searched"

    # Document events (for lawyer use case)
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_REVIEWED = "document.reviewed"
    COMPLIANCE_CHECK_STARTED = "compliance.check_started"
    COMPLIANCE_CHECK_COMPLETED = "compliance.check_completed"

    # Business events (for SMB use case)
    SUPPORT_TICKET_CREATED = "support.ticket_created"
    CUSTOMER_INQUIRY = "customer.inquiry"
    DEADLINE_APPROACHING = "deadline.approaching"

    # System events
    SYSTEM_ERROR = "system.error"
    RL_TRAINING_STARTED = "rl.training_started"
    RL_TRAINING_COMPLETED = "rl.training_completed"


@dataclass
class Event:
    """Base event class"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.WORKFLOW_STARTED
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source: str = ""  # Which component emitted this
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


EventHandler = Callable[[Event], None]


class EventBus:
    """
    Central Event Bus for async agent coordination

    Features:
    - Pub/Sub pattern
    - Event routing by type
    - Async event processing
    - Integration with external event bridges
    """

    def __init__(self, enable_async: bool = True):
        self.enable_async = enable_async
        self.subscribers: Dict[EventType, List[EventHandler]] = {}
        self.event_history: List[Event] = []
        self.event_queue: Queue = Queue()
        self.lock = Lock()

        # Statistics
        self.stats = {
            "total_events": 0,
            "events_by_type": {},
            "handlers_called": 0
        }

        # Start async processing thread if enabled
        if self.enable_async:
            self.processing_thread = Thread(target=self._process_events, daemon=True)
            self.processing_thread.start()

    def subscribe(self, event_type: EventType, handler: EventHandler):
        """
        Subscribe to events of a specific type

        Args:
            event_type: Type of event to listen for
            handler: Callback function to execute when event occurs
        """
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)
            print(f"✓ Subscribed handler to {event_type.value}")

    def unsubscribe(self, event_type: EventType, handler: EventHandler):
        """Unsubscribe from events"""
        with self.lock:
            if event_type in self.subscribers:
                if handler in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(handler)

    def publish(self, event: Event, async_processing: bool = True):
        """
        Publish an event to all subscribers

        Args:
            event: Event to publish
            async_processing: If True, process handlers asynchronously
        """
        with self.lock:
            # Log event
            self.event_history.append(event)
            self.stats["total_events"] += 1

            event_type_str = event.event_type.value
            if event_type_str not in self.stats["events_by_type"]:
                self.stats["events_by_type"][event_type_str] = 0
            self.stats["events_by_type"][event_type_str] += 1

        # Queue for async processing or execute immediately
        if async_processing and self.enable_async:
            self.event_queue.put(event)
        else:
            self._execute_handlers(event)

    def _execute_handlers(self, event: Event):
        """Execute all handlers for an event"""
        event_type = event.event_type

        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    handler(event)
                    with self.lock:
                        self.stats["handlers_called"] += 1
                except Exception as e:
                    print(f"❌ Error in event handler for {event_type.value}: {e}")

    def _process_events(self):
        """Background thread for async event processing"""
        while True:
            try:
                event = self.event_queue.get(timeout=1.0)
                self._execute_handlers(event)
                self.event_queue.task_done()
            except:
                pass  # Timeout, continue loop

    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        with self.lock:
            return {
                "total_events": self.stats["total_events"],
                "events_by_type": self.stats["events_by_type"].copy(),
                "handlers_called": self.stats["handlers_called"],
                "subscribers": {
                    event_type.value: len(handlers)
                    for event_type, handlers in self.subscribers.items()
                },
                "queue_size": self.event_queue.qsize()
            }

    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get event history with optional filtering"""
        with self.lock:
            if event_type:
                events = [e for e in self.event_history if e.event_type == event_type]
            else:
                events = self.event_history.copy()

            return events[-limit:]


# ==================== External Event Bridge Integration ====================

class ExternalEventBridge:
    """
    Base class for integrating with external event systems

    Subclass this to implement Kafka, RabbitMQ, AWS EventBridge, etc.
    """

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def forward_to_external(self, event: Event):
        """Forward event to external system (implement in subclass)"""
        raise NotImplementedError

    def receive_from_external(self) -> Optional[Event]:
        """Receive event from external system (implement in subclass)"""
        raise NotImplementedError


class KafkaEventBridge(ExternalEventBridge):
    """
    Kafka integration for event streaming

    TODO: Implement actual Kafka producer/consumer
    This is a stub for future implementation
    """

    def __init__(self, event_bus: EventBus, bootstrap_servers: str = "localhost:9092"):
        super().__init__(event_bus)
        self.bootstrap_servers = bootstrap_servers
        # self.producer = KafkaProducer(...)  # Implement when kafka-python is added
        # self.consumer = KafkaConsumer(...)

    def forward_to_external(self, event: Event):
        """Forward event to Kafka topic"""
        # topic = f"agentic-workflow-{event.event_type.value}"
        # self.producer.send(topic, value=event.to_json().encode('utf-8'))
        print(f"[Kafka Stub] Would publish to: {event.event_type.value}")

    def receive_from_external(self) -> Optional[Event]:
        """Receive event from Kafka"""
        # message = next(self.consumer)
        # return Event(**json.loads(message.value))
        return None


class RabbitMQEventBridge(ExternalEventBridge):
    """
    RabbitMQ integration

    TODO: Implement actual RabbitMQ publisher/consumer
    """

    def forward_to_external(self, event: Event):
        print(f"[RabbitMQ Stub] Would publish: {event.event_type.value}")

    def receive_from_external(self) -> Optional[Event]:
        return None


class AWSEventBridge(ExternalEventBridge):
    """
    AWS EventBridge integration

    TODO: Implement using boto3
    """

    def forward_to_external(self, event: Event):
        print(f"[AWS EventBridge Stub] Would publish: {event.event_type.value}")

    def receive_from_external(self) -> Optional[Event]:
        return None


# ==================== Pre-built Event Handlers ====================

def log_event_handler(event: Event):
    """Simple logging handler"""
    print(f"📡 Event: {event.event_type.value} from {event.source}")


def workflow_completion_handler(event: Event):
    """Handle workflow completion events"""
    if event.event_type == EventType.WORKFLOW_COMPLETED:
        print(f"✅ Workflow {event.data.get('run_id')} completed successfully")


def compliance_check_handler(event: Event):
    """Handle compliance check events (for lawyer use case)"""
    if event.event_type == EventType.COMPLIANCE_CHECK_COMPLETED:
        doc_id = event.data.get('document_id')
        passed = event.data.get('passed', False)
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} Compliance check for document {doc_id}")


def deadline_alert_handler(event: Event):
    """Handle deadline approaching events (for SMB use case)"""
    if event.event_type == EventType.DEADLINE_APPROACHING:
        task = event.data.get('task')
        deadline = event.data.get('deadline')
        print(f"⚠️  ALERT: {task} deadline approaching: {deadline}")


# ==================== Example Usage ====================

def example_event_bus():
    """Example: Using the event bus"""
    from rich.console import Console
    console = Console()

    console.print("\n[bold cyan]Event Bus Demo[/bold cyan]\n")

    # Create event bus
    bus = EventBus(enable_async=True)

    # Subscribe handlers
    bus.subscribe(EventType.WORKFLOW_COMPLETED, workflow_completion_handler)
    bus.subscribe(EventType.COMPLIANCE_CHECK_COMPLETED, compliance_check_handler)
    bus.subscribe(EventType.DEADLINE_APPROACHING, deadline_alert_handler)

    # Publish events
    console.print("[yellow]Publishing events...[/yellow]\n")

    # Event 1: Workflow completed
    bus.publish(Event(
        event_type=EventType.WORKFLOW_COMPLETED,
        source="WorkflowEngine",
        data={"run_id": "abc123", "status": "success"}
    ))

    # Event 2: Compliance check (lawyer scenario)
    bus.publish(Event(
        event_type=EventType.COMPLIANCE_CHECK_COMPLETED,
        source="ComplianceAgent",
        data={"document_id": "contract_456", "passed": True}
    ))

    # Event 3: Deadline approaching (SMB scenario)
    bus.publish(Event(
        event_type=EventType.DEADLINE_APPROACHING,
        source="SchedulerAgent",
        data={"task": "Client proposal", "deadline": "2024-01-15"}
    ))

    # Wait for async processing
    import time
    time.sleep(1)

    # Show statistics
    console.print("\n[cyan]Event Bus Statistics:[/cyan]")
    stats = bus.get_statistics()
    console.print(f"  Total events: {stats['total_events']}")
    console.print(f"  Handlers called: {stats['handlers_called']}")
    console.print(f"  Events by type: {stats['events_by_type']}\n")


if __name__ == "__main__":
    example_event_bus()
