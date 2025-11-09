"""
Company Knowledge Center
Central repository for company-specific knowledge accessible to all agents

Features:
- Upload documents, policies, FAQs, processes
- Vector search for semantic retrieval
- Domain-specific knowledge bases
- Version control for knowledge updates
- Usage analytics (what agents search for)
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
import hashlib
from dataclasses import dataclass, asdict


@dataclass
class KnowledgeDocument:
    """A single knowledge document"""
    doc_id: str
    title: str
    content: str
    doc_type: str  # policy, faq, process, guideline, etc.
    domain: str  # Which domain this knowledge belongs to
    tags: List[str]
    created_by: str
    created_at: str
    updated_at: str
    version: int = 1
    metadata: Dict[str, Any] = None

    def to_dict(self) -> dict:
        return asdict(self)


class KnowledgeCenter:
    """
    Central Knowledge Repository

    Stores and retrieves company-specific knowledge for agents
    """

    def __init__(self, base_path: str = "./workflow_db/knowledge_center"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Storage paths
        self.docs_path = self.base_path / "documents"
        self.docs_path.mkdir(exist_ok=True)

        self.index_path = self.base_path / "index.json"

        # In-memory index
        self.index: Dict[str, KnowledgeDocument] = {}
        self._load_index()

    def _load_index(self):
        """Load the knowledge index"""
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                data = json.load(f)
                self.index = {
                    doc_id: KnowledgeDocument(**doc_data)
                    for doc_id, doc_data in data.items()
                }

    def _save_index(self):
        """Save the knowledge index"""
        with open(self.index_path, 'w') as f:
            json.dump(
                {doc_id: doc.to_dict() for doc_id, doc in self.index.items()},
                f,
                indent=2
            )

    def add_document(
        self,
        title: str,
        content: str,
        doc_type: str,
        domain: str,
        tags: List[str],
        created_by: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a knowledge document

        Args:
            title: Document title
            content: Full document content
            doc_type: Type (policy, faq, process, guideline)
            domain: Which domain (legal, sales, hr, general, etc.)
            tags: Search tags
            created_by: Who uploaded this (user/manager name)
            metadata: Additional metadata

        Returns:
            Document ID
        """
        # Generate document ID
        doc_id = hashlib.sha256(
            f"{title}{content}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]

        # Create document
        doc = KnowledgeDocument(
            doc_id=doc_id,
            title=title,
            content=content,
            doc_type=doc_type,
            domain=domain,
            tags=tags,
            created_by=created_by,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )

        # Save to disk
        doc_file = self.docs_path / f"{doc_id}.json"
        with open(doc_file, 'w') as f:
            json.dump(doc.to_dict(), f, indent=2)

        # Add to index
        self.index[doc_id] = doc
        self._save_index()

        print(f"✓ Added knowledge document: {title} ({doc_id})")
        print(f"  Domain: {domain}")
        print(f"  Type: {doc_type}")
        print(f"  Tags: {', '.join(tags)}")

        return doc_id

    def update_document(self, doc_id: str, content: str, updated_by: str) -> None:
        """Update a document's content"""
        if doc_id not in self.index:
            raise ValueError(f"Document {doc_id} not found")

        doc = self.index[doc_id]

        # Update
        doc.content = content
        doc.updated_at = datetime.utcnow().isoformat()
        doc.version += 1

        # Save
        doc_file = self.docs_path / f"{doc_id}.json"
        with open(doc_file, 'w') as f:
            json.dump(doc.to_dict(), f, indent=2)

        self._save_index()

        print(f"✓ Updated document: {doc.title} (v{doc.version})")

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        doc_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Tuple[KnowledgeDocument, float]]:
        """
        Search for relevant documents

        Args:
            query: Search query
            domain: Filter by domain
            doc_type: Filter by document type
            limit: Max results

        Returns:
            List of (document, relevance_score) tuples
        """
        # Filter documents
        candidates = list(self.index.values())

        if domain:
            candidates = [d for d in candidates if d.domain == domain]

        if doc_type:
            candidates = [d for d in candidates if d.doc_type == doc_type]

        # Simple keyword search (TODO: Replace with vector search)
        query_lower = query.lower()
        results = []

        for doc in candidates:
            score = 0.0

            # Title match (high weight)
            if query_lower in doc.title.lower():
                score += 5.0

            # Content match
            content_lower = doc.content.lower()
            query_words = query_lower.split()
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word) * 0.5

            # Tag match
            for tag in doc.tags:
                if query_lower in tag.lower():
                    score += 2.0

            if score > 0:
                results.append((doc, score))

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """Get a specific document"""
        return self.index.get(doc_id)

    def list_documents(
        self,
        domain: Optional[str] = None,
        doc_type: Optional[str] = None
    ) -> List[KnowledgeDocument]:
        """List all documents with optional filtering"""
        docs = list(self.index.values())

        if domain:
            docs = [d for d in docs if d.domain == domain]

        if doc_type:
            docs = [d for d in docs if d.doc_type == doc_type]

        return sorted(docs, key=lambda d: d.updated_at, reverse=True)

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        docs = list(self.index.values())

        # Count by domain
        by_domain = {}
        for doc in docs:
            by_domain[doc.domain] = by_domain.get(doc.domain, 0) + 1

        # Count by type
        by_type = {}
        for doc in docs:
            by_type[doc.doc_type] = by_type.get(doc.doc_type, 0) + 1

        return {
            "total_documents": len(docs),
            "by_domain": by_domain,
            "by_type": by_type,
            "total_size_kb": sum(
                len(doc.content.encode('utf-8')) for doc in docs
            ) / 1024
        }


class KnowledgeManager:
    """
    Manager interface for uploading and managing company knowledge

    This is what business users/managers interact with
    """

    def __init__(self, knowledge_center: KnowledgeCenter):
        self.kc = knowledge_center

    def upload_policy(self, title: str, content: str, domain: str, uploaded_by: str) -> str:
        """Upload a company policy"""
        return self.kc.add_document(
            title=title,
            content=content,
            doc_type="policy",
            domain=domain,
            tags=["policy", "official", domain],
            created_by=uploaded_by,
            metadata={"requires_acknowledgment": True}
        )

    def upload_faq(self, title: str, qa_pairs: List[Dict[str, str]], domain: str, uploaded_by: str) -> str:
        """Upload FAQ document"""
        # Format FAQ content
        content = f"# {title}\n\n"
        for i, qa in enumerate(qa_pairs, 1):
            content += f"**Q{i}: {qa['question']}**\n\n"
            content += f"A: {qa['answer']}\n\n"

        return self.kc.add_document(
            title=title,
            content=content,
            doc_type="faq",
            domain=domain,
            tags=["faq", "questions", domain],
            created_by=uploaded_by
        )

    def upload_process(self, title: str, steps: List[str], domain: str, uploaded_by: str) -> str:
        """Upload a business process"""
        # Format process content
        content = f"# {title}\n\n"
        for i, step in enumerate(steps, 1):
            content += f"{i}. {step}\n"

        return self.kc.add_document(
            title=title,
            content=content,
            doc_type="process",
            domain=domain,
            tags=["process", "procedure", domain],
            created_by=uploaded_by
        )

    def upload_guideline(self, title: str, content: str, domain: str, uploaded_by: str) -> str:
        """Upload company guidelines"""
        return self.kc.add_document(
            title=title,
            content=content,
            doc_type="guideline",
            domain=domain,
            tags=["guideline", "best-practice", domain],
            created_by=uploaded_by
        )

    def bulk_upload_from_files(self, file_paths: List[str], domain: str, uploaded_by: str) -> List[str]:
        """
        Bulk upload documents from files

        Supports: .txt, .md, .pdf (future), .docx (future)
        """
        doc_ids = []

        for file_path in file_paths:
            path = Path(file_path)

            if not path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue

            # Read content
            if path.suffix in ['.txt', '.md']:
                with open(path, 'r') as f:
                    content = f.read()

                # Determine doc type from filename or extension
                doc_type = "document"
                if "policy" in path.stem.lower():
                    doc_type = "policy"
                elif "faq" in path.stem.lower():
                    doc_type = "faq"
                elif "process" in path.stem.lower():
                    doc_type = "process"

                doc_id = self.kc.add_document(
                    title=path.stem,
                    content=content,
                    doc_type=doc_type,
                    domain=domain,
                    tags=[doc_type, domain, "bulk-upload"],
                    created_by=uploaded_by
                )

                doc_ids.append(doc_id)

        return doc_ids


# ==================== Integration with Agents ====================

def create_knowledge_retrieval_tool(knowledge_center: KnowledgeCenter, domain: str):
    """
    Create a tool that agents can use to search the knowledge base

    This gets added to agents so they can query company knowledge
    """
    from agno.tools import tool

    @tool
    def search_company_knowledge(query: str) -> str:
        """
        Search the company knowledge base for relevant information.

        Use this when you need company-specific information like:
        - Company policies
        - Standard processes
        - FAQs
        - Guidelines

        Args:
            query: What to search for

        Returns:
            Relevant knowledge from the company knowledge base
        """
        # Search with domain filter
        results = knowledge_center.search(query, domain=domain, limit=3)

        if not results:
            return f"No relevant company knowledge found for: {query}"

        # Format results
        output = f"Found {len(results)} relevant documents:\n\n"

        for doc, score in results:
            output += f"**{doc.title}** ({doc.doc_type})\n"
            output += f"{doc.content[:500]}...\n\n"

        return output

    return search_company_knowledge


# ==================== Example Usage ====================

def example_knowledge_center():
    """Example: Setting up and using knowledge center"""
    from rich.console import Console
    console = Console()

    console.print("\n[bold cyan]Company Knowledge Center Demo[/bold cyan]\n")

    # 1. Create knowledge center
    kc = KnowledgeCenter()
    manager = KnowledgeManager(kc)

    # 2. Manager uploads company policies
    console.print("[yellow]Manager uploading company knowledge...[/yellow]\n")

    # Upload remote work policy
    manager.upload_policy(
        title="Remote Work Policy",
        content="""
        # Remote Work Policy

        ## Eligibility
        All full-time employees are eligible for remote work with manager approval.

        ## Requirements
        - Maintain regular working hours (9 AM - 5 PM local time)
        - Available on company communication channels
        - Secure internet connection required
        - Home office setup meeting ergonomic standards

        ## Sick Child Care
        Employees may work remotely when caring for sick children without using PTO
        for up to 5 days per year. Manager notification required.

        ## Equipment
        Company provides: Laptop, monitor, keyboard, mouse
        Employee responsible for: Internet connection, workspace

        ## Performance
        Same performance standards apply as office work.
        Regular check-ins with manager required.
        """,
        domain="hr",
        uploaded_by="HR Manager"
    )

    # Upload customer support FAQ
    manager.upload_faq(
        title="Customer Support FAQ - Return Policy",
        qa_pairs=[
            {
                "question": "What is our return window?",
                "answer": "Customers can return products within 30 days of purchase for a full refund."
            },
            {
                "question": "Do we cover return shipping?",
                "answer": "Yes, we provide a prepaid return label for all returns."
            },
            {
                "question": "What if the product is damaged?",
                "answer": "Damaged products get priority processing and can be returned even after 30 days."
            },
            {
                "question": "Can customers exchange instead of return?",
                "answer": "Yes, exchanges are processed immediately without waiting for return receipt."
            }
        ],
        domain="customer_support",
        uploaded_by="Support Manager"
    )

    # Upload sales process
    manager.upload_process(
        title="Enterprise Sales Process",
        steps=[
            "Initial contact: Qualify lead (budget, authority, need, timeline)",
            "Discovery call: Understand pain points and requirements",
            "Product demo: Customized to their use case",
            "Proposal: Generate using pricing calculator (15% discount for 500+ units)",
            "Negotiation: Involve sales director for deals over $50K",
            "Contract: Legal review required for custom terms",
            "Close: Onboarding kickoff within 2 business days"
        ],
        domain="sales",
        uploaded_by="Sales VP"
    )

    console.print("\n[green]✓ Knowledge uploaded![/green]\n")

    # 3. Show statistics
    stats = kc.get_statistics()
    console.print(f"[cyan]Knowledge Base Statistics:[/cyan]")
    console.print(f"  Total documents: {stats['total_documents']}")
    console.print(f"  By domain: {stats['by_domain']}")
    console.print(f"  By type: {stats['by_type']}\n")

    # 4. Agent searches knowledge
    console.print("[yellow]Agent searching for information...[/yellow]\n")

    # Example 1: HR agent looks up remote work policy
    console.print("[cyan]Q: Can I work from home if my child is sick?[/cyan]")
    results = kc.search("remote work sick child", domain="hr")
    if results:
        doc, score = results[0]
        console.print(f"[green]Found:[/green] {doc.title}")
        console.print(f"{doc.content[:300]}...\n")

    # Example 2: Support agent looks up return policy
    console.print("[cyan]Q: What's our return policy for damaged items?[/cyan]")
    results = kc.search("return policy damaged", domain="customer_support")
    if results:
        doc, score = results[0]
        console.print(f"[green]Found:[/green] {doc.title}")
        console.print(f"{doc.content[:300]}...\n")

    # Example 3: Sales agent looks up discount rules
    console.print("[cyan]Q: What discount for 500 units?[/cyan]")
    results = kc.search("discount 500 units", domain="sales")
    if results:
        doc, score = results[0]
        console.print(f"[green]Found:[/green] {doc.title}")
        console.print(f"{doc.content[:300]}...\n")


if __name__ == "__main__":
    example_knowledge_center()
