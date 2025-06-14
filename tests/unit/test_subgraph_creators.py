"""
Tests for subgraph creator classes that build different parts of the conversation analysis workflow.
"""

import pytest
from unittest.mock import Mock, patch
from subgraph_creators import (
    ConcernAnalysisSubgraphCreator,
    ConfigBasedEvaluationSubgraphCreator,
    ScoringSynthesisSubgraphCreator,
)


class TestConcernAnalysisSubgraphCreator:
    """Tests for the concern analysis subgraph creator."""

    def test_subgraph_creation(self, sample_health_config, mock_llm, mock_logger):
        """Test concern analysis subgraph building."""
        creator = ConcernAnalysisSubgraphCreator(
            sample_health_config, mock_llm, mock_logger
        )
        subgraph, entry_node, end_nodes = creator.create_subgraph()

        # Check nodes were added
        assert "identify_conversation_concerns" in subgraph.nodes
        assert "analyze_concern_handling" in subgraph.nodes

        # Check entry and exit points
        assert entry_node == "identify_conversation_concerns"
        assert "analyze_concern_handling" in end_nodes

        # Check subgraph structure
        assert len(subgraph.nodes) == 2

    def test_edge_creation(self, sample_health_config, mock_llm, mock_logger):
        """Test edges are created between nodes."""
        creator = ConcernAnalysisSubgraphCreator(
            sample_health_config, mock_llm, mock_logger
        )
        subgraph, _, _ = creator.create_subgraph()

        # Should have edge from identify to analyze
        assert len(subgraph.edges) >= 1


class TestConfigBasedEvaluationSubgraphCreator:
    """Tests for the config-based evaluation subgraph creator."""

    def test_subgraph_creation(
        self, sample_health_config, mock_llm, mock_logger, mock_node_builders
    ):
        """Test config-based evaluation subgraph building."""
        criteria_builder, indicator_builder = mock_node_builders

        creator = ConfigBasedEvaluationSubgraphCreator(
            sample_health_config, mock_llm, mock_logger
        )

        subgraph, entry_node, end_nodes = creator.create_subgraph()

        # Check entry node
        assert entry_node == "start_evaluations"
        assert "start_evaluations" in subgraph.nodes

        # Should have nodes for config-based criteria and indicators
        config_based_criteria = [
            c
            for c in sample_health_config.evaluation_criteria.values()
            if c.is_config_based
        ]
        expected_nodes = (
            1
            + len(config_based_criteria)
            + len(sample_health_config.quality_indicators)
        )
        assert len(subgraph.nodes) == expected_nodes

    def test_entry_node_connections(
        self, sample_health_config, mock_llm, mock_logger, mock_node_builders
    ):
        """Test that entry node connects to all evaluation nodes."""
        criteria_builder, indicator_builder = mock_node_builders

        creator = ConfigBasedEvaluationSubgraphCreator(
            sample_health_config, mock_llm, mock_logger
        )

        subgraph, entry_node, end_nodes = creator.create_subgraph()

        # Entry node should connect to all evaluation nodes
        edges_from_entry = [edge for edge in subgraph.edges if edge[0] == entry_node]

        # Should have edges to all evaluation and indicator nodes
        config_based_criteria = [
            c
            for c in sample_health_config.evaluation_criteria.values()
            if c.is_config_based
        ]
        expected_connections = len(config_based_criteria) + len(
            sample_health_config.quality_indicators
        )
        assert len(edges_from_entry) == expected_connections

    def test_node_builder_integration(
        self, sample_health_config, mock_llm, mock_logger, mock_node_builders
    ):
        """Test integration with node builders."""
        criteria_builder, indicator_builder = mock_node_builders

        creator = ConfigBasedEvaluationSubgraphCreator(
            sample_health_config, mock_llm, mock_logger
        )

        creator.create_subgraph()

        # Verify node builders were used correctly
        criteria_builder.assert_called_once_with(mock_llm, mock_logger)
        indicator_builder.assert_called_once_with(mock_llm, mock_logger)


class TestScoringSynthesisSubgraphCreator:
    """Tests for the scoring and synthesis subgraph creator."""

    def test_subgraph_creation(self, sample_health_config, mock_llm, mock_logger):
        """Test scoring and synthesis subgraph building."""
        creator = ScoringSynthesisSubgraphCreator(
            sample_health_config, mock_llm, mock_logger
        )

        subgraph, entry_node, end_nodes = creator.create_subgraph()

        # Check nodes
        assert "calculate_health_score" in subgraph.nodes
        assert "synthesize_final_assessment" in subgraph.nodes

        # Check entry and exit points
        assert entry_node == "calculate_health_score"
        assert "synthesize_final_assessment" in end_nodes

        # Check subgraph structure
        assert len(subgraph.nodes) == 2

    def test_synthesis_node_execution(
        self, sample_health_config, mock_llm, mock_logger, sample_health_score
    ):
        """Test assessment synthesis node execution."""
        creator = ScoringSynthesisSubgraphCreator(
            sample_health_config, mock_llm, mock_logger
        )

        with patch("subgraph_creators.call_llm") as mock_call:
            with patch(
                "subgraph_creators.get_health_assessment_synthesis_prompt"
            ) as mock_prompt:
                mock_call.return_value = "Generated assessment content"
                mock_prompt.return_value = "Synthesis prompt"

                state = Mock(
                    health_score=sample_health_score,
                    criteria_evaluations={"test": "data"},
                    quality_indicator_detections={"test": "detection"},
                )
                result = creator._synthesize_health_assessment(state)

                assert "final_assessment" in result
                final_assessment = result["final_assessment"]
                assert "overall_assessment" in final_assessment
                assert (
                    final_assessment["overall_assessment"]
                    == "Generated assessment content"
                )
                assert "criteria_evaluations" in final_assessment
                assert "quality_indicator_detections" in final_assessment
                assert "health_score" in final_assessment

    def test_subgraph_edge_structure(self, sample_health_config, mock_llm, mock_logger):
        """Test that scoring subgraph has correct edge structure."""
        creator = ScoringSynthesisSubgraphCreator(
            sample_health_config, mock_llm, mock_logger
        )

        subgraph, entry_node, end_nodes = creator.create_subgraph()

        # Should have edge from scoring to synthesis
        scoring_to_synthesis_edges = [
            edge
            for edge in subgraph.edges
            if edge[0] == "calculate_health_score"
            and edge[1] == "synthesize_final_assessment"
        ]
        assert len(scoring_to_synthesis_edges) == 1
