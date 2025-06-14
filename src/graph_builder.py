from typing import List, Dict, Optional, Union, Any
from logging import Logger
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END, START
from models import ConversationAnalysisState, ConversationHealthConfig
from subgraph_creators import (
    ConcernAnalysisSubgraphCreator,
    ConfigBasedEvaluationSubgraphCreator,
    ScoringSynthesisSubgraphCreator,
)


class GraphBuilder:
    def __init__(
        self,
        state: Any,
        config: ConversationHealthConfig,
        llm: BaseLanguageModel,
        logger: Logger,
        initial_entry_node: str = "start_conversation_analysis",
    ):
        self.config = config
        self.llm = llm
        self.logger = logger
        self.main_graph = StateGraph(state)
        self.initial_entry_node = initial_entry_node

        self.main_graph.add_node(initial_entry_node, lambda state: None)

    def add_subgraph(
        self,
        subgraph: StateGraph,
        entry_node: str,
        exit_connections: Dict[str, Union[str, END]],  # type: ignore
        connect_entry_to: Optional[Union[str, List[str]]] = None,
    ) -> "GraphBuilder":
        """
        Add a subgraph to the main workflow.

        Args:
            subgraph: The StateGraph to add
            entry_node: The node that should serve as entry point for this subgraph
            exit_connections: Dict of {exit_node: target_node} connections
            connect_entry_to: Node(s) to connect to this subgraph's entry (None for initial subgraph)
        """
        from langgraph.graph import START

        for node_name, node_spec in subgraph.nodes.items():
            if node_name != START:
                self.main_graph.add_node(node_name, node_spec.runnable)

        for src, dst in subgraph.edges:
            if src != START and dst != START:
                self.main_graph.add_edge(src, dst)

        if connect_entry_to:
            if isinstance(connect_entry_to, str):
                self.main_graph.add_edge(connect_entry_to, entry_node)
            else:
                for source_node in connect_entry_to:
                    self.main_graph.add_edge(source_node, entry_node)

        for exit_node, target_node in exit_connections.items():
            if target_node != END:
                self.main_graph.add_edge(exit_node, target_node)
            else:
                self.main_graph.add_edge(exit_node, END)

        return self

    def build(self) -> StateGraph:
        if not self.main_graph.nodes:
            raise ValueError("No nodes added to the graph")

        self.main_graph.add_edge(START, self.initial_entry_node)

        return self.main_graph


def create_default_conversation_health_system(
    config: ConversationHealthConfig, llm: BaseLanguageModel, logger: Logger
) -> StateGraph:
    builder = GraphBuilder(
        ConversationAnalysisState,
        config,
        llm,
        logger,
        initial_entry_node="start_conversation_analysis",
    )

    concern_creator = ConcernAnalysisSubgraphCreator(config, llm, logger)
    concern_graph, concern_entry, concern_exits = concern_creator.create_subgraph()
    builder.add_subgraph(
        concern_graph,
        entry_node=concern_entry,
        connect_entry_to="start_conversation_analysis",
        exit_connections={concern_exits[0]: "start_evaluations"},
    )

    eval_creator = ConfigBasedEvaluationSubgraphCreator(config, llm, logger)
    eval_graph, eval_entry, eval_exits = eval_creator.create_subgraph()
    builder.add_subgraph(
        eval_graph,
        entry_node=eval_entry,
        connect_entry_to=concern_exits,
        exit_connections={
            exit_node: "calculate_health_score" for exit_node in eval_exits
        },
    )

    scoring_creator = ScoringSynthesisSubgraphCreator(config, llm, logger)
    scoring_graph, scoring_entry, scoring_exits = scoring_creator.create_subgraph()
    builder.add_subgraph(
        scoring_graph,
        entry_node=scoring_entry,
        connect_entry_to=None,
        exit_connections={scoring_exits[0]: END},
    )

    return builder.build()
