# import pytest
# from unittest.mock import Mock, patch
# from conversation_health_builder import (
#     ConversationHealthAnalysisBuilder,
#     create_default_conversation_health_system,
# )


# def test_builder_initialization(sample_health_config, mock_llm, mock_logger):
#     """Test builder initialization"""
#     builder = ConversationHealthAnalysisBuilder(
#         sample_health_config, mock_llm, mock_logger
#     )

#     assert builder.config == sample_health_config
#     assert builder.llm == mock_llm
#     assert builder.logger == mock_logger
#     assert not builder.entry_point_set
#     assert not builder.scoring_nodes_added


# def test_set_entry_point(sample_health_config, mock_llm, mock_logger):
#     """Test entry point setting"""
#     builder = ConversationHealthAnalysisBuilder(
#         sample_health_config, mock_llm, mock_logger
#     )

#     result = builder.set_entry_point("test_node")

#     assert builder.entry_point_set
#     assert result == builder  # Should return self for chaining


# def test_add_subgraph(sample_health_config, mock_llm, mock_logger):
#     """Test subgraph addition"""
#     builder = ConversationHealthAnalysisBuilder(
#         sample_health_config, mock_llm, mock_logger
#     )

#     # Create mock subgraph
#     mock_subgraph = Mock()
#     mock_subgraph.nodes = {
#         "node1": Mock(runnable=Mock()),
#         "node2": Mock(runnable=Mock()),
#     }
#     mock_subgraph.edges = [("node1", "node2")]

#     result = builder.add_subgraph(mock_subgraph, "node1", ["node2"], "next_node")

#     # Should add nodes and edges
#     assert "node1" in builder.main_graph.nodes
#     assert "node2" in builder.main_graph.nodes
#     assert result == builder  # Should return self


# def test_add_concern_analysis_subgraph(sample_health_config, mock_llm, mock_logger):
#     """Test concern analysis subgraph addition"""
#     builder = ConversationHealthAnalysisBuilder(
#         sample_health_config, mock_llm, mock_logger
#     )

#     with patch(
#         "conversation_health_builder.ConcernAnalysisSubgraphCreator"
#     ) as mock_creator:
#         mock_subgraph = Mock()
#         mock_subgraph.nodes = {"identify_conversation_concerns": Mock(runnable=Mock())}
#         mock_subgraph.edges = []
#         mock_creator.return_value.create_concern_analysis_subgraph.return_value = (
#             mock_subgraph
#         )

#         result = builder.add_subgraph(
#             mock_subgraph,
#             "identify_conversation_concerns",
#             ["analyze_concern_handling_quality"],
#             "next_node",
#         )

#         assert result == builder
#         assert builder.entry_point_set


# def test_add_config_based_evaluation_subgraph(
#     sample_health_config, mock_llm, mock_logger
# ):
#     """Test config-based evaluation subgraph convenience method"""
#     builder = ConversationHealthAnalysisBuilder(
#         sample_health_config, mock_llm, mock_logger
#     )

#     with patch(
#         "conversation_health_builder.ConfigBasedEvaluationSubgraphCreator"
#     ) as mock_creator:
#         mock_subgraph = Mock()
#         mock_subgraph.nodes = {"eval_node": Mock(runnable=Mock())}
#         mock_subgraph.edges = []
#         mock_creator.return_value.create_evaluation_subgraph.return_value = (
#             mock_subgraph
#         )

#         result = builder.add_standard_evaluation_subgraph("next_node")

#         assert result == builder


# def test_add_scoring_and_synthesis_nodes(sample_health_config, mock_llm, mock_logger):
#     """Test scoring and synthesis nodes addition"""
#     builder = ConversationHealthAnalysisBuilder(
#         sample_health_config, mock_llm, mock_logger
#     )

#     with patch(
#         "conversation_health_builder.create_health_scoring_node"
#     ) as mock_scoring:
#         with patch(
#             "conversation_health_builder.create_assessment_synthesis_node"
#         ) as mock_synthesis:
#             mock_scoring.return_value = Mock()
#             mock_synthesis.return_value = Mock()

#             result = builder.add_scoring_and_synthesis_nodes()

#             assert builder.scoring_nodes_added
#             assert result == builder
#             assert "calculate_health_score" in builder.main_graph.nodes
#             assert "synthesize_final_assessment" in builder.main_graph.nodes


# def test_build_validation(sample_health_config, mock_llm, mock_logger):
#     """Test build validation requirements"""
#     builder = ConversationHealthAnalysisBuilder(
#         sample_health_config, mock_llm, mock_logger
#     )

#     # Should fail without entry point
#     with pytest.raises(ValueError, match="Entry point must be set"):
#         builder.build()

#     # Should fail without scoring nodes
#     builder.set_entry_point("test")
#     with pytest.raises(ValueError, match="Scoring nodes must be added"):
#         builder.build()


# def test_successful_build(sample_health_config, mock_llm, mock_logger):
#     """Test successful graph building"""
#     builder = ConversationHealthAnalysisBuilder(
#         sample_health_config, mock_llm, mock_logger
#     )

#     with patch(
#         "conversation_health_builder.create_health_scoring_node", return_value=Mock()
#     ):
#         with patch(
#             "conversation_health_builder.create_assessment_synthesis_node",
#             return_value=Mock(),
#         ):
#             graph = (
#                 builder.set_entry_point("test_node")
#                 .add_scoring_and_synthesis_nodes()
#                 .build()
#             )

#             assert graph is not None


# def test_create_default_system(sample_health_config, mock_llm, mock_logger):
#     """Test default system creation end-to-end"""
#     with patch(
#         "conversation_health_builder.ConcernAnalysisSubgraphCreator"
#     ) as mock_concern:
#         with patch(
#             "conversation_health_builder.ConfigBasedEvaluationSubgraphCreator"
#         ) as mock_config:
#             with patch(
#                 "conversation_health_builder.create_health_scoring_node",
#                 return_value=Mock(),
#             ):
#                 with patch(
#                     "conversation_health_builder.create_assessment_synthesis_node",
#                     return_value=Mock(),
#                 ):
#                     # Mock subgraphs
#                     mock_concern_subgraph = Mock()
#                     mock_concern_subgraph.nodes = {
#                         "identify_conversation_concerns": Mock(runnable=Mock())
#                     }
#                     mock_concern_subgraph.edges = []
#                     mock_concern.return_value.create_concern_analysis_subgraph.return_value = (
#                         mock_concern_subgraph
#                     )

#                     mock_config_subgraph = Mock()
#                     mock_config_subgraph.nodes = {"eval_node": Mock(runnable=Mock())}
#                     mock_config_subgraph.edges = []
#                     mock_config.return_value.create_evaluation_subgraph.return_value = (
#                         mock_config_subgraph
#                     )

#                     graph = create_default_conversation_health_system(
#                         sample_health_config, mock_llm, mock_logger
#                     )

#                     assert graph is not None
