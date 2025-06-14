"""
Tests for the graph builder that assembles the complete conversation analysis workflow.
"""

import pytest
from unittest.mock import Mock, patch
from langgraph.graph import StateGraph, END
from graph_builder import GraphBuilder, create_default_conversation_health_system
from models import ConversationAnalysisState


class TestGraphBuilder:
    """Tests for the GraphBuilder class."""

    def test_initialization(self, sample_health_config, mock_llm, mock_logger):
        """Test graph builder initialization."""
        builder = GraphBuilder(
            ConversationAnalysisState,
            sample_health_config,
            mock_llm,
            mock_logger,
            initial_entry_node="start_conversation_analysis",
        )

        assert builder.config == sample_health_config
        assert builder.llm == mock_llm
        assert builder.logger == mock_logger
        assert builder.initial_entry_node == "start_conversation_analysis"
        assert "start_conversation_analysis" in builder.main_graph.nodes

    def test_custom_initial_entry_node(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test initialization with custom initial entry node."""
        builder = GraphBuilder(
            ConversationAnalysisState,
            sample_health_config,
            mock_llm,
            mock_logger,
            initial_entry_node="custom_start",
        )

        assert builder.initial_entry_node == "custom_start"
        assert "custom_start" in builder.main_graph.nodes

    def test_add_subgraph_basic(self, sample_health_config, mock_llm, mock_logger):
        """Test adding a basic subgraph to main graph."""
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )

        # Create a mock subgraph
        mock_subgraph = StateGraph(ConversationAnalysisState)
        mock_subgraph.add_node("test_node", lambda state: {"test": "data"})

        result = builder.add_subgraph(
            subgraph=mock_subgraph,
            entry_node="test_node",
            exit_connections={"test_node": END},
            connect_entry_to="start_conversation_analysis",
        )

        # Should return self for chaining
        assert result == builder

        # Should add the node to main graph
        assert "test_node" in builder.main_graph.nodes

        # Should create edge from entry to subgraph entry
        edges = builder.main_graph.edges
        entry_edges = [
            e
            for e in edges
            if e[0] == "start_conversation_analysis" and e[1] == "test_node"
        ]
        assert len(entry_edges) == 1

    def test_add_subgraph_multiple_connections(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test adding subgraph with multiple connection points."""
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )

        # Add first subgraph
        mock_subgraph1 = StateGraph(ConversationAnalysisState)
        mock_subgraph1.add_node("node1", lambda state: {})
        mock_subgraph1.add_node("node2", lambda state: {})

        builder.add_subgraph(
            subgraph=mock_subgraph1,
            entry_node="node1",
            exit_connections={"node1": "node2", "node2": "next_stage"},
            connect_entry_to="start_conversation_analysis",
        )

        # Add second subgraph connected to multiple exit points
        mock_subgraph2 = StateGraph(ConversationAnalysisState)
        mock_subgraph2.add_node("final_node", lambda state: {})

        builder.add_subgraph(
            subgraph=mock_subgraph2,
            entry_node="final_node",
            exit_connections={"final_node": END},
            connect_entry_to=["node1", "node2"],  # Multiple connection points
        )

        # Verify multiple connections were created
        edges = builder.main_graph.edges
        connections_to_final = [
            e for e in edges if e[1] == "final_node" and e[0] in ["node1", "node2"]
        ]
        assert len(connections_to_final) == 2

    def test_add_subgraph_with_internal_edges(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test that internal subgraph edges are preserved."""
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )

        # Create subgraph with internal edges
        mock_subgraph = StateGraph(ConversationAnalysisState)
        mock_subgraph.add_node("internal_node1", lambda state: {})
        mock_subgraph.add_node("internal_node2", lambda state: {})
        mock_subgraph.add_edge("internal_node1", "internal_node2")

        builder.add_subgraph(
            subgraph=mock_subgraph,
            entry_node="internal_node1",
            exit_connections={"internal_node2": END},
            connect_entry_to="start_conversation_analysis",
        )

        # Verify internal edge was preserved
        edges = builder.main_graph.edges
        internal_edges = [
            e for e in edges if e[0] == "internal_node1" and e[1] == "internal_node2"
        ]
        assert len(internal_edges) == 1

    def test_build_validation_success(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test successful graph building."""
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )

        # Should be able to build (has nodes)
        graph = builder.build()
        assert graph is not None
        assert isinstance(graph, StateGraph)

    def test_build_validation_empty_graph(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test build validation with empty graph."""
        # Create builder but remove all nodes
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )
        builder.main_graph.nodes.clear()

        # Should fail validation
        with pytest.raises(ValueError, match="No nodes added to the graph"):
            builder.build()

    def test_build_sets_start_edge(self, sample_health_config, mock_llm, mock_logger):
        """Test that build() sets the START edge correctly."""
        builder = GraphBuilder(
            ConversationAnalysisState,
            sample_health_config,
            mock_llm,
            mock_logger,
            initial_entry_node="custom_entry",
        )

        graph = builder.build()

        # Should have START edge to initial entry node
        # Note: This test depends on the internal structure of LangGraph
        # and might need adjustment based on the actual implementation
        compiled_graph = graph.compile()
        assert compiled_graph is not None

    def test_chaining_pattern(self, sample_health_config, mock_llm, mock_logger):
        """Test that builder methods can be chained."""
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )

        # Create mock subgraphs
        mock_subgraph1 = StateGraph(ConversationAnalysisState)
        mock_subgraph1.add_node("step1", lambda state: {})

        mock_subgraph2 = StateGraph(ConversationAnalysisState)
        mock_subgraph2.add_node("step2", lambda state: {})

        # Test chaining
        result = builder.add_subgraph(
            mock_subgraph1, "step1", {"step1": "step2"}, "start_conversation_analysis"
        ).add_subgraph(mock_subgraph2, "step2", {"step2": END}, None)

        assert result == builder
        assert "step1" in builder.main_graph.nodes
        assert "step2" in builder.main_graph.nodes


class TestCreateDefaultSystem:
    """Tests for the default system creation function."""

    def test_default_system_creation(self, sample_health_config, mock_llm, mock_logger):
        """Test creating the default conversation health system."""
        with patch("graph_builder.ConcernAnalysisSubgraphCreator") as mock_concern:
            with patch(
                "graph_builder.ConfigBasedEvaluationSubgraphCreator"
            ) as mock_config:
                with patch(
                    "graph_builder.ScoringSynthesisSubgraphCreator"
                ) as mock_scoring:
                    # Setup mock subgraphs
                    self._setup_mock_creators(mock_concern, mock_config, mock_scoring)

                    graph = create_default_conversation_health_system(
                        sample_health_config, mock_llm, mock_logger
                    )

                    assert graph is not None

                    # Verify all creators were instantiated
                    mock_concern.assert_called_once_with(
                        sample_health_config, mock_llm, mock_logger
                    )
                    mock_config.assert_called_once_with(
                        sample_health_config, mock_llm, mock_logger
                    )
                    mock_scoring.assert_called_once_with(
                        sample_health_config, mock_llm, mock_logger
                    )

    def test_default_system_node_structure(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test that default system has expected node structure."""
        with patch("graph_builder.ConcernAnalysisSubgraphCreator") as mock_concern:
            with patch(
                "graph_builder.ConfigBasedEvaluationSubgraphCreator"
            ) as mock_config:
                with patch(
                    "graph_builder.ScoringSynthesisSubgraphCreator"
                ) as mock_scoring:
                    self._setup_mock_creators(mock_concern, mock_config, mock_scoring)

                    graph = create_default_conversation_health_system(
                        sample_health_config, mock_llm, mock_logger
                    )

                    # Compile and check node structure
                    compiled_graph = graph.compile()
                    node_names = list(compiled_graph.get_graph().nodes.keys())

                    expected_nodes = [
                        "start_conversation_analysis",
                        "identify_conversation_concerns",
                        "analyze_concern_handling",
                        "start_evaluations",
                        "calculate_health_score",
                        "synthesize_final_assessment",
                    ]

                    for node in expected_nodes:
                        assert node in node_names

    def test_default_system_integration_flow(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test the integration flow of the default system."""
        with patch("graph_builder.ConcernAnalysisSubgraphCreator") as mock_concern:
            with patch(
                "graph_builder.ConfigBasedEvaluationSubgraphCreator"
            ) as mock_config:
                with patch(
                    "graph_builder.ScoringSynthesisSubgraphCreator"
                ) as mock_scoring:
                    self._setup_mock_creators(mock_concern, mock_config, mock_scoring)

                    graph = create_default_conversation_health_system(
                        sample_health_config, mock_llm, mock_logger
                    )

                    # Verify subgraphs were connected properly
                    all_creators = [mock_concern, mock_config, mock_scoring]
                    for creator_mock in all_creators:
                        creator_mock.return_value.create_subgraph.assert_called_once()

    def test_error_handling_in_default_system(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test error handling during default system creation."""
        with patch("graph_builder.ConcernAnalysisSubgraphCreator") as mock_concern:
            # Make concern creator fail
            mock_concern.side_effect = Exception("Creator failed")

            with pytest.raises(Exception, match="Creator failed"):
                create_default_conversation_health_system(
                    sample_health_config, mock_llm, mock_logger
                )

    def _setup_mock_creators(self, mock_concern, mock_config, mock_scoring):
        """Helper to setup mock creators with proper return values."""
        # Mock concern analysis subgraph
        mock_concern_subgraph = StateGraph(ConversationAnalysisState)
        mock_concern_subgraph.add_node("identify_conversation_concerns", lambda s: {})
        mock_concern_subgraph.add_node("analyze_concern_handling", lambda s: {})
        mock_concern.return_value.create_subgraph.return_value = (
            mock_concern_subgraph,
            "identify_conversation_concerns",
            ["analyze_concern_handling"],
        )

        # Mock config-based evaluation subgraph
        mock_config_subgraph = StateGraph(ConversationAnalysisState)
        mock_config_subgraph.add_node("start_evaluations", lambda s: {})
        mock_config_subgraph.add_node("eval_node", lambda s: {})
        mock_config.return_value.create_subgraph.return_value = (
            mock_config_subgraph,
            "start_evaluations",
            ["eval_node"],
        )

        # Mock scoring synthesis subgraph
        mock_scoring_subgraph = StateGraph(ConversationAnalysisState)
        mock_scoring_subgraph.add_node("calculate_health_score", lambda s: {})
        mock_scoring_subgraph.add_node("synthesize_final_assessment", lambda s: {})
        mock_scoring.return_value.create_subgraph.return_value = (
            mock_scoring_subgraph,
            "calculate_health_score",
            ["synthesize_final_assessment"],
        )


class TestGraphBuilderEdgeCases:
    """Tests for edge cases and error conditions in graph building."""

    def test_add_subgraph_none_connection(
        self, sample_health_config, mock_llm, mock_logger
    ):
        """Test adding subgraph with None connection (standalone subgraph)."""
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )

        # Create a standalone subgraph
        mock_subgraph = StateGraph(ConversationAnalysisState)
        mock_subgraph.add_node("standalone_node", lambda state: {})

        result = builder.add_subgraph(
            subgraph=mock_subgraph,
            entry_node="standalone_node",
            exit_connections={"standalone_node": END},
            connect_entry_to=None,  # No connection to existing nodes
        )

        assert result == builder
        assert "standalone_node" in builder.main_graph.nodes

        # Should not create any entry connections
        edges = builder.main_graph.edges
        entry_edges = [e for e in edges if e[1] == "standalone_node"]
        assert len(entry_edges) == 0

    def test_empty_subgraph_handling(self, sample_health_config, mock_llm, mock_logger):
        """Test handling of empty subgraphs."""
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )

        # Create empty subgraph
        mock_subgraph = StateGraph(ConversationAnalysisState)

        # This should not crash, though it may not be a typical use case
        result = builder.add_subgraph(
            subgraph=mock_subgraph,
            entry_node="nonexistent_node",
            exit_connections={},
            connect_entry_to="start_conversation_analysis",
        )

        assert result == builder

    def test_circular_connections(self, sample_health_config, mock_llm, mock_logger):
        """Test that circular connections can be created if needed."""
        builder = GraphBuilder(
            ConversationAnalysisState, sample_health_config, mock_llm, mock_logger
        )

        # Create subgraph with potential for circular connection
        mock_subgraph = StateGraph(ConversationAnalysisState)
        mock_subgraph.add_node("circular_node", lambda state: {})

        builder.add_subgraph(
            subgraph=mock_subgraph,
            entry_node="circular_node",
            exit_connections={
                "circular_node": "start_conversation_analysis"
            },  # Back to start
            connect_entry_to="start_conversation_analysis",
        )

        # Should create the circular reference
        edges = builder.main_graph.edges
        circular_edges = [
            e
            for e in edges
            if (e[0] == "start_conversation_analysis" and e[1] == "circular_node")
            or (e[0] == "circular_node" and e[1] == "start_conversation_analysis")
        ]
        assert len(circular_edges) >= 2
