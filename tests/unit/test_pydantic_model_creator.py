import pytest
from pydantic_model_creators import (
    create_evaluation_criteria_model,
    create_quality_indicator_model,
)
from models import EvaluationCriteriaResult, QualityIndicatorResult


def test_create_evaluation_criteria_model(sample_criteria_config):
    """Test dynamic evaluation criteria model creation"""
    model_class = create_evaluation_criteria_model(sample_criteria_config)

    # Check model name generation
    assert "SentimentAnalysis" in model_class.__name__

    # Test model instantiation with valid data
    instance = model_class(
        selected_response="positive", reasoning="Test reasoning", confidence="high"
    )

    assert instance.selected_response.value == "positive"  # Enum value
    assert instance.reasoning == "Test reasoning"


def test_evaluation_model_enum_generation(sample_criteria_config):
    """Test enum generation from response options"""
    model_class = create_evaluation_criteria_model(sample_criteria_config)

    # Create instance and check enum values
    instance = model_class(
        selected_response="positive", reasoning="Test", confidence="high"
    )

    # Should accept all response options
    for response_key in sample_criteria_config.response_options.keys():
        instance.selected_response = response_key  # Should not raise error


def test_create_quality_indicator_model():
    """Test quality indicator model creation"""
    model_class = create_quality_indicator_model("test_indicator")

    # Check model name generation
    assert "TestIndicator" in model_class.__name__

    # Test model instantiation
    instance = model_class(
        detected=True, reasoning="Pattern detected", confidence="high"
    )

    assert instance.detected is True
    assert instance.reasoning == "Pattern detected"


def test_model_inheritance(sample_criteria_config):
    """Test that created models inherit from base classes"""
    criteria_model = create_evaluation_criteria_model(sample_criteria_config)
    indicator_model = create_quality_indicator_model("test")

    # Should be subclasses of base result types
    assert issubclass(criteria_model, EvaluationCriteriaResult)
    assert issubclass(indicator_model, QualityIndicatorResult)
