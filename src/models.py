from typing import Dict, List, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from langgraph.graph.message import add_messages
from utils import merge_dicts


class EvaluationCriteriaType(str, Enum):
    """Type of evaluation criteria - standard automated analysis or custom logic"""

    STANDARD = "standard"
    CUSTOM = "custom"


class QualityIndicatorType(str, Enum):
    """Type of quality indicator based on severity"""

    CRITICAL = "critical"
    WARNING = "warning"
    POSITIVE = "positive"
    INFO = "info"


class ConcernAddressalLevel(str, Enum):
    """How well a concern was addressed in the conversation"""

    NOT_ADDRESSED = "not_addressed"
    PARTIALLY_ADDRESSED = "partially_addressed"
    MOSTLY_ADDRESSED = "mostly_addressed"
    FULLY_ADDRESSED = "fully_addressed"


class AssessmentConfidence(str, Enum):
    """Confidence level in an assessment result"""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"


class QualityIndicatorConfig(BaseModel):
    """Configuration for detecting conversation quality patterns"""

    name: str = Field(description="Unique identifier for this quality indicator")
    type: QualityIndicatorType = Field(description="Severity type of this indicator")
    score_impact: float = Field(description="Points added/deducted when detected")
    description: str = Field(description="Human-readable description")
    minimum_confidence: AssessmentConfidence = Field(
        description="Minimum confidence required to apply this indicator"
    )


class CriteriaResponseOption(BaseModel):
    """Possible response option for an evaluation criteria"""

    score_multiplier: float = Field(
        description="Score multiplier (-1.0-1.0) for this response", ge=-1, le=1
    )
    description: str = Field(description="What this response option represents")


class EvaluationCriteriaConfig(BaseModel):
    """Configuration for a conversation evaluation criteria"""

    name: str = Field(description="Unique identifier for this criteria")
    description: str = Field(description="Human-readable description")
    prompt: str = Field(description="LLM prompt for analyzing this criteria")
    max_points: float = Field(
        description="Maximum points this criteria can contribute", gt=0
    )
    response_options: Dict[str, CriteriaResponseOption] = Field(
        description="Possible response options and their score multipliers"
    )
    default_score_multiplier: float = Field(
        description="Default score when criteria cannot be evaluated", ge=0, le=1
    )
    is_config_based: bool = Field(
        description="Whether to automatically create analysis node for this criteria"
    )
    minimum_confidence: AssessmentConfidence = Field(
        description="Minimum confidence required for scoring"
    )

    @field_validator("response_options")
    def validate_response_options(cls, v):
        if not v:
            raise ValueError("At least one response option must be provided")
        return v


class HealthScoreRange(BaseModel):
    """Score range definition for conversation health levels"""

    min_score: int = Field(description="Minimum score for this health level")
    max_score: int = Field(description="Maximum score for this health level")
    label: str = Field(description="Human-readable label for this health level")
    color: str = Field(description="Color indicator for UI display")
    description: str = Field(description="Description of what this health level means")

    @field_validator("max_score")
    def validate_score_range(cls, v, info):
        if info.data and "min_score" in info.data and v <= info.data["min_score"]:
            raise ValueError("max_score must be greater than min_score")
        return v


class ConversationConcern(BaseModel):
    """A concern identified in the conversation"""

    description: str = Field(description="Description of the concern")
    addressal_level: ConcernAddressalLevel = Field(
        description="How well this concern was addressed"
    )
    reasoning: str = Field(description="Explanation for the addressal level assessment")


class IdentifiedConcerns(BaseModel):
    """Collection of concerns found in a conversation"""

    concerns: List[ConversationConcern] = Field(
        description="List of identified concerns"
    )


class ConcernHandlingAssessment(BaseModel):
    """Assessment of how well concerns were handled overall"""

    overall_quality: str = Field(description="Overall quality assessment")
    reasoning: str = Field(description="Detailed reasoning for the assessment")


class EvaluationCriteriaResult(BaseModel):
    """Result of evaluating a conversation against specific criteria"""

    selected_response: Enum = Field(description="The selected response option")
    reasoning: str = Field(description="Explanation of why this response was selected")
    confidence: AssessmentConfidence = Field(
        description="Confidence in this evaluation"
    )


class QualityIndicatorResult(BaseModel):
    """Result of checking for a quality indicator pattern"""

    detected: bool = Field(description="Whether the pattern was detected")
    reasoning: str = Field(description="Explanation for the detection result")
    confidence: AssessmentConfidence = Field(description="Confidence in this detection")


class ConversationHealthConfig(BaseModel):
    """Complete configuration for conversation health assessment"""

    evaluation_criteria: Dict[str, EvaluationCriteriaConfig] = Field(
        description="All evaluation criteria configurations"
    )
    quality_indicators: List[QualityIndicatorConfig] = Field(
        description="All quality indicator configurations"
    )
    health_score_ranges: Dict[str, HealthScoreRange] = Field(
        description="Health score range definitions"
    )
    confidence_level_weights: Dict[AssessmentConfidence, int] = Field(
        description="Numeric weights for confidence levels"
    )

    @field_validator("health_score_ranges")
    def validate_health_score_ranges(cls, v):
        if not v:
            raise ValueError("At least one health score range must be provided")
        return v


# Result types for the scoring system
class CriteriaEvaluationResult(TypedDict):
    """Detailed result for a single evaluation criteria"""

    criteria_name: str
    selected_response: str
    earned_points: float
    score_multiplier: float
    reasoning: str
    confidence: AssessmentConfidence
    included_in_final_score: bool


class QualityIndicatorDetectionResult(TypedDict):
    """Detailed result for a single quality indicator"""

    indicator_name: str
    pattern_detected: bool
    score_impact: float
    reasoning: str
    confidence: AssessmentConfidence
    included_in_final_score: bool


class ScoringUncertainty(TypedDict):
    """Information about what was excluded due to low confidence"""

    excluded_criteria: List[str]
    excluded_indicators: List[str]


class ConversationHealthScore(TypedDict):
    """Complete scoring breakdown for a conversation"""

    criteria_results: Dict[str, CriteriaEvaluationResult]
    total_criteria_points: float
    indicator_results: Dict[str, QualityIndicatorDetectionResult]
    total_indicator_adjustment: float
    raw_score: float
    final_score: int
    health_level: str
    health_color: str
    uncertainty_info: ScoringUncertainty


# Collections for analysis results
CriteriaEvaluations = Dict[str, EvaluationCriteriaResult]
QualityIndicatorDetections = Dict[str, QualityIndicatorResult]
CriteriaAnalysisNodeOutput = Dict[str, CriteriaEvaluations]
QualityIndicatorNodeOutput = Dict[str, QualityIndicatorDetections]


class ConversationHealthAssessment(TypedDict):
    """Final comprehensive health assessment"""

    criteria_evaluations: CriteriaEvaluations
    quality_indicator_detections: QualityIndicatorDetections
    health_score: ConversationHealthScore
    overall_assessment: str
    final_score: float


class ConversationAnalysisState(BaseModel):
    """State object for the conversation analysis workflow"""

    transcript: str = ""
    identified_concerns: IdentifiedConcerns = Field(
        default_factory=lambda: IdentifiedConcerns(concerns=[])
    )
    criteria_evaluations: Annotated[CriteriaEvaluations, merge_dicts] = Field(
        default_factory=dict
    )
    quality_indicator_detections: Annotated[QualityIndicatorDetections, merge_dicts] = (
        Field(default_factory=dict)
    )
    health_score: ConversationHealthScore = Field(default_factory=dict)  # type: ignore
    final_assessment: ConversationHealthAssessment = Field(default_factory=dict)  # type: ignore
