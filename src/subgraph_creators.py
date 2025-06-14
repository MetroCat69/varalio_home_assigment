from abc import ABC, abstractmethod
from typing import Dict, Tuple, List
from logging import Logger
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph
from models import (
    ConversationAnalysisState,
    ConversationHealthConfig,
    IdentifiedConcerns,
    CriteriaAnalysisNodeOutput,
    ConversationHealthScore,
    ConversationHealthAssessment,
)
from prompts import (
    get_concern_identification_prompt,
    get_concern_resolution_prompt,
    get_health_assessment_synthesis_prompt,
)
from pydantic_model_creators import create_evaluation_criteria_model
from llm import call_llm_structured, call_llm
from score_calculator import ConversationHealthScorer


class BaseSubgraphCreator(ABC):
    def __init__(
        self, config: ConversationHealthConfig, llm: BaseLanguageModel, logger: Logger
    ):
        self.config = config
        self.llm = llm
        self.logger = logger

    @abstractmethod
    def create_subgraph(self) -> Tuple[StateGraph, str, List[str]]:
        """Returns tuple of (subgraph, entry_node_name, end_node_names)"""
        pass


class ScoringSynthesisSubgraphCreator(BaseSubgraphCreator):
    def create_subgraph(self) -> Tuple[StateGraph, str, List[str]]:
        subgraph = StateGraph(ConversationAnalysisState)
        entry_node = "calculate_health_score"
        end_nodes = ["synthesize_final_assessment"]

        subgraph.add_node(entry_node, self._calculate_conversation_health_score)

        subgraph.add_node(end_nodes[0], self._synthesize_health_assessment)

        subgraph.set_entry_point(entry_node)
        subgraph.add_edge(entry_node, end_nodes[0])

        return subgraph, entry_node, end_nodes

    def _calculate_conversation_health_score(
        self,
        state: ConversationAnalysisState,
    ) -> Dict[str, ConversationHealthScore]:
        scorer = ConversationHealthScorer(self.config)
        health_score = scorer.generate_complete_health_score(
            state.criteria_evaluations, state.quality_indicator_detections
        )
        return {"health_score": health_score}

    def _synthesize_health_assessment(
        self,
        state: ConversationAnalysisState,
    ) -> Dict[str, ConversationHealthAssessment]:
        synthesis_prompt = get_health_assessment_synthesis_prompt(state.health_score)
        assessment_content = call_llm(synthesis_prompt, self.llm, self.logger)
        return {
            "final_assessment": {
                "criteria_evaluations": state.criteria_evaluations,
                "quality_indicator_detections": state.quality_indicator_detections,
                "health_score": state.health_score,
                "overall_assessment": assessment_content,
                "final_score": state.health_score["final_score"],
            }
        }


class ConcernAnalysisSubgraphCreator(BaseSubgraphCreator):
    def create_subgraph(self) -> Tuple[StateGraph, str, List[str]]:
        subgraph = StateGraph(ConversationAnalysisState)
        entry_node = "identify_conversation_concerns"
        end_nodes = ["analyze_concern_handling"]

        subgraph.add_node(entry_node, self._identify_concerns)
        subgraph.add_node(end_nodes[0], self._analyze_concern_handling)

        subgraph.set_entry_point(entry_node)
        subgraph.add_edge(entry_node, end_nodes[0])

        return subgraph, entry_node, end_nodes

    def _identify_concerns(
        self, state: ConversationAnalysisState
    ) -> Dict[str, IdentifiedConcerns]:
        prompt = get_concern_identification_prompt(state.transcript)
        result = call_llm_structured(prompt, IdentifiedConcerns, self.llm, self.logger)
        return {"identified_concerns": result}

    def _analyze_concern_handling(
        self, state: ConversationAnalysisState
    ) -> CriteriaAnalysisNodeOutput:
        model = create_evaluation_criteria_model(
            self.config.evaluation_criteria["concern_handling_quality"]
        )
        prompt = get_concern_resolution_prompt(state.identified_concerns)
        result = call_llm_structured(prompt, model, self.llm, self.logger)
        return {"criteria_evaluations": {"concern_handling_quality": result}}


class ConfigBasedEvaluationSubgraphCreator(BaseSubgraphCreator):
    def create_subgraph(self) -> Tuple[StateGraph, str, List[str]]:
        from node_builders import (
            EvaluationCriteriaNodeBuilder,
            QualityIndicatorNodeBuilder,
        )

        subgraph = StateGraph(ConversationAnalysisState)

        # Create a dedicated entry node that branches to all evaluation nodes
        entry_node = "start_evaluations"
        subgraph.add_node(entry_node, lambda state: None)  # Pass-through node

        end_nodes = []
        criteria_builder = EvaluationCriteriaNodeBuilder(self.llm, self.logger)
        indicator_builder = QualityIndicatorNodeBuilder(self.llm, self.logger)

        # Add evaluation criteria nodes
        evaluation_nodes = []
        for name, config in self.config.evaluation_criteria.items():
            if config.is_config_based:
                node_name = f"evaluate_{name}"
                subgraph.add_node(
                    node_name, criteria_builder.create_evaluation_node(config)
                )
                evaluation_nodes.append(node_name)
                end_nodes.append(node_name)

        # Add quality indicator nodes
        indicator_nodes = []
        for indicator in self.config.quality_indicators:
            node_name = f"detect_{indicator.name}"
            subgraph.add_node(
                node_name, indicator_builder.create_detection_node(indicator)
            )
            indicator_nodes.append(node_name)
            end_nodes.append(node_name)

        # Connect entry node to all evaluation and indicator nodes
        for node in evaluation_nodes + indicator_nodes:
            subgraph.add_edge(entry_node, node)

        subgraph.set_entry_point(entry_node)
        return subgraph, entry_node, end_nodes
