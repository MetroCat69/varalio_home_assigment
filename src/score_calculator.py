from typing import Dict, Tuple
from models import (
    ConversationHealthConfig,
    HealthScoreRange,
    AssessmentConfidence,
    CriteriaEvaluationResult,
    QualityIndicatorDetectionResult,
    ConversationHealthScore,
    CriteriaEvaluations,
    QualityIndicatorDetections,
    ScoringUncertainty,
)


class ConversationHealthScorer:

    def __init__(self, config: ConversationHealthConfig):
        self.config = config
        self._quality_indicator_lookup = {
            indicator.name: indicator for indicator in config.quality_indicators
        }

    def _meets_confidence_threshold(
        self,
        actual_confidence: AssessmentConfidence,
        required_confidence: AssessmentConfidence,
    ) -> bool:
        actual_weight = self.config.confidence_level_weights[actual_confidence]
        required_weight = self.config.confidence_level_weights[required_confidence]
        return actual_weight >= required_weight

    def score_evaluation_criteria(
        self,
        criteria_name: str,
        selected_response: str,
        confidence: AssessmentConfidence,
        reasoning: str = "",
    ) -> CriteriaEvaluationResult:

        if criteria_name not in self.config.evaluation_criteria:
            raise KeyError(
                f"Evaluation criteria '{criteria_name}' not found in configuration"
            )

        criteria_config = self.config.evaluation_criteria[criteria_name]

        included_in_final_score = self._meets_confidence_threshold(
            confidence, criteria_config.minimum_confidence
        )

        if included_in_final_score:
            if selected_response not in criteria_config.response_options:
                raise ValueError(
                    f"Response '{selected_response}' not valid for criteria '{criteria_name}'. "
                    f"Valid responses: {list(criteria_config.response_options.keys())}"
                )
            response_config = criteria_config.response_options[selected_response]
            score_multiplier = response_config.score_multiplier
        else:
            score_multiplier = criteria_config.default_score_multiplier

        earned_points = score_multiplier * criteria_config.max_points

        return {
            "criteria_name": criteria_name,
            "selected_response": selected_response,
            "earned_points": earned_points,
            "score_multiplier": score_multiplier,
            "reasoning": reasoning,
            "confidence": confidence,
            "included_in_final_score": included_in_final_score,
        }

    def score_quality_indicator(
        self,
        indicator_name: str,
        pattern_detected: bool,
        confidence: AssessmentConfidence,
        reasoning: str = "",
    ) -> QualityIndicatorDetectionResult:

        if indicator_name not in self._quality_indicator_lookup:
            raise ValueError(
                f"Quality indicator '{indicator_name}' not found in configuration"
            )

        indicator_config = self._quality_indicator_lookup[indicator_name]

        confidence_sufficient = self._meets_confidence_threshold(
            confidence, indicator_config.minimum_confidence
        )
        included_in_final_score = confidence_sufficient and pattern_detected

        score_impact = indicator_config.score_impact if included_in_final_score else 0.0

        return {
            "indicator_name": indicator_name,
            "pattern_detected": pattern_detected,
            "score_impact": score_impact,
            "reasoning": reasoning,
            "confidence": confidence,
            "included_in_final_score": included_in_final_score,
        }

    def score_all_evaluation_criteria(
        self,
        criteria_evaluations: CriteriaEvaluations,
    ) -> Dict[str, CriteriaEvaluationResult]:

        all_criteria_scores = {}
        for criteria_name, evaluation in criteria_evaluations.items():
            all_criteria_scores[criteria_name] = self.score_evaluation_criteria(
                criteria_name,
                evaluation.selected_response.value,
                evaluation.confidence,
                evaluation.reasoning,
            )
        return all_criteria_scores

    def score_all_quality_indicators(
        self, quality_indicator_detections: QualityIndicatorDetections
    ) -> Dict[str, QualityIndicatorDetectionResult]:

        all_indicator_scores = {}
        for indicator_name, detection in quality_indicator_detections.items():
            all_indicator_scores[indicator_name] = self.score_quality_indicator(
                indicator_name,
                detection.detected,
                detection.confidence,
                detection.reasoning,
            )
        return all_indicator_scores

    def calculate_final_health_score(
        self,
        criteria_results: Dict[str, CriteriaEvaluationResult],
        indicator_results: Dict[str, QualityIndicatorDetectionResult],
    ) -> Tuple[int, float]:

        total_criteria_points = sum(
            result["earned_points"]
            for result in criteria_results.values()
            if result["included_in_final_score"]
        )

        total_indicator_adjustment = sum(
            result["score_impact"]
            for result in indicator_results.values()
            if result["included_in_final_score"]
        )

        # Calculate raw score and constrain to 0-100 range
        raw_score = total_criteria_points + total_indicator_adjustment
        final_score = max(0, min(100, int(raw_score)))

        return final_score, raw_score

    def determine_health_level(self, score: int) -> HealthScoreRange:

        for health_range in self.config.health_score_ranges.values():
            if health_range.min_score <= score <= health_range.max_score:
                return health_range
        raise ValueError(f"Score {score} does not fall within any defined health range")

    def analyze_scoring_uncertainty(
        self,
        criteria_results: Dict[str, CriteriaEvaluationResult],
        indicator_results: Dict[str, QualityIndicatorDetectionResult],
    ) -> ScoringUncertainty:

        excluded_criteria = [
            name
            for name, result in criteria_results.items()
            if not result["included_in_final_score"]
        ]

        # Only include indicators that were detected but excluded due to low confidence
        excluded_indicators = [
            name
            for name, result in indicator_results.items()
            if not result["included_in_final_score"] and result["pattern_detected"]
        ]

        return {
            "excluded_criteria": excluded_criteria,
            "excluded_indicators": excluded_indicators,
        }

    def generate_complete_health_score(
        self,
        criteria_evaluations: CriteriaEvaluations,
        quality_indicator_detections: QualityIndicatorDetections,
    ) -> ConversationHealthScore:

        criteria_results = self.score_all_evaluation_criteria(criteria_evaluations)
        indicator_results = self.score_all_quality_indicators(
            quality_indicator_detections
        )

        final_score, raw_score = self.calculate_final_health_score(
            criteria_results, indicator_results
        )

        health_info = self.determine_health_level(final_score)

        uncertainty_info = self.analyze_scoring_uncertainty(
            criteria_results, indicator_results
        )

        total_criteria_points = sum(
            result["earned_points"]
            for result in criteria_results.values()
            if result["included_in_final_score"]
        )

        total_indicator_adjustment = sum(
            result["score_impact"]
            for result in indicator_results.values()
            if result["included_in_final_score"]
        )

        return {
            "criteria_results": criteria_results,
            "total_criteria_points": total_criteria_points,
            "indicator_results": indicator_results,
            "total_indicator_adjustment": total_indicator_adjustment,
            "raw_score": raw_score,
            "final_score": final_score,
            "health_level": health_info.label,
            "health_color": health_info.color,
            "uncertainty_info": uncertainty_info,
        }
