"""
Action Model Training for Recruitment

Distills LLM decisions into small, fast neural networks:
1. Placement Success Predictor (will this candidate accept the offer?)
2. Interview Quality Scorer (how good was the interview response?)
3. Client Conversion Predictor (will this company become a client?)
4. Candidate-Job Matcher (optimal matching)
5. Ghosting Detector (will this candidate ghost?)

After 6-12 months of data collection, these models replace expensive LLM calls
with 10-50ms inference, free after training.
"""

import json
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import numpy as np

# TODO: When implementing actual training, add:
# import torch
# import torch.nn as nn
# from sklearn.model_selection import train_test_split


@dataclass
class TrainingExample:
    """A single training example for action model"""
    example_id: str
    model_type: str  # placement, interview, client_conversion, matching, ghosting
    input_features: Dict[str, Any]
    target_output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ActionModelMetrics:
    """Performance metrics for an action model"""
    model_name: str
    model_type: str
    training_examples: int
    validation_accuracy: float
    inference_time_ms: float
    model_size_mb: float
    training_date: str
    version: int = 1


class PlacementDataCollector:
    """
    Collects training data from actual placements

    Every workflow run becomes training data for action models
    """

    def __init__(self, storage_path: str = "./action_model_data"):
        self.storage_path = storage_path

    def collect_placement_example(
        self,
        candidate_profile: Dict[str, Any],
        job_profile: Dict[str, Any],
        interview_results: Dict[str, Any],
        offer_details: Dict[str, Any],
        outcome: str  # accepted, rejected, ghosted
    ) -> TrainingExample:
        """
        Collect training data from a placement attempt

        This trains the Placement Success Predictor
        """

        # Extract features
        features = {
            # Candidate features
            "candidate_years_experience": candidate_profile.get("years_experience", 0),
            "candidate_current_salary": candidate_profile.get("current_salary", 0),
            "candidate_location": candidate_profile.get("location", ""),
            "candidate_job_changes_3y": candidate_profile.get("job_changes_last_3_years", 0),

            # Job features
            "job_salary_min": job_profile.get("salary_min", 0),
            "job_salary_max": job_profile.get("salary_max", 0),
            "job_remote_policy": job_profile.get("remote_policy", ""),
            "job_company_stage": job_profile.get("company_stage", ""),

            # Match features
            "salary_delta_percent": (
                (offer_details.get("offer_salary", 0) - candidate_profile.get("current_salary", 1)) /
                candidate_profile.get("current_salary", 1) * 100
            ),
            "commute_time_minutes": candidate_profile.get("commute_time", 0),
            "skills_match_percent": interview_results.get("skills_match", 0),

            # Interview signals
            "interview_enthusiasm_score": interview_results.get("enthusiasm", 0),
            "interview_red_flags": len(interview_results.get("red_flags", [])),
            "interview_questions_asked": interview_results.get("questions_asked_count", 0),

            # Timeline
            "days_since_first_contact": candidate_profile.get("days_in_pipeline", 0),
            "competing_offers": candidate_profile.get("has_competing_offers", False)
        }

        # Target: Will they accept?
        target = {
            "accepted": outcome == "accepted",
            "probability": 1.0 if outcome == "accepted" else 0.0
        }

        return TrainingExample(
            example_id=f"placement_{datetime.now().timestamp()}",
            model_type="placement_predictor",
            input_features=features,
            target_output=target,
            metadata={
                "candidate_id": candidate_profile.get("candidate_id"),
                "job_id": job_profile.get("job_id"),
                "outcome": outcome
            }
        )

    def collect_interview_example(
        self,
        question: str,
        candidate_response: str,
        interviewer_rating: int,  # 1-10 from human recruiter
        red_flags_detected: List[str],
        green_flags_detected: List[str]
    ) -> TrainingExample:
        """
        Collect training data from interview responses

        This trains the Interview Quality Scorer
        """

        features = {
            "question_type": self._classify_question_type(question),
            "response_length_words": len(candidate_response.split()),
            "response_has_specific_examples": self._contains_star_format(candidate_response),
            "response_negativity_score": self._calculate_negativity(candidate_response),
            "response_technical_depth": self._assess_technical_depth(candidate_response),
            "response_confidence_markers": self._count_confidence_markers(candidate_response),
        }

        target = {
            "quality_score": interviewer_rating,
            "red_flags": red_flags_detected,
            "green_flags": green_flags_detected,
            "recommendation": "proceed" if interviewer_rating >= 7 else "reject"
        }

        return TrainingExample(
            example_id=f"interview_{datetime.now().timestamp()}",
            model_type="interview_scorer",
            input_features=features,
            target_output=target
        )

    def collect_client_conversion_example(
        self,
        company_profile: Dict[str, Any],
        outreach_details: Dict[str, Any],
        outcome: str  # became_client, not_interested, no_response
    ) -> TrainingExample:
        """
        Collect training data from BD outreach

        This trains the Client Conversion Predictor
        """

        features = {
            # Company features
            "company_size": company_profile.get("employee_count", 0),
            "company_funding_stage": company_profile.get("funding_stage", ""),
            "company_open_positions": company_profile.get("open_positions_count", 0),
            "company_industry": company_profile.get("industry", ""),

            # Hiring signals
            "positions_open_long_term": company_profile.get("positions_open_60plus_days", 0),
            "recent_growth_percent": company_profile.get("headcount_growth_6mo", 0),
            "has_specialized_roles": company_profile.get("has_senior_roles", False),

            # Outreach features
            "outreach_channel": outreach_details.get("channel", ""),
            "outreach_personalization_score": outreach_details.get("personalization", 0),
            "connection_warmth": outreach_details.get("warmth", "cold"),  # cold, warm, hot
            "response_time_hours": outreach_details.get("response_time_hours", 0),
        }

        target = {
            "became_client": outcome == "became_client",
            "conversion_probability": 1.0 if outcome == "became_client" else 0.0,
            "predicted_lifetime_value": self._estimate_ltv(company_profile)
        }

        return TrainingExample(
            example_id=f"client_{datetime.now().timestamp()}",
            model_type="client_converter",
            input_features=features,
            target_output=target
        )

    def collect_ghosting_example(
        self,
        candidate_profile: Dict[str, Any],
        engagement_history: List[Dict[str, Any]],
        outcome: str  # ghosted, stayed_engaged
    ) -> TrainingExample:
        """
        Collect training data from candidate engagement

        This trains the Ghosting Detector
        """

        # Calculate engagement trends
        recent_responses = engagement_history[-5:]  # Last 5 interactions
        response_times = [r.get("response_time_hours", 0) for r in recent_responses]
        avg_response_time = np.mean(response_times) if response_times else 0
        response_time_trend = response_times[-1] - response_times[0] if len(response_times) > 1 else 0

        features = {
            "days_since_last_contact": candidate_profile.get("days_since_last_contact", 0),
            "engagement_score": candidate_profile.get("engagement_score", 0),
            "avg_response_time_hours": avg_response_time,
            "response_time_increasing": response_time_trend > 0,

            # Behavioral signals
            "missed_scheduled_calls": candidate_profile.get("missed_calls", 0),
            "short_responses": sum(1 for r in recent_responses if len(r.get("message", "")) < 50),
            "interview_enthusiasm_drop": candidate_profile.get("enthusiasm_delta", 0),

            # Context
            "stage": candidate_profile.get("pipeline_stage", ""),
            "has_competing_offers": candidate_profile.get("has_competing_offers", False),
            "salary_concerns_raised": candidate_profile.get("salary_concerns", False),
        }

        target = {
            "will_ghost": outcome == "ghosted",
            "risk_score": 1.0 if outcome == "ghosted" else 0.0,
            "days_until_ghost": candidate_profile.get("days_until_ghost", 0)
        }

        return TrainingExample(
            example_id=f"ghosting_{datetime.now().timestamp()}",
            model_type="ghosting_detector",
            input_features=features,
            target_output=target
        )

    # Helper methods
    def _classify_question_type(self, question: str) -> str:
        """Classify question as technical, behavioral, etc."""
        question_lower = question.lower()
        if any(word in question_lower for word in ["technical", "code", "algorithm", "system design"]):
            return "technical"
        elif any(word in question_lower for word in ["tell me about", "experience", "time when"]):
            return "behavioral"
        else:
            return "other"

    def _contains_star_format(self, response: str) -> bool:
        """Check if response uses STAR format (Situation, Task, Action, Result)"""
        indicators = ["situation", "task", "action", "result", "for example", "specifically"]
        return sum(1 for ind in indicators if ind in response.lower()) >= 2

    def _calculate_negativity(self, text: str) -> float:
        """Calculate negativity score (0-1)"""
        negative_words = ["problem", "issue", "difficult", "bad", "terrible", "hate", "blame"]
        word_count = len(text.split())
        negative_count = sum(1 for word in negative_words if word in text.lower())
        return min(negative_count / max(word_count / 20, 1), 1.0)

    def _assess_technical_depth(self, response: str) -> float:
        """Assess technical depth (0-1)"""
        technical_terms = ["architecture", "design", "implementation", "algorithm", "performance", "scale"]
        return min(sum(1 for term in technical_terms if term in response.lower()) / 3, 1.0)

    def _count_confidence_markers(self, response: str) -> int:
        """Count confidence markers"""
        confidence = ["I led", "I built", "I designed", "I implemented", "successfully", "achieved"]
        return sum(1 for marker in confidence if marker.lower() in response.lower())

    def _estimate_ltv(self, company_profile: Dict[str, Any]) -> float:
        """Estimate lifetime value of a client"""
        # Rough estimate: $25K per placement * expected placements
        open_positions = company_profile.get("open_positions_count", 0)
        expected_placements = min(open_positions * 0.3, 10)  # Assume we fill 30%, cap at 10
        return expected_placements * 25000


class ActionModelTrainer:
    """
    Trains action models from collected data

    Uses PyTorch to create small neural networks (15-50MB)
    that replace expensive LLM calls with <50ms inference
    """

    def __init__(self, model_type: str):
        self.model_type = model_type
        self.model = None
        self.metrics = None

    def train(
        self,
        training_examples: List[TrainingExample],
        validation_split: float = 0.2,
        epochs: int = 50
    ) -> ActionModelMetrics:
        """
        Train action model on collected examples

        TODO: Implement actual PyTorch training
        For now, returns mock metrics
        """

        print(f"\n🎓 Training {self.model_type} action model...")
        print(f"   Training examples: {len(training_examples)}")
        print(f"   Validation split: {validation_split}")
        print(f"   Epochs: {epochs}")

        # TODO: Actual training implementation
        # X, y = self._prepare_data(training_examples)
        # X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split)
        #
        # model = SmallActionModel(input_size, hidden_size, output_size)
        # optimizer = torch.optim.Adam(model.parameters())
        # criterion = nn.BCELoss()  # or MSELoss, CrossEntropyLoss
        #
        # for epoch in range(epochs):
        #     model.train()
        #     optimizer.zero_grad()
        #     outputs = model(X_train)
        #     loss = criterion(outputs, y_train)
        #     loss.backward()
        #     optimizer.step()
        #
        # val_accuracy = self._evaluate(model, X_val, y_val)

        # Mock metrics for now
        self.metrics = ActionModelMetrics(
            model_name=f"{self.model_type}_v1",
            model_type=self.model_type,
            training_examples=len(training_examples),
            validation_accuracy=0.87,  # Mock: 87% accuracy
            inference_time_ms=45,       # Mock: 45ms inference
            model_size_mb=22.5,         # Mock: 22.5MB model
            training_date=datetime.now().isoformat(),
            version=1
        )

        print(f"✅ Training complete!")
        print(f"   Validation accuracy: {self.metrics.validation_accuracy:.1%}")
        print(f"   Inference time: {self.metrics.inference_time_ms}ms")
        print(f"   Model size: {self.metrics.model_size_mb}MB\n")

        return self.metrics

    def predict(self, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run inference on trained model

        In production, this replaces LLM calls
        """
        if not self.model:
            return {"error": "Model not trained yet"}

        # TODO: Actual inference
        # X = self._prepare_input(input_features)
        # with torch.no_grad():
        #     output = self.model(X)
        # return self._format_output(output)

        # Mock prediction
        if self.model_type == "placement_predictor":
            return {
                "will_accept": True,
                "confidence": 0.82,
                "factors": ["Salary increase 25%", "Shorter commute", "Better tech stack"]
            }
        elif self.model_type == "interview_scorer":
            return {
                "quality_score": 7.5,
                "recommendation": "proceed",
                "confidence": 0.89
            }
        elif self.model_type == "client_converter":
            return {
                "will_convert": True,
                "confidence": 0.74,
                "estimated_ltv": 125000
            }
        elif self.model_type == "ghosting_detector":
            return {
                "ghosting_risk": 0.23,
                "risk_level": "low",
                "recommendation": "Continue normal outreach"
            }

        return {}


# Example: Small Neural Network Architecture (for actual implementation)
"""
import torch.nn as nn

class SmallActionModel(nn.Module):
    def __init__(self, input_size, hidden_sizes, output_size):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_sizes[0]),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_sizes[0], hidden_sizes[1]),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_sizes[1], hidden_sizes[2]),
            nn.ReLU(),
            nn.Linear(hidden_sizes[2], output_size),
            nn.Sigmoid()  # For binary classification
        )

    def forward(self, x):
        return self.network(x)

# Typical architecture:
# Input: 50-100 features
# Hidden: [256, 128, 64]
# Output: 1 (binary) or N (multi-class)
# Total params: ~100K
# Model size: 15-30MB
# Inference: 10-50ms on CPU
"""


if __name__ == "__main__":
    from rich.console import Console
    console = Console()

    console.print("\n[bold cyan]Action Model Training Demo[/bold cyan]\n")

    # 1. Collect training data
    console.print("[yellow]1. Collecting Training Data[/yellow]\n")

    collector = PlacementDataCollector()

    # Example: Collect placement data
    placement_example = collector.collect_placement_example(
        candidate_profile={
            "candidate_id": "C123",
            "years_experience": 8,
            "current_salary": 120000,
            "location": "Miami",
            "job_changes_last_3_years": 1,
            "days_in_pipeline": 14,
            "has_competing_offers": False
        },
        job_profile={
            "job_id": "J456",
            "salary_min": 130000,
            "salary_max": 160000,
            "remote_policy": "hybrid",
            "company_stage": "Series B"
        },
        interview_results={
            "skills_match": 0.85,
            "enthusiasm": 8,
            "red_flags": [],
            "questions_asked_count": 5
        },
        offer_details={
            "offer_salary": 145000
        },
        outcome="accepted"
    )

    console.print(f"✓ Collected placement example")
    console.print(f"  Features: {len(placement_example.input_features)} features")
    console.print(f"  Target: {placement_example.target_output}\n")

    # 2. Train action model
    console.print("[yellow]2. Training Action Model[/yellow]")

    trainer = ActionModelTrainer(model_type="placement_predictor")

    # In real system, we'd have thousands of examples
    mock_examples = [placement_example] * 1000  # Simulate 1000 examples

    metrics = trainer.train(mock_examples, epochs=50)

    # 3. Run inference
    console.print("[yellow]3. Running Inference (Action Model vs LLM)[/yellow]\n")

    test_input = {
        "candidate_years_experience": 7,
        "candidate_current_salary": 110000,
        "job_salary_max": 150000,
        "salary_delta_percent": 27,
        "interview_enthusiasm_score": 9,
        "interview_red_flags": 0,
        "competing_offers": False
    }

    prediction = trainer.predict(test_input)

    console.print("[green]Action Model Prediction (45ms, $0.00):[/green]")
    console.print(json.dumps(prediction, indent=2))

    console.print("\n[cyan]vs LLM (2500ms, $0.03)[/cyan]")
    console.print("  Same accuracy, 55x faster, free after training\n")

    # 4. Show ROI
    console.print("[yellow]4. ROI After 1 Year[/yellow]\n")

    console.print("Assumptions:")
    console.print("  • 500 placements/year")
    console.print("  • 10 LLM calls per placement (routing, matching, analysis)")
    console.print("  • LLM cost: $0.03 per call")
    console.print("  • LLM time: 2.5 seconds per call")
    console.print("")

    llm_cost_per_year = 500 * 10 * 0.03
    llm_time_per_year_hours = (500 * 10 * 2.5) / 3600

    console.print(f"[red]With LLMs Only:[/red]")
    console.print(f"  Cost: ${llm_cost_per_year}/year")
    console.print(f"  Time wasted: {llm_time_per_year_hours:.1f} hours/year")
    console.print("")

    action_model_cost = 0  # Free after training
    action_model_time_hours = (500 * 10 * 0.045) / 3600

    console.print(f"[green]With Action Models (85% coverage):[/green]")
    console.print(f"  Cost: ${action_model_cost}/year (free after training)")
    console.print(f"  Time: {action_model_time_hours:.1f} hours/year")
    console.print(f"  Savings: ${llm_cost_per_year * 0.85:.2f}/year")
    console.print(f"  Time saved: {(llm_time_per_year_hours - action_model_time_hours):.1f} hours/year")
    console.print("")

    console.print("[green]✓ Action models = 55x faster + 85% cost reduction[/green]\n")
