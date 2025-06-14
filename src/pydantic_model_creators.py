from typing import Type, cast
from pydantic import Field, create_model
from enum import Enum
from models import (
    EvaluationCriteriaConfig,
    EvaluationCriteriaResult,
    QualityIndicatorResult,
)


def create_evaluation_criteria_model(
    criteria_config: EvaluationCriteriaConfig,
) -> Type[EvaluationCriteriaResult]:

    available_responses = list(criteria_config.response_options.keys())

    response_enum_name = f"{criteria_config.name.title().replace('_', '')}Response"
    response_enum_values = {response: response for response in available_responses}
    response_enum = Enum(response_enum_name, response_enum_values)  # type: ignore[misc]

    analysis_model_name = f"{criteria_config.name.title().replace('_', '')}Analysis"
    analysis_model = create_model(
        analysis_model_name,
        __base__=EvaluationCriteriaResult,
        selected_response=(
            response_enum,
            Field(description=f"Selected response for {criteria_config.description}"),
        ),
    )

    return cast(Type[EvaluationCriteriaResult], analysis_model)


def create_quality_indicator_model(
    indicator_name: str,
) -> Type[QualityIndicatorResult]:

    detection_model_name = f"{indicator_name.title().replace('_', '')}Detection"
    detection_model = create_model(
        detection_model_name,
        __base__=QualityIndicatorResult,
    )

    return cast(Type[QualityIndicatorResult], detection_model)
