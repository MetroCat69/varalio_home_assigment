import pytest
from unittest.mock import patch, Mock
from node_builders import QualityIndicatorNodeBuilder, EvaluationCriteriaNodeBuilder
from models import ConversationAnalysisState


def test_quality_indicator_node_creation(
    mock_llm, mock_logger, sample_indicator_config, mock_structured_response
):
    """Test quality indicator node function creation"""
    builder = QualityIndicatorNodeBuilder(mock_llm, mock_logger)

    with patch(
        "node_builders.call_llm_structured", return_value=mock_structured_response
    ):
        node_func = builder.create_detection_node(sample_indicator_config)

        # Test node function signature
        assert callable(node_func)

        # Test node execution
        state = Mock(spec=ConversationAnalysisState)
        state.transcript = "Test transcript"

        result = node_func(state)

        assert "quality_indicator_detections" in result
        assert sample_indicator_config.name in result["quality_indicator_detections"]


def test_evaluation_criteria_node_creation(
    mock_llm, mock_logger, sample_criteria_config, mock_structured_response
):
    """Test evaluation criteria node function creation"""
    builder = EvaluationCriteriaNodeBuilder(mock_llm, mock_logger)

    with patch(
        "node_builders.call_llm_structured", return_value=mock_structured_response
    ):
        node_func = builder.create_evaluation_node(sample_criteria_config)

        # Test node function signature
        assert callable(node_func)

        # Test node execution
        state = Mock(spec=ConversationAnalysisState)
        state.transcript = "Test transcript"

        result = node_func(state)

        assert "criteria_evaluations" in result
        assert sample_criteria_config.name in result["criteria_evaluations"]


def test_node_llm_integration(mock_llm, mock_logger, sample_indicator_config):
    """Test LLM call integration in nodes"""
    builder = QualityIndicatorNodeBuilder(mock_llm, mock_logger)

    with patch("node_builders.call_llm_structured") as mock_call:
        mock_call.return_value = Mock(
            detected=True, reasoning="Test", confidence="high"
        )

        node_func = builder.create_detection_node(sample_indicator_config)
        state = Mock(transcript="Test transcript")

        node_func(state)

        # Verify LLM was called with proper arguments
        mock_call.assert_called_once()
        call_args = mock_call.call_args
        assert mock_llm in call_args[0]
        assert mock_logger in call_args[0]


def test_prompt_generation_integration(mock_llm, mock_logger, sample_criteria_config):
    """Test prompt generation is called"""
    builder = EvaluationCriteriaNodeBuilder(mock_llm, mock_logger)

    with patch("node_builders.get_criteria_analysis_prompt") as mock_prompt:
        with patch("node_builders.call_llm_structured", return_value=Mock()):
            mock_prompt.return_value = "Generated prompt"

            node_func = builder.create_evaluation_node(sample_criteria_config)
            state = Mock(transcript="Test transcript")

            node_func(state)

            # Verify prompt generation was called
            mock_prompt.assert_called_once_with(
                sample_criteria_config, "Test transcript"
            )
