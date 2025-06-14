import pytest
from score_calculator import ConversationHealthScorer
from models import AssessmentConfidence
from pydantic_model_creators import (
    create_evaluation_criteria_model,
    create_quality_indicator_model,
)


def test_basic_scoring(
    sample_health_config, sample_criteria_config, sample_indicator_config
):
    """Test basic score calculation"""
    scorer = ConversationHealthScorer(sample_health_config)

    # Create proper model instances
    criteria_model = create_evaluation_criteria_model(sample_criteria_config)
    criteria_eval = criteria_model(
        selected_response="positive",
        confidence=AssessmentConfidence.HIGH,
        reasoning="Test reasoning",
    )

    indicator_model = create_quality_indicator_model(sample_indicator_config.name)
    indicator_detection = indicator_model(
        detected=False,
        confidence=AssessmentConfidence.HIGH,
        reasoning="No escalation detected",
    )

    criteria_evals = {"conversation_sentiment": criteria_eval}
    indicator_detections = {"escalation_language": indicator_detection}

    result = scorer.generate_complete_health_score(criteria_evals, indicator_detections)

    assert result["final_score"] >= 0
    assert result["final_score"] <= 100
    assert result["health_level"] in [
        "Excellent",
        "Good",
        "Concerning",
        "Poor",
        "Critical",
    ]


def test_quality_indicator_impact(
    sample_health_config, sample_criteria_config, sample_indicator_config
):
    """Test quality indicators affect score"""
    scorer = ConversationHealthScorer(sample_health_config)

    # Create proper model instances
    criteria_model = create_evaluation_criteria_model(sample_criteria_config)
    criteria_eval = criteria_model(
        selected_response="positive",
        confidence=AssessmentConfidence.HIGH,
        reasoning="Test reasoning",
    )
    criteria_evals = {"conversation_sentiment": criteria_eval}

    indicator_model = create_quality_indicator_model(sample_indicator_config.name)

    # Without indicator
    no_indicator_detection = indicator_model(
        detected=False, confidence=AssessmentConfidence.HIGH, reasoning="No escalation"
    )
    score_without = scorer.generate_complete_health_score(
        criteria_evals, {"escalation_language": no_indicator_detection}
    )

    # With indicator
    with_indicator_detection = indicator_model(
        detected=True,
        confidence=AssessmentConfidence.HIGH,
        reasoning="Escalation detected",
    )
    score_with = scorer.generate_complete_health_score(
        criteria_evals, {"escalation_language": with_indicator_detection}
    )

    assert score_with["final_score"] < score_without["final_score"]


def test_confidence_filtering(sample_health_config, sample_criteria_config):
    """Test low confidence results are excluded"""
    scorer = ConversationHealthScorer(sample_health_config)

    # Create low confidence evaluation
    criteria_model = create_evaluation_criteria_model(sample_criteria_config)
    criteria_eval = criteria_model(
        selected_response="positive",
        confidence=AssessmentConfidence.VERY_LOW,  # Too low
        reasoning="Test reasoning",
    )
    criteria_evals = {"conversation_sentiment": criteria_eval}

    result = scorer.generate_complete_health_score(criteria_evals, {})

    # Should use default multiplier for excluded criteria
    assert result["uncertainty_info"]["excluded_criteria"] == ["conversation_sentiment"]


def test_edge_case_empty_results(sample_health_config):
    """Test with empty evaluation results"""
    scorer = ConversationHealthScorer(sample_health_config)

    result = scorer.generate_complete_health_score({}, {})

    assert 0 <= result["final_score"] <= 100
    assert "health_level" in result
