"""
Domain-Specific Configuration System

Each business domain gets its own:
- Specialized workflows
- Domain-specific agents
- Custom action model
- Isolated training data

Examples:
- Legal: Contract drafting, compliance checking, precedent research
- Healthcare: Report generation, diagnosis assistance, medical coding
- E-commerce: Customer support, product recommendations, fraud detection
- Finance: Risk analysis, portfolio optimization, regulatory compliance
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class DomainConfig:
    """Configuration for a specific business domain"""

    # Domain identity
    domain_name: str
    domain_description: str

    # Domain-specific workflows
    workflows: List[str]  # e.g., ["draft_contract", "review_compliance", "research_precedent"]

    # Domain-specific agent types
    agent_types: List[str]  # e.g., ["Legal Researcher", "Contract Drafter", "Compliance Checker"]

    # Domain vocabulary and context
    domain_vocabulary: List[str]  # Key terms specific to this domain
    domain_context: str  # Background context for the domain

    # Training configuration
    min_runs_before_training: int = 50
    success_threshold: float = 0.75

    # Storage paths (isolated per domain)
    data_dir: str = None
    model_dir: str = None

    def __post_init__(self):
        """Set default paths based on domain name"""
        if self.data_dir is None:
            self.data_dir = f"./workflow_db/domains/{self.domain_name}"
        if self.model_dir is None:
            self.model_dir = f"./workflow_db/domains/{self.domain_name}/models"


class DomainRegistry:
    """
    Registry of all business domains

    Each domain is completely isolated:
    - Separate workflow definitions
    - Separate agent pools
    - Separate training data
    - Separate action models
    """

    def __init__(self, registry_path: str = "./workflow_db/domains/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.domains: Dict[str, DomainConfig] = {}
        self._load_registry()

    def _load_registry(self):
        """Load existing domain registry"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                for domain_name, config_dict in data.items():
                    self.domains[domain_name] = DomainConfig(**config_dict)

    def _save_registry(self):
        """Save domain registry to disk"""
        data = {
            name: {
                "domain_name": config.domain_name,
                "domain_description": config.domain_description,
                "workflows": config.workflows,
                "agent_types": config.agent_types,
                "domain_vocabulary": config.domain_vocabulary,
                "domain_context": config.domain_context,
                "min_runs_before_training": config.min_runs_before_training,
                "success_threshold": config.success_threshold,
                "data_dir": config.data_dir,
                "model_dir": config.model_dir,
            }
            for name, config in self.domains.items()
        }

        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)

    def register_domain(self, config: DomainConfig):
        """Register a new business domain"""
        self.domains[config.domain_name] = config

        # Create domain-specific directories
        Path(config.data_dir).mkdir(parents=True, exist_ok=True)
        Path(config.model_dir).mkdir(parents=True, exist_ok=True)

        self._save_registry()

        print(f"✓ Registered domain: {config.domain_name}")
        print(f"  Workflows: {len(config.workflows)}")
        print(f"  Agent types: {len(config.agent_types)}")

    def get_domain(self, domain_name: str) -> Optional[DomainConfig]:
        """Get configuration for a domain"""
        return self.domains.get(domain_name)

    def list_domains(self) -> List[str]:
        """List all registered domains"""
        return list(self.domains.keys())


# ==================== Pre-defined Domain Templates ====================

def create_legal_domain() -> DomainConfig:
    """Legal services domain"""
    return DomainConfig(
        domain_name="legal",
        domain_description="Legal document processing, contract drafting, and compliance",
        workflows=[
            "draft_contract",
            "review_contract",
            "research_precedent",
            "compliance_check",
            "legal_memo",
            "due_diligence",
        ],
        agent_types=[
            "Legal Researcher",
            "Contract Drafter",
            "Compliance Checker",
            "Precedent Analyzer",
            "Legal Editor",
        ],
        domain_vocabulary=[
            "jurisdiction", "precedent", "statute", "liability", "indemnification",
            "force majeure", "arbitration", "litigation", "plaintiff", "defendant",
            "tort", "contract", "negligence", "damages", "remedy"
        ],
        domain_context="""
        Legal domain focuses on contract drafting, legal research, and compliance.
        All work must be accurate, cite relevant precedents, and follow jurisdictional rules.
        Precision and attention to detail are critical.
        """
    )


def create_healthcare_domain() -> DomainConfig:
    """Healthcare and medical domain"""
    return DomainConfig(
        domain_name="healthcare",
        domain_description="Medical report generation, diagnosis assistance, and clinical documentation",
        workflows=[
            "generate_radiology_report",
            "clinical_summary",
            "medical_coding",
            "patient_intake",
            "treatment_plan",
            "discharge_summary",
        ],
        agent_types=[
            "Medical Literature Reviewer",
            "Clinical Documentation Specialist",
            "Medical Coder",
            "Diagnosis Assistant",
            "Treatment Planner",
        ],
        domain_vocabulary=[
            "diagnosis", "prognosis", "pathology", "radiology", "ICD-10",
            "CPT", "clinical", "patient", "symptom", "treatment",
            "medication", "prescription", "dosage", "contraindication", "adverse event"
        ],
        domain_context="""
        Healthcare domain focuses on clinical documentation and medical decision support.
        All outputs must be evidence-based, cite medical literature, and follow clinical guidelines.
        Patient safety and accuracy are paramount.
        """
    )


def create_ecommerce_domain() -> DomainConfig:
    """E-commerce and customer support domain"""
    return DomainConfig(
        domain_name="ecommerce",
        domain_description="Customer support, product recommendations, and order management",
        workflows=[
            "customer_support_response",
            "product_recommendation",
            "order_issue_resolution",
            "return_processing",
            "fraud_detection",
            "customer_feedback_analysis",
        ],
        agent_types=[
            "Customer Support Specialist",
            "Product Recommendation Engine",
            "Fraud Analyzer",
            "Sentiment Analyzer",
            "Order Management Agent",
        ],
        domain_vocabulary=[
            "SKU", "inventory", "shipping", "return", "refund",
            "customer", "order", "product", "cart", "checkout",
            "payment", "delivery", "tracking", "warranty", "satisfaction"
        ],
        domain_context="""
        E-commerce domain focuses on customer experience and operational efficiency.
        Responses should be friendly, helpful, and solution-oriented.
        Speed and customer satisfaction are key metrics.
        """
    )


def create_finance_domain() -> DomainConfig:
    """Financial services domain"""
    return DomainConfig(
        domain_name="finance",
        domain_description="Financial analysis, risk assessment, and regulatory compliance",
        workflows=[
            "risk_analysis",
            "portfolio_optimization",
            "regulatory_compliance",
            "financial_report",
            "fraud_detection",
            "credit_assessment",
        ],
        agent_types=[
            "Risk Analyst",
            "Portfolio Manager",
            "Compliance Officer",
            "Financial Researcher",
            "Fraud Detection Specialist",
        ],
        domain_vocabulary=[
            "portfolio", "risk", "diversification", "volatility", "ROI",
            "compliance", "regulation", "SEC", "fiduciary", "liquidity",
            "equity", "bond", "derivative", "hedge", "yield"
        ],
        domain_context="""
        Finance domain focuses on accuracy, risk management, and regulatory compliance.
        All analysis must be data-driven and cite relevant financial principles.
        Regulatory compliance is mandatory.
        """
    )


def create_content_marketing_domain() -> DomainConfig:
    """Content marketing and creative domain"""
    return DomainConfig(
        domain_name="content_marketing",
        domain_description="Content creation, SEO optimization, and marketing campaigns",
        workflows=[
            "blog_post_creation",
            "seo_optimization",
            "social_media_campaign",
            "email_marketing",
            "content_strategy",
            "competitor_analysis",
        ],
        agent_types=[
            "Content Writer",
            "SEO Specialist",
            "Social Media Manager",
            "Marketing Strategist",
            "Brand Voice Guardian",
        ],
        domain_vocabulary=[
            "SEO", "keyword", "engagement", "conversion", "CTR",
            "audience", "persona", "funnel", "campaign", "analytics",
            "brand", "voice", "tone", "storytelling", "CTA"
        ],
        domain_context="""
        Content marketing domain focuses on engagement, conversion, and brand voice.
        Content should be compelling, optimized for search, and aligned with brand guidelines.
        Creativity and data-driven optimization are equally important.
        """
    )


# ==================== Domain Initialization ====================

def initialize_standard_domains() -> DomainRegistry:
    """Initialize registry with standard domain templates"""
    registry = DomainRegistry()

    # Register standard domains
    standard_domains = [
        create_legal_domain(),
        create_healthcare_domain(),
        create_ecommerce_domain(),
        create_finance_domain(),
        create_content_marketing_domain(),
    ]

    for domain in standard_domains:
        if domain.domain_name not in registry.domains:
            registry.register_domain(domain)

    return registry


def create_custom_domain(
    name: str,
    description: str,
    workflows: List[str],
    agent_types: List[str],
    vocabulary: List[str],
    context: str
) -> DomainConfig:
    """
    Create a custom business domain

    Example:
        education_domain = create_custom_domain(
            name="education",
            description="Educational content and course creation",
            workflows=["create_lesson_plan", "generate_quiz", "grade_assignment"],
            agent_types=["Curriculum Designer", "Content Creator", "Assessment Specialist"],
            vocabulary=["pedagogy", "learning objective", "assessment", "curriculum"],
            context="Focus on effective learning outcomes and student engagement"
        )
    """
    return DomainConfig(
        domain_name=name,
        domain_description=description,
        workflows=workflows,
        agent_types=agent_types,
        domain_vocabulary=vocabulary,
        domain_context=context
    )


# ==================== Usage Examples ====================

if __name__ == "__main__":
    # Initialize with standard domains
    registry = initialize_standard_domains()

    print("\n📚 Registered Domains:")
    for domain_name in registry.list_domains():
        domain = registry.get_domain(domain_name)
        print(f"\n{domain_name}:")
        print(f"  Description: {domain.domain_description}")
        print(f"  Workflows: {', '.join(domain.workflows[:3])}...")
        print(f"  Agents: {', '.join(domain.agent_types[:3])}...")

    # Create custom domain
    print("\n\n✨ Creating Custom Domain:")
    custom = create_custom_domain(
        name="real_estate",
        description="Real estate listings, valuations, and market analysis",
        workflows=["property_valuation", "market_analysis", "listing_creation"],
        agent_types=["Property Analyst", "Market Researcher", "Listing Writer"],
        vocabulary=["valuation", "comps", "MLS", "appraisal", "market"],
        context="Focus on accurate valuations and compelling property descriptions"
    )

    registry.register_domain(custom)
    print(f"✓ Created '{custom.domain_name}' domain")
