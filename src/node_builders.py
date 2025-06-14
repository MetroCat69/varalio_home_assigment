from typing import Callable
from logging import Logger
from langchain_core.language_models import BaseLanguageModel
from llm import call_llm_structured
from prompts import get_criteria_analysis_prompt, get_quality_indicator_detection_prompt
from models import (
    ConversationAnalysisState,
    QualityIndicatorConfig,
    EvaluationCriteriaConfig,
    QualityIndicatorNodeOutput,
    CriteriaAnalysisNodeOutput,
)
from pydantic_model_creators import (
    create_evaluation_criteria_model,
    create_quality_indicator_model,
)


class QualityIndicatorNodeBuilder:
    def __init__(self, llm: BaseLanguageModel, logger: Logger):
        self.llm = llm
        self.logger = logger

    def create_detection_node(
        self, indicator_config: QualityIndicatorConfig
    ) -> Callable:
        indicator_model = create_quality_indicator_model(indicator_config.name)

        def detect_quality_indicator(
            state: ConversationAnalysisState,
        ) -> QualityIndicatorNodeOutput:
            prompt = get_quality_indicator_detection_prompt(
                indicator_config, state.transcript
            )
            result = call_llm_structured(prompt, indicator_model, self.llm, self.logger)
            return {"quality_indicator_detections": {indicator_config.name: result}}

        return detect_quality_indicator


class EvaluationCriteriaNodeBuilder:
    def __init__(self, llm: BaseLanguageModel, logger: Logger):
        self.llm = llm
        self.logger = logger

    def create_evaluation_node(
        self, criteria_config: EvaluationCriteriaConfig
    ) -> Callable:
        criteria_model = create_evaluation_criteria_model(criteria_config)

        def evaluate_conversation_criteria(
            state: ConversationAnalysisState,
        ) -> CriteriaAnalysisNodeOutput:
            prompt = get_criteria_analysis_prompt(criteria_config, state.transcript)
            result = call_llm_structured(prompt, criteria_model, self.llm, self.logger)
            return {"criteria_evaluations": {criteria_config.name: result}}

        return evaluate_conversation_criteria
