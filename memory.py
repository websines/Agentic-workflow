"""
Memory System for Agentic Workflow
Dual-memory architecture: Short-term (working) + Long-term (knowledge)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json


class ShortTermMemory:
    """
    Short-term (Working) Memory

    Stores:
    - Current conversation context
    - Active workflow state
    - Recent tool calls and decisions
    - Temporary results

    Implementation: In-memory with optional Redis backing
    """

    def __init__(self, max_size: int = 100, ttl_minutes: int = 60):
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
        self.memory: deque = deque(maxlen=max_size)
        self.context: Dict[str, Any] = {}

    def add(self, item: Dict[str, Any]):
        """Add an item to short-term memory"""
        item['timestamp'] = datetime.utcnow().isoformat()
        self.memory.append(item)

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent items from memory"""
        return list(self.memory)[-limit:]

    def set_context(self, key: str, value: Any):
        """Set a context variable"""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context variable"""
        return self.context.get(key, default)

    def clear_old(self):
        """Clear old items beyond TTL"""
        cutoff = datetime.utcnow() - self.ttl
        self.memory = deque(
            [item for item in self.memory
             if datetime.fromisoformat(item['timestamp']) > cutoff],
            maxlen=self.max_size
        )

    def clear(self):
        """Clear all short-term memory"""
        self.memory.clear()
        self.context.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Export memory state"""
        return {
            "items": list(self.memory),
            "context": self.context
        }


class LongTermMemory:
    """
    Long-term (Knowledge) Memory

    Stores:
    - Historical patterns and learned behaviors
    - Successful workflow templates
    - Agent performance history
    - Embeddings of past runs for semantic search

    Future Implementation: Helix-DB (Graph + Vector Database)

    Graph Component:
    - Nodes: Agents, Workflows, Tasks, Runs
    - Edges: agent_performed_task, workflow_contains_step, run_used_agent
    - Queries: "Which agents work well together?", "What workflows succeed for X type of task?"

    Vector Component:
    - Embeddings of successful runs
    - Semantic search: "Find similar situations"
    - Nearest neighbor: "What worked in similar contexts?"
    """

    def __init__(self, storage_path: str = "./workflow_db/long_term_memory"):
        self.storage_path = storage_path
        # Placeholder - would integrate with Helix-DB
        self.knowledge_base: Dict[str, Any] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.graph: Dict[str, List[Dict[str, Any]]] = {
            "agents": [],
            "workflows": [],
            "relationships": []
        }

    # ==================== Knowledge Storage ====================

    def store_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """Store a learned pattern"""
        if pattern_type not in self.knowledge_base:
            self.knowledge_base[pattern_type] = []

        pattern_data['stored_at'] = datetime.utcnow().isoformat()
        self.knowledge_base[pattern_type].append(pattern_data)

    def retrieve_patterns(self, pattern_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve learned patterns"""
        patterns = self.knowledge_base.get(pattern_type, [])
        return patterns[-limit:]

    # ==================== Semantic Search (Vector DB) ====================

    def store_embedding(self, run_id: str, embedding: List[float], metadata: Dict[str, Any]):
        """
        Store an embedding for semantic search

        In production with Helix-DB:
        - Would store in vector component
        - Enable cosine similarity search
        - Find semantically similar runs
        """
        self.embeddings[run_id] = {
            "vector": embedding,
            "metadata": metadata,
            "stored_at": datetime.utcnow().isoformat()
        }

    def semantic_search(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar runs using semantic search

        In production with Helix-DB:
        - Cosine similarity search in vector space
        - Return most similar historical runs
        - Use for "what worked in similar situations?"
        """
        # Placeholder - would use vector DB
        # For now, return empty
        return []

    # ==================== Graph Queries ====================

    def add_relationship(self, source: str, relationship: str, target: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a relationship to the knowledge graph

        Examples:
        - ("Research Agent", "succeeded_in", "Run_123", {success_rate: 0.95})
        - ("Content Workflow", "uses_agent", "Writer Agent", {frequency: 0.8})
        - ("Analyst Agent", "works_well_with", "Research Agent", {synergy: 0.9})
        """
        self.graph["relationships"].append({
            "source": source,
            "relationship": relationship,
            "target": target,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        })

    def query_graph(self, pattern: str) -> List[Dict[str, Any]]:
        """
        Query the knowledge graph

        In production with Helix-DB:
        - Cypher-like queries
        - Find patterns in agent collaboration
        - Discover successful workflows

        Examples:
        - "MATCH (a:Agent)-[:WORKS_WELL_WITH]->(b:Agent) WHERE a.success_rate > 0.8"
        - "MATCH (w:Workflow)-[:USES_AGENT]->(a:Agent) WHERE w.type='content_creation'"
        """
        # Placeholder - would use graph DB
        return []

    # ==================== Agent Evolution Knowledge ====================

    def record_agent_evolution(self, agent_name: str, from_version: int, to_version: int,
                              reason: str, performance_delta: float):
        """Record an agent evolution event"""
        evolution = {
            "agent": agent_name,
            "from_version": from_version,
            "to_version": to_version,
            "reason": reason,
            "performance_delta": performance_delta,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.store_pattern("agent_evolutions", evolution)

    def get_evolution_history(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get evolution history for an agent"""
        evolutions = self.knowledge_base.get("agent_evolutions", [])
        return [e for e in evolutions if e["agent"] == agent_name]

    # ==================== Workflow Learning ====================

    def record_workflow_success(self, workflow_type: str, success_factors: List[str],
                               performance_metrics: Dict[str, Any]):
        """Record what made a workflow successful"""
        success_pattern = {
            "workflow_type": workflow_type,
            "success_factors": success_factors,
            "metrics": performance_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.store_pattern("workflow_successes", success_pattern)

    def get_successful_patterns(self, workflow_type: str) -> List[Dict[str, Any]]:
        """Get successful patterns for a workflow type"""
        successes = self.knowledge_base.get("workflow_successes", [])
        return [s for s in successes if s["workflow_type"] == workflow_type]

    # ==================== Integration Points ====================

    def integrate_with_helix_db(self, helix_connection: Any):
        """
        Integration point for Helix-DB

        TODO: Implement when ready:
        1. Connect to Helix-DB instance
        2. Migrate in-memory data to Helix
        3. Use Helix for all graph + vector operations
        4. Enable advanced queries
        """
        pass


class MemorySystem:
    """
    Unified Memory System
    Combines short-term and long-term memory
    """

    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()

    def remember_short_term(self, item: Dict[str, Any]):
        """Add to short-term memory"""
        self.short_term.add(item)

    def remember_long_term(self, pattern_type: str, pattern_data: Dict[str, Any]):
        """Add to long-term memory"""
        self.long_term.store_pattern(pattern_type, pattern_data)

    def recall_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Recall recent short-term memories"""
        return self.short_term.get_recent(limit)

    def recall_pattern(self, pattern_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recall learned patterns from long-term memory"""
        return self.long_term.retrieve_patterns(pattern_type, limit)

    def consolidate(self, run_id: str, run_data: Dict[str, Any]):
        """
        Consolidate short-term memory to long-term

        Called after a successful run to:
        1. Extract patterns
        2. Store in long-term memory
        3. Update knowledge graph
        4. Clear relevant short-term memory
        """
        # Extract and store successful patterns
        if run_data.get("status") == "completed":
            self.long_term.record_workflow_success(
                workflow_type=run_data.get("workflow_type"),
                success_factors=run_data.get("success_factors", []),
                performance_metrics=run_data.get("metrics", {})
            )

    def clear_short_term(self):
        """Clear short-term memory"""
        self.short_term.clear()
