from typing import List
from models import ConversationHealthScore, IdentifiedConcerns
from models import EvaluationCriteriaConfig, QualityIndicatorConfig


def get_confidence_level_description() -> str:
    return """Confidence levels:
- very_high: Extremely clear evidence, no ambiguity
- high: Strong evidence with minor uncertainty. This is a very strong statement and must have strong supporting evidence.
- moderate: Moderate evidence, some ambiguity
- low: Weak evidence, significant uncertainty
- very_low: Minimal evidence, high uncertainty"""


def get_health_assessment_synthesis_prompt(
    health_score: ConversationHealthScore,
) -> str:
    return f"""Create a comprehensive communication health assessment based on the analysis and calculated score.

Criteria Results: {health_score['criteria_results']}
Quality Indicator Results: {health_score['indicator_results']}
Score Information:
- Final Score: {health_score['final_score']}/100
- Health Level: {health_score['health_level']}
- Total Criteria Points: {health_score['total_criteria_points']}
- Indicator Adjustments: {health_score['total_indicator_adjustment']}
- Raw Score: {health_score['raw_score']}

Provide an overall assessment that:
- Highlights key strengths and weaknesses in ONE SHORT SENTENCE ONLY
- Provides 2-3 actionable recommendation points based on findings (include positive aspects when appropriate)
- Maintains conciseness while being insightful (2-3 points with concrete recommendations)
- Only includes actions that are clearly relevant to the assessment
- For predominantly positive assessments, provide ONLY ONE SHORT SENTENCE highlighting what was done well

CRITICAL: If the conversation was generally effective, respond with ONLY ONE SHORT SENTENCE about the strengths - do not add bullet points or additional recommendations."""


def get_concern_identification_prompt(transcript: str) -> str:
    return f"""Analyze this conversation transcript to identify key concerns and questions that were raised.

Transcript:
{transcript}

For each concern or question you identify:
1. Provide a clear description of what was raised
2. Assess the addressal level (not_addressed, partially_addressed, mostly_addressed, fully_addressed)
3. Explain your reasoning for the addressal assessment

Focus on substantive concerns that were brought up during the conversation. Look for:
- Direct questions asked by participants (high confidence when explicitly stated)
- Concerns or problems mentioned (confident when clearly expressed)
- Requests for information or help (very confident with explicit requests)
- Important issues or topics discussed (confident when clearly introduced)
- Complaints or feedback shared (high confidence with direct statements)
- Goals or objectives mentioned (confident when explicitly stated)

Be comprehensive but focused - identify concerns that are meaningful to the conversation's purpose and outcomes. Only include items you can support with confident reasoning from the transcript."""


def get_concern_resolution_prompt(
    identified_concerns: IdentifiedConcerns,
) -> str:
    return f"""Based on the identified concerns below, provide an overall assessment of how well concerns were addressed in the conversation.

Identified Concerns:
{identified_concerns.model_dump()}

{get_confidence_level_description()}

Analyze the overall pattern of how concerns were handled with high analytical confidence:
- How thoroughly were questions and concerns addressed? (confident assessment based on clear evidence)
- Was there genuine effort to respond to what was raised? (very confident when explicit responses are shown)
- Were concerns given appropriate attention, or were some dismissed or ignored? (somewhat confident, requires inference)
- Did the conversation achieve its apparent purpose based on the concerns discussed? (confident based on flow and outcome)

Provide:
1. Your assessment of the overall concern handling quality
2. Brief reasoning for your choice with confidence level (MUST BE ONE SHORT SENTENCE ONLY)

Rate your confidence level in this synthesis using the scale above.
Focus on patterns you can identify with at least moderate certainty."""


def get_criteria_analysis_prompt(
    criteria_config: EvaluationCriteriaConfig, transcript: str
) -> str:
    available_responses = list(criteria_config.response_options.keys())
    response_descriptions = {
        response: config.description
        for response, config in criteria_config.response_options.items()
    }

    return f"""Analyze this conversation transcript for: {criteria_config.description}

Transcript:
{transcript}

{criteria_config.prompt}

Available response options:
{chr(10).join(f"- {response}: {response_descriptions[response]}" for response in available_responses)}

{get_confidence_level_description()}

Provide:
1. Your selected response from the options above
2. Brief reasoning for your choice with confidence assessment (MUST BE ONE SHORT SENTENCE ONLY)
3. Your confidence level using the scale above

Be thorough in your reasoning, acknowledge limitations honestly, and provide your best assessment."""


def get_quality_indicator_detection_prompt(
    indicator_config: QualityIndicatorConfig, transcript: str
) -> str:
    return f"""Analyze this conversation transcript to detect the following communication quality indicator:

Indicator: {indicator_config.name}
Description: {indicator_config.description}

Transcript:
{transcript}

{get_confidence_level_description()}

Determine:
1. Whether this quality indicator is present in the conversation (true/false)
2. Brief reasoning for your choice with confidence assessment (MUST BE ONE SHORT SENTENCE ONLY)
3. Your confidence level using the scale above

Be conservative in detection - only flag instances you can identify with reasonable certainty.
If evidence is ambiguous or requires significant inference, rate as 'low' or 'very_low' confidence.
Clear, explicit examples should yield 'high' or 'very_high' confidence ratings."""
