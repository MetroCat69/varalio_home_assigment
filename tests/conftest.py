"""
Comprehensive test fixtures for the Conversation Health Analysis System.

This conftest.py provides all necessary fixtures for testing the conversation health
analysis system, including mocks, sample data, and configuration objects.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from logging import Logger
from typing import Dict, List, Any
from models import (
    ConversationAnalysisState,
    ConversationHealthConfig,
    EvaluationCriteriaConfig,
    QualityIndicatorConfig,
    CriteriaResponseOption,
    HealthScoreRange,
    EvaluationCriteriaType,
    QualityIndicatorType,
    AssessmentConfidence,
    IdentifiedConcerns,
    ConversationHealthScore,
    ConversationHealthAssessment,
)


# ==================== CORE SYSTEM MOCKS ====================


@pytest.fixture
def mock_llm():
    """Mock BaseLanguageModel for testing LLM interactions"""
    llm = Mock()
    llm.invoke.return_value = Mock(content="Mock LLM response")
    llm.with_structured_output.return_value = llm
    return llm


@pytest.fixture
def mock_logger():
    """Mock Logger for testing logging functionality"""
    logger = Mock(spec=Logger)
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def mock_structured_response():
    """Mock structured response from LLM with typical fields"""
    response = Mock()
    response.selected_response = "positive"
    response.reasoning = "Test reasoning for positive assessment"
    response.confidence = AssessmentConfidence.HIGH
    response.detected = True
    response.score_multiplier = 1.0
    return response


@pytest.fixture
def mock_llm_call_structured():
    """Mock for call_llm_structured function"""
    with patch("llm.call_llm_structured") as mock:
        yield mock


@pytest.fixture
def mock_llm_call():
    """Mock for call_llm function"""
    with patch("llm.call_llm") as mock:
        mock.return_value = "Generated assessment content"
        yield mock


# ==================== CONFIGURATION FIXTURES ====================


@pytest.fixture
def sample_criteria_config():
    """Sample evaluation criteria config for sentiment analysis"""
    return EvaluationCriteriaConfig(
        name="conversation_sentiment",
        description="Analyze overall conversation sentiment and tone",
        prompt="Evaluate the emotional tone and sentiment throughout this conversation",
        max_points=40,
        response_options={
            "positive": CriteriaResponseOption(
                score_multiplier=1.0,
                description="Positive, friendly, constructive tone",
            ),
            "neutral": CriteriaResponseOption(
                score_multiplier=0.6, description="Neutral, professional tone"
            ),
            "negative": CriteriaResponseOption(
                score_multiplier=0.2,
                description="Negative, hostile, or unconstructive tone",
            ),
        },
        criteria_type=EvaluationCriteriaType.STANDARD,
        default_score_multiplier=0.5,
        auto_create_analysis_node=True,
        is_config_based=True,
        minimum_confidence=AssessmentConfidence.HIGH,
    )


@pytest.fixture
def sample_concern_handling_criteria():
    """Sample criteria config for concern handling quality"""
    return EvaluationCriteriaConfig(
        name="concern_handling_quality",
        description="Evaluate how well concerns and issues were addressed",
        prompt="Assess the quality of concern resolution in this conversation",
        max_points=35,
        response_options={
            "excellent": CriteriaResponseOption(
                score_multiplier=1.0, description="All concerns thoroughly addressed"
            ),
            "good": CriteriaResponseOption(
                score_multiplier=0.8, description="Most concerns adequately addressed"
            ),
            "poor": CriteriaResponseOption(
                score_multiplier=0.3, description="Concerns poorly addressed or ignored"
            ),
        },
        criteria_type=EvaluationCriteriaType.STANDARD,
        default_score_multiplier=0.5,
        auto_create_analysis_node=False,  # Handled by custom subgraph
        is_config_based=False,
        minimum_confidence=AssessmentConfidence.MODERATE,
    )


@pytest.fixture
def sample_indicator_config():
    """Sample quality indicator config for escalation detection"""
    return QualityIndicatorConfig(
        name="escalation_language",
        type=QualityIndicatorType.CRITICAL,
        score_impact=-15,
        description="Detect escalating language or hostile behavior",
        minimum_confidence=AssessmentConfidence.HIGH,
    )


@pytest.fixture
def sample_positive_indicator_config():
    """Sample positive quality indicator config"""
    return QualityIndicatorConfig(
        name="mutual_collaboration",
        type=QualityIndicatorType.POSITIVE,
        score_impact=10,
        description="Detect collaborative problem-solving behavior",
        minimum_confidence=AssessmentConfidence.MODERATE,
    )


@pytest.fixture
def sample_health_config(
    sample_criteria_config,
    sample_concern_handling_criteria,
    sample_indicator_config,
    sample_positive_indicator_config,
):
    """Complete conversation health configuration with all required components"""
    return ConversationHealthConfig(
        evaluation_criteria={
            "conversation_sentiment": sample_criteria_config,
            "concern_handling_quality": sample_concern_handling_criteria,
        },
        quality_indicators=[
            sample_indicator_config,
            sample_positive_indicator_config,
        ],
        health_score_ranges={
            "excellent": HealthScoreRange(
                min_score=85,
                max_score=100,
                label="Excellent",
                color="green",
                description="Outstanding conversation quality",
            ),
            "good": HealthScoreRange(
                min_score=70,
                max_score=84,
                label="Good",
                color="blue",
                description="Good conversation with minor issues",
            ),
            "concerning": HealthScoreRange(
                min_score=50,
                max_score=69,
                label="Concerning",
                color="yellow",
                description="Conversation needs attention",
            ),
            "poor": HealthScoreRange(
                min_score=25,
                max_score=49,
                label="Poor",
                color="orange",
                description="Poor conversation quality",
            ),
            "critical": HealthScoreRange(
                min_score=0,
                max_score=24,
                label="Critical",
                color="red",
                description="Critical conversation issues",
            ),
        },
        confidence_level_weights={
            AssessmentConfidence.VERY_HIGH: 5,
            AssessmentConfidence.HIGH: 4,
            AssessmentConfidence.MODERATE: 3,
            AssessmentConfidence.LOW: 2,
            AssessmentConfidence.VERY_LOW: 1,
        },
    )


# ==================== SAMPLE DATA FIXTURES ====================


@pytest.fixture
def sample_transcript():
    """Realistic conversation transcript for testing"""
    return """Customer: Hi, I'm having trouble with my recent order. It hasn't arrived yet and I'm getting worried.

Agent: Hello! I'm sorry to hear about the delay with your order. I'd be happy to help you track it down. Can you please provide me with your order number?

Customer: Yes, it's ORD-12345. I placed it last week and was told it would arrive by today.

Agent: Thank you for that information. Let me check on order ORD-12345 for you right away. 

*Agent checks system*

Agent: I can see your order here. It looks like there was a delay at our fulfillment center, but your package is actually out for delivery today. You should receive it within the next few hours.

Customer: Oh that's a relief! Thank you for checking on that. I was starting to worry it was lost.

Agent: Absolutely no problem! I completely understand your concern. Is there anything else I can help you with today?

Customer: No, that's all I needed. Thanks for your help!

Agent: You're very welcome! Have a great day!"""


@pytest.fixture
def sample_problematic_transcript():
    """Conversation transcript with issues for testing negative scenarios"""
    return """Customer: This is ridiculous! I've been waiting on hold for 45 minutes and nobody can help me!

Agent: Look, I'm doing the best I can here. What's your problem?

Customer: My problem is that you people don't know how to do your jobs! I ordered something 3 weeks ago and it never came!

Agent: Well did you check the tracking number?

Customer: Of course I checked it! It says delivered but I never got it!

Agent: Then that's not our problem. Take it up with the shipping company.

Customer: Are you serious right now? This is your responsibility!

Agent: I've told you what to do. Is there anything else?

Customer: This is the worst customer service I've ever experienced!

Agent: *hangs up*"""


@pytest.fixture
def sample_conversation_state(sample_transcript):
    """Basic conversation analysis state with transcript"""
    return ConversationAnalysisState(
        messages=[],
        transcript=sample_transcript,
        criteria_evaluations={},
        quality_indicator_detections={},
        identified_concerns=None,
        health_score=None,
        final_assessment=None,
    )


@pytest.fixture
def sample_identified_concerns():
    """Sample identified concerns from transcript analysis"""
    return IdentifiedConcerns(
        concerns=[
            "Customer worried about delayed order delivery",
            "Potential fulfillment center delays affecting customer expectations",
        ],
        urgency_level="medium",
        participant_concerns={
            "customer": ["Order delivery delay", "Lack of proactive communication"],
            "agent": ["System delays", "Customer satisfaction"],
        },
    )


# ==================== EVALUATION RESULT FIXTURES ====================


@pytest.fixture
def sample_criteria_result():
    """Sample evaluation criteria result with positive outcome"""
    return {
        "selected_response": "positive",
        "reasoning": "Agent demonstrated empathy and provided clear, helpful information to resolve customer concern",
        "confidence": AssessmentConfidence.HIGH,
        "score_multiplier": 1.0,
    }


@pytest.fixture
def sample_negative_criteria_result():
    """Sample evaluation criteria result with negative outcome"""
    return {
        "selected_response": "negative",
        "reasoning": "Agent was dismissive and failed to take responsibility for the issue",
        "confidence": AssessmentConfidence.HIGH,
        "score_multiplier": 0.2,
    }


@pytest.fixture
def sample_indicator_result():
    """Sample quality indicator result detecting an issue"""
    return {
        "detected": True,
        "reasoning": "Customer expressed frustration with 'This is ridiculous!' indicating escalation",
        "confidence": AssessmentConfidence.HIGH,
    }


@pytest.fixture
def sample_positive_indicator_result():
    """Sample quality indicator result detecting positive behavior"""
    return {
        "detected": True,
        "reasoning": "Agent and customer worked together collaboratively to resolve the delivery issue",
        "confidence": AssessmentConfidence.MODERATE,
    }


@pytest.fixture
def sample_health_score():
    """Sample conversation health score"""
    return ConversationHealthScore(
        criteria_results={
            "conversation_sentiment": 36.0,  # 40 * 0.9 (positive with high confidence)
            "concern_handling_quality": 28.0,  # 35 * 0.8 (good handling)
        },
        total_criteria_points=64.0,
        indicator_results={
            "escalation_language": 0,  # Not detected
            "mutual_collaboration": 8,  # Detected with moderate confidence
        },
        total_indicator_adjustment=8,
        raw_score=72.0,
        final_score=80,  # After confidence adjustments
        health_level="good",
        health_color="blue",
        uncertainty_info={
            "low_confidence_evaluations": [],
            "conflicting_indicators": [],
            "missing_data_impact": "minimal",
        },
    )


@pytest.fixture
def sample_health_assessment(sample_health_score):
    """Sample complete health assessment"""
    return ConversationHealthAssessment(
        criteria_evaluations={
            "conversation_sentiment": {
                "selected_response": "positive",
                "reasoning": "Professional and empathetic tone throughout",
                "confidence": AssessmentConfidence.HIGH,
            }
        },
        quality_indicator_detections={
            "escalation_language": {
                "detected": False,
                "reasoning": "No hostile or escalating language detected",
                "confidence": AssessmentConfidence.HIGH,
            }
        },
        health_score=sample_health_score,
        overall_assessment="This conversation demonstrates good customer service practices with effective issue resolution and professional communication.",
        final_score=80,
    )


# ==================== SCORING TEST FIXTURES ====================


@pytest.fixture
def sample_criteria_evaluation_for_scoring():
    """Sample criteria evaluation compatible with scoring system"""
    from pydantic_model_creators import create_evaluation_criteria_model
    from models import AssessmentConfidence

    # Create a mock evaluation that matches what the scorer expects
    mock_eval = Mock()
    mock_eval.selected_response = "positive"
    mock_eval.confidence = AssessmentConfidence.HIGH
    mock_eval.reasoning = "Good sentiment detected"
    return mock_eval


@pytest.fixture
def sample_indicator_detection_for_scoring():
    """Sample indicator detection compatible with scoring system"""
    from pydantic_model_creators import create_quality_indicator_model
    from models import AssessmentConfidence

    # Create a mock detection that matches what the scorer expects
    mock_detection = Mock()
    mock_detection.detected = False
    mock_detection.confidence = AssessmentConfidence.HIGH
    mock_detection.reasoning = "No escalation detected"
    return mock_detection


@pytest.fixture
def scoring_compatible_health_config():
    """Health config with criteria names that match the scoring test expectations"""
    return ConversationHealthConfig(
        evaluation_criteria={
            "conversation_sentiment": EvaluationCriteriaConfig(
                name="conversation_sentiment",
                description="Test sentiment for scoring",
                prompt="Analyze sentiment",
                max_points=40,
                response_options={
                    "positive": CriteriaResponseOption(
                        score_multiplier=1.0, description="Positive"
                    ),
                    "neutral": CriteriaResponseOption(
                        score_multiplier=0.6, description="Neutral"
                    ),
                    "negative": CriteriaResponseOption(
                        score_multiplier=0.2, description="Negative"
                    ),
                },
                criteria_type=EvaluationCriteriaType.STANDARD,
                default_score_multiplier=0.5,
                auto_create_analysis_node=True,
                is_config_based=True,
                minimum_confidence=AssessmentConfidence.HIGH,
            ),
        },
        quality_indicators=[
            QualityIndicatorConfig(
                name="escalation_language",
                type=QualityIndicatorType.CRITICAL,
                score_impact=-15,
                description="Test escalation",
                minimum_confidence=AssessmentConfidence.HIGH,
            )
        ],
        health_score_ranges={
            "excellent": HealthScoreRange(85, 100, "Excellent", "green", "Great"),
            "good": HealthScoreRange(70, 84, "Good", "blue", "Good"),
            "poor": HealthScoreRange(0, 69, "Poor", "red", "Poor"),
        },
        confidence_level_weights={
            AssessmentConfidence.VERY_HIGH: 5,
            AssessmentConfidence.HIGH: 4,
            AssessmentConfidence.MODERATE: 3,
            AssessmentConfidence.LOW: 2,
            AssessmentConfidence.VERY_LOW: 1,
        },
    )


# ==================== BUILDER AND GRAPH FIXTURES ====================


@pytest.fixture
def mock_subgraph_creator():
    """Mock subgraph creator for testing graph building"""
    creator = Mock()
    mock_subgraph = Mock()
    mock_subgraph.nodes = {"test_node": Mock(runnable=Mock())}
    mock_subgraph.edges = []
    creator.create_subgraph.return_value = (mock_subgraph, "test_node", ["test_node"])
    return creator


@pytest.fixture
def mock_node_builders():
    """Mock node builders for evaluation testing"""
    with patch("node_builders.EvaluationCriteriaNodeBuilder") as criteria_builder:
        with patch("node_builders.QualityIndicatorNodeBuilder") as indicator_builder:
            criteria_builder.return_value.create_evaluation_node.return_value = Mock()
            indicator_builder.return_value.create_detection_node.return_value = Mock()
            yield criteria_builder, indicator_builder


# ==================== FILE SYSTEM AND CONFIG FIXTURES ====================


@pytest.fixture
def valid_config_json():
    """Valid JSON configuration for file loading tests"""
    return """{
        "evaluation_criteria": {
            "sentiment": {
                "name": "sentiment",
                "description": "Sentiment analysis",
                "prompt": "Analyze sentiment",
                "max_points": 40,
                "response_options": {
                    "positive": {"score_multiplier": 1.0, "description": "Positive"},
                    "neutral": {"score_multiplier": 0.6, "description": "Neutral"},
                    "negative": {"score_multiplier": 0.2, "description": "Negative"}
                },
                "criteria_type": "standard",
                "default_score_multiplier": 0.5,
                "auto_create_analysis_node": true,
                "is_config_based": true,
                "minimum_confidence": "high"
            }
        },
        "quality_indicators": [
            {
                "name": "escalation_language",
                "type": "critical",
                "score_impact": -15,
                "description": "Detect escalating language",
                "minimum_confidence": "high"
            }
        ],
        "health_score_ranges": {
            "excellent": {
                "min_score": 85, "max_score": 100, "label": "Excellent",
                "color": "green", "description": "Outstanding quality"
            },
            "good": {
                "min_score": 70, "max_score": 84, "label": "Good",
                "color": "blue", "description": "Good quality"
            }
        },
        "confidence_level_weights": {
            "very_high": 5, "high": 4, "moderate": 3, "low": 2, "very_low": 1
        }
    }"""


@pytest.fixture
def invalid_config_json():
    """Invalid JSON for testing error handling"""
    return '{"invalid": json syntax missing bracket'


@pytest.fixture
def incomplete_config_json():
    """JSON missing required fields"""
    return """{
        "evaluation_criteria": {},
        "quality_indicators": []
    }"""


# ==================== INTEGRATION TEST FIXTURES ====================


@pytest.fixture
def mock_conversation_health_scorer():
    """Mock ConversationHealthScorer for testing"""
    with patch("score_calculator.ConversationHealthScorer") as mock_scorer:
        mock_instance = Mock()
        mock_instance.generate_complete_health_score.return_value = {
            "final_score": 75,
            "health_level": "good",
            "health_color": "blue",
            "criteria_results": {},
            "indicator_results": {},
            "total_criteria_points": 60,
            "total_indicator_adjustment": 15,
            "raw_score": 75,
            "uncertainty_info": {},
        }
        mock_scorer.return_value = mock_instance
        yield mock_scorer


@pytest.fixture
def mock_prompt_functions():
    """Mock all prompt generation functions"""
    with patch("prompts.get_concern_identification_prompt") as mock_concern_prompt:
        with patch("prompts.get_concern_resolution_prompt") as mock_resolution_prompt:
            with patch("prompts.get_criteria_analysis_prompt") as mock_criteria_prompt:
                with patch(
                    "prompts.get_quality_indicator_prompt"
                ) as mock_indicator_prompt:
                    with patch(
                        "prompts.get_health_assessment_synthesis_prompt"
                    ) as mock_synthesis_prompt:
                        mock_concern_prompt.return_value = "Identify concerns prompt"
                        mock_resolution_prompt.return_value = "Resolve concerns prompt"
                        mock_criteria_prompt.return_value = "Criteria analysis prompt"
                        mock_indicator_prompt.return_value = (
                            "Indicator detection prompt"
                        )
                        mock_synthesis_prompt.return_value = (
                            "Assessment synthesis prompt"
                        )
                        yield {
                            "concern": mock_concern_prompt,
                            "resolution": mock_resolution_prompt,
                            "criteria": mock_criteria_prompt,
                            "indicator": mock_indicator_prompt,
                            "synthesis": mock_synthesis_prompt,
                        }


# ==================== UTILITY FIXTURES ====================


@pytest.fixture
def patch_pydantic_model_creators():
    """Patch pydantic model creation functions"""
    with patch(
        "pydantic_model_creators.create_evaluation_criteria_model"
    ) as mock_criteria_model:
        with patch(
            "pydantic_model_creators.create_quality_indicator_model"
        ) as mock_indicator_model:
            # Create mock model classes that can be instantiated
            mock_criteria_class = Mock()
            mock_criteria_class.return_value = Mock(
                selected_response="positive",
                confidence=AssessmentConfidence.HIGH,
                reasoning="Test reasoning",
            )
            mock_criteria_model.return_value = mock_criteria_class

            mock_indicator_class = Mock()
            mock_indicator_class.return_value = Mock(
                detected=True,
                confidence=AssessmentConfidence.HIGH,
                reasoning="Test detection reasoning",
            )
            mock_indicator_model.return_value = mock_indicator_class

            yield mock_criteria_model, mock_indicator_model


@pytest.fixture(autouse=True)
def reset_mocks():
    """Automatically reset all mocks after each test"""
    yield
    # This runs after each test - clear any mock state


# ==================== GRAPH BUILDER SPECIFIC FIXTURES ====================


@pytest.fixture
def mock_unique_subgraphs():
    """Mock subgraphs with unique node names for testing graph builder edge cases"""
    from langgraph.graph import StateGraph

    subgraph1 = StateGraph(ConversationAnalysisState)
    subgraph1.add_node("unique_node_1", lambda state: {"source": "first"})

    subgraph2 = StateGraph(ConversationAnalysisState)
    subgraph2.add_node("unique_node_2", lambda state: {"source": "second"})

    return subgraph1, subgraph2


# ==================== PERFORMANCE TEST FIXTURES ====================


@pytest.fixture
def large_transcript():
    """Large transcript for performance testing"""
    base_conversation = """Customer: I have an issue.
Agent: I can help with that.
Customer: Thank you.
Agent: You're welcome."""

    # Repeat the conversation 100 times to create a large transcript
    return "\n\n".join(
        [f"--- Conversation {i} ---\n{base_conversation}" for i in range(100)]
    )


@pytest.fixture
def complex_health_config():
    """Complex configuration with many criteria and indicators for performance testing"""
    criteria = {}
    indicators = []

    # Create 10 different criteria
    for i in range(10):
        criteria[f"criteria_{i}"] = EvaluationCriteriaConfig(
            name=f"criteria_{i}",
            description=f"Test criteria {i}",
            prompt=f"Evaluate aspect {i}",
            max_points=10,
            response_options={
                "good": CriteriaResponseOption(
                    score_multiplier=1.0, description="Good"
                ),
                "bad": CriteriaResponseOption(score_multiplier=0.0, description="Bad"),
            },
            criteria_type=EvaluationCriteriaType.STANDARD,
            default_score_multiplier=0.5,
            auto_create_analysis_node=True,
            is_config_based=True,
            minimum_confidence=AssessmentConfidence.MODERATE,
        )

    # Create 15 different indicators
    for i in range(15):
        indicators.append(
            QualityIndicatorConfig(
                name=f"indicator_{i}",
                type=(
                    QualityIndicatorType.CRITICAL
                    if i % 2 == 0
                    else QualityIndicatorType.POSITIVE
                ),
                score_impact=-5 if i % 2 == 0 else 5,
                description=f"Test indicator {i}",
                minimum_confidence=AssessmentConfidence.LOW,
            )
        )

    return ConversationHealthConfig(
        evaluation_criteria=criteria,
        quality_indicators=indicators,
        health_score_ranges={
            "excellent": HealthScoreRange(85, 100, "Excellent", "green", "Great"),
            "good": HealthScoreRange(70, 84, "Good", "blue", "Good"),
            "poor": HealthScoreRange(0, 69, "Poor", "red", "Poor"),
        },
        confidence_level_weights={
            AssessmentConfidence.VERY_HIGH: 5,
            AssessmentConfidence.HIGH: 4,
            AssessmentConfidence.MODERATE: 3,
            AssessmentConfidence.LOW: 2,
            AssessmentConfidence.VERY_LOW: 1,
        },
    )
