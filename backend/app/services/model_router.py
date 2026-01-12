"""Model Router Service for intelligent model selection and cost optimization."""

import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from app.config import settings


class ModelTier(Enum):
    """Model tiers for different task complexities."""

    FAST = "fast"
    STANDARD = "standard"
    PREMIUM = "premium"


class TaskCategory(Enum):
    """Categories of tasks for routing decisions."""

    SIMPLE_QUERY = "simple_query"
    FILE_OPERATION = "file_operation"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    DEBUGGING = "debugging"
    ARCHITECTURE = "architecture"
    DATA_ANALYSIS = "data_analysis"
    TOOL_EXECUTION = "tool_execution"
    CONVERSATION = "conversation"
    PLANNING = "planning"


@dataclass
class TokenUsage:
    """Track token usage for a request."""

    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def calculate_cost(self) -> float:
        """Calculate cost based on model pricing."""
        costs = settings.model_costs.get(self.model, {"input": 0, "output": 0})
        input_cost = (self.input_tokens / 1000) * costs["input"]
        output_cost = (self.output_tokens / 1000) * costs["output"]
        return input_cost + output_cost


@dataclass
class SessionCostTracker:
    """Track costs for a session."""

    session_id: str
    usage_history: List[TokenUsage] = field(default_factory=list)
    total_cost: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def add_usage(self, usage: TokenUsage) -> None:
        """Add token usage to history."""
        self.usage_history.append(usage)
        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens
        self.total_cost += usage.calculate_cost()

    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        return {
            "session_id": self.session_id,
            "total_cost": round(self.total_cost, 6),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_requests": len(self.usage_history),
            "cost_by_model": self._cost_by_model(),
        }

    def _cost_by_model(self) -> Dict[str, float]:
        """Get cost breakdown by model."""
        costs: Dict[str, float] = {}
        for usage in self.usage_history:
            if usage.model not in costs:
                costs[usage.model] = 0.0
            costs[usage.model] += usage.calculate_cost()
        return {k: round(v, 6) for k, v in costs.items()}


class ModelRouter:
    """Routes requests to appropriate models based on task complexity."""

    def __init__(self):
        self.session_trackers: Dict[str, SessionCostTracker] = {}

        self.task_patterns = {
            TaskCategory.SIMPLE_QUERY: [
                r"^(what|who|when|where|how)\s+(is|are|was|were)\b",
                r"^(list|show|display|get)\s+",
                r"^(yes|no|ok|okay|sure|thanks|thank you)",
                r"^(hello|hi|hey)\b",
            ],
            TaskCategory.FILE_OPERATION: [
                r"\b(read|write|edit|create|delete|move|copy)\s+(file|folder|directory)",
                r"\b(cat|ls|mkdir|rm|cp|mv)\b",
                r"\.(?:py|js|ts|tsx|json|yaml|yml|md|txt|html|css)$",
            ],
            TaskCategory.CODE_GENERATION: [
                r"\b(write|create|implement|build|make|generate)\s+(a\s+)?(function|class|component|module|api|endpoint)",
                r"\b(add|implement)\s+(feature|functionality)",
                r"\bnew\s+(file|component|class|function)\b",
            ],
            TaskCategory.CODE_ANALYSIS: [
                r"\b(explain|understand|analyze|review)\s+(this|the|my)?\s*(code|function|class)",
                r"\bwhat\s+does\s+(this|the)\s+(code|function|class)\s+do\b",
                r"\b(find|search|look\s+for)\s+(bugs?|issues?|problems?)",
            ],
            TaskCategory.DEBUGGING: [
                r"\b(debug|fix|solve|resolve)\s+(this|the|my)?\s*(error|bug|issue|problem)",
                r"\b(why|how)\s+(is|does)\s+(this|it)\s+(not\s+)?(work|fail)",
                r"\berror\b.*\b(message|stack\s*trace)\b",
                r"\b(traceback|exception|crash)\b",
            ],
            TaskCategory.ARCHITECTURE: [
                r"\b(design|architect|structure|organize)\s+(the|a|my)?\s*(system|application|project)",
                r"\b(best\s+practice|pattern|approach)\s+for\b",
                r"\b(refactor|restructure|reorganize)\b",
                r"\b(scalab|maintain|extend)ability\b",
            ],
            TaskCategory.DATA_ANALYSIS: [
                r"\b(analyze|process|transform)\s+(data|csv|json|excel)",
                r"\b(chart|graph|plot|visualize)\b",
                r"\b(statistics|mean|median|average|sum|count)\b",
                r"\bpandas|numpy|matplotlib\b",
            ],
            TaskCategory.PLANNING: [
                r"\b(plan|break\s+down|outline|steps?\s+to)\b",
                r"\b(todo|task\s*list|checklist)\b",
                r"\b(how\s+should\s+i|what\s+should\s+i)\b",
            ],
        }

        self.category_to_tier = {
            TaskCategory.SIMPLE_QUERY: ModelTier.FAST,
            TaskCategory.FILE_OPERATION: ModelTier.FAST,
            TaskCategory.TOOL_EXECUTION: ModelTier.FAST,
            TaskCategory.CONVERSATION: ModelTier.FAST,
            TaskCategory.CODE_ANALYSIS: ModelTier.STANDARD,
            TaskCategory.CODE_GENERATION: ModelTier.STANDARD,
            TaskCategory.DATA_ANALYSIS: ModelTier.STANDARD,
            TaskCategory.DEBUGGING: ModelTier.PREMIUM,
            TaskCategory.ARCHITECTURE: ModelTier.PREMIUM,
            TaskCategory.PLANNING: ModelTier.STANDARD,
        }

    def classify_task(self, message: str, context: Optional[Dict[str, Any]] = None) -> Tuple[TaskCategory, float]:
        """Classify a task based on message content and context."""
        message_lower = message.lower().strip()
        scores: Dict[TaskCategory, float] = {cat: 0.0 for cat in TaskCategory}

        for category, patterns in self.task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    scores[category] += 1.0

        if context:
            if context.get("has_code_context"):
                scores[TaskCategory.CODE_ANALYSIS] += 0.5
                scores[TaskCategory.CODE_GENERATION] += 0.3

            if context.get("has_error"):
                scores[TaskCategory.DEBUGGING] += 1.0

            if context.get("is_followup"):
                scores[TaskCategory.CONVERSATION] += 0.5

            if context.get("tool_calls"):
                scores[TaskCategory.TOOL_EXECUTION] += 0.5

        message_length = len(message.split())
        if message_length > 100:
            scores[TaskCategory.ARCHITECTURE] += 0.3
            scores[TaskCategory.PLANNING] += 0.3
        elif message_length < 10:
            scores[TaskCategory.SIMPLE_QUERY] += 0.5

        best_category = max(scores, key=lambda k: scores[k])
        confidence = scores[best_category] / max(sum(scores.values()), 1.0)

        if confidence < 0.3:
            best_category = TaskCategory.CONVERSATION

        return best_category, confidence

    def select_model(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        force_tier: Optional[ModelTier] = None,
        prefer_provider: Optional[str] = None,
    ) -> Tuple[str, ModelTier, TaskCategory]:
        """Select the appropriate model for a task."""
        category, confidence = self.classify_task(message, context)

        if force_tier:
            tier = force_tier
        else:
            tier = self.category_to_tier.get(category, ModelTier.STANDARD)

            if confidence < 0.5 and tier == ModelTier.FAST:
                tier = ModelTier.STANDARD

        provider = prefer_provider
        if not provider:
            if settings.openai_api_key:
                provider = "openai"
            elif settings.anthropic_api_key:
                provider = "anthropic"
            else:
                provider = "openai"

        model = self._get_model_for_tier(tier, provider)

        return model, tier, category

    def _get_model_for_tier(self, tier: ModelTier, provider: str) -> str:
        """Get the model name for a tier and provider."""
        if provider == "openai":
            if tier == ModelTier.FAST:
                return settings.fast_model_openai
            elif tier == ModelTier.STANDARD:
                return settings.standard_model_openai
            else:
                return settings.premium_model_openai
        else:
            if tier == ModelTier.FAST:
                return settings.fast_model_anthropic
            elif tier == ModelTier.STANDARD:
                return settings.standard_model_anthropic
            else:
                return settings.premium_model_anthropic

    def get_max_tokens_for_tier(self, tier: ModelTier) -> int:
        """Get max tokens for a tier."""
        if tier == ModelTier.FAST:
            return settings.fast_model_max_tokens
        elif tier == ModelTier.STANDARD:
            return settings.standard_model_max_tokens
        else:
            return settings.premium_model_max_tokens

    def track_usage(
        self,
        session_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> TokenUsage:
        """Track token usage for a session."""
        if session_id not in self.session_trackers:
            self.session_trackers[session_id] = SessionCostTracker(session_id=session_id)

        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
        )
        self.session_trackers[session_id].add_usage(usage)
        return usage

    def get_session_costs(self, session_id: str) -> Dict[str, Any]:
        """Get cost summary for a session."""
        if session_id not in self.session_trackers:
            return {
                "session_id": session_id,
                "total_cost": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_requests": 0,
                "cost_by_model": {},
            }
        return self.session_trackers[session_id].get_summary()

    def get_all_costs(self) -> Dict[str, Any]:
        """Get cost summary across all sessions."""
        total_cost = 0.0
        total_input = 0
        total_output = 0
        total_requests = 0

        for tracker in self.session_trackers.values():
            total_cost += tracker.total_cost
            total_input += tracker.total_input_tokens
            total_output += tracker.total_output_tokens
            total_requests += len(tracker.usage_history)

        return {
            "total_cost": round(total_cost, 6),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_requests": total_requests,
            "sessions": len(self.session_trackers),
        }

    def estimate_cost(self, message: str, estimated_output_tokens: int = 500) -> Dict[str, Any]:
        """Estimate cost for a message before sending."""
        model, tier, category = self.select_model(message)
        estimated_input_tokens = len(message.split()) * 1.3

        costs = settings.model_costs.get(model, {"input": 0, "output": 0})
        estimated_cost = (
            (estimated_input_tokens / 1000) * costs["input"]
            + (estimated_output_tokens / 1000) * costs["output"]
        )

        return {
            "model": model,
            "tier": tier.value,
            "category": category.value,
            "estimated_input_tokens": int(estimated_input_tokens),
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_cost": round(estimated_cost, 6),
        }


model_router = ModelRouter()
