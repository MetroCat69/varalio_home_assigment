from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uvicorn

# Import your conversation health modules
from logger import get_logger
from config_manager import ConversationHealthConfigManager
from llm import get_llm
from graph_builder import create_default_conversation_health_system

app = FastAPI(
    title="Conversation Health Analysis API",
    description="API for analyzing conversation health and quality metrics",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalysisRequest(BaseModel):
    transcript: str
    test_case: Optional[str] = None


class AnalysisResponse(BaseModel):
    finalScore: int
    healthLevel: str
    overallAssessment: str
    overallConfidence: str
    criteriaEvaluations: Dict[str, Any]
    qualityIndicators: Dict[str, Any]
    uncertaintyInfo: Dict[str, Any]
    metadata: Dict[str, Any]


# Initialize the conversation health system
logger = get_logger("conversation_health")
config_manager = ConversationHealthConfigManager("config.json")
config = config_manager.get_configuration()
llm = get_llm()
graph = create_default_conversation_health_system(config, llm, logger)
compiled_graph = graph.compile()

print("✅ Conversation health system initialized successfully")


@app.get("/")
async def root():
    return {
        "message": "Conversation Health Analysis API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_conversation(request: AnalysisRequest):
    """
    Analyze a conversation transcript for health metrics
    """
    if not request.transcript.strip():
        raise HTTPException(status_code=400, detail="Transcript cannot be empty")

    print("🔍 Running analysis with graph...")

    # Run the actual graph analysis
    result = compiled_graph.invoke({"transcript": request.transcript})

    # Transform the result to match our frontend format
    analysis_result = transform_graph_result(
        result, request.transcript, request.test_case
    )

    return AnalysisResponse(**analysis_result)


def transform_graph_result(
    graph_result: Dict[str, Any], transcript: str, test_case: Optional[str]
) -> Dict[str, Any]:
    """
    Transform the graph result to match the frontend format
    """
    # Extract the final assessment from your graph result
    final_assessment = graph_result.get("final_assessment", {})
    health_score = final_assessment.get("health_score", {})

    # Extract core metrics
    final_score = health_score.get("final_score", 0)
    health_level = health_score.get("health_level", "unknown").lower()

    # Transform criteria evaluations
    criteria_evaluations = {}
    raw_criteria = final_assessment.get("criteria_evaluations", {})

    for criteria_name, evaluation in raw_criteria.items():
        criteria_evaluations[criteria_name] = {
            "points": health_score.get("criteria_results", {})
            .get(criteria_name, {})
            .get("earned_points", 0),
            "maxPoints": 30,  # You can get this from your config
            "selectedResponse": (
                evaluation.selected_response.value
                if hasattr(evaluation, "selected_response")
                else str(evaluation.get("selected_response", ""))
            ),
            "confidence": (
                evaluation.confidence.value
                if hasattr(evaluation, "confidence")
                else str(evaluation.get("confidence", "moderate"))
            ),
            "reasoning": (
                evaluation.reasoning
                if hasattr(evaluation, "reasoning")
                else str(evaluation.get("reasoning", ""))
            ),
            "color": get_color_for_response(
                evaluation.selected_response
                if hasattr(evaluation, "selected_response")
                else evaluation.get("selected_response", "")
            ),
        }

    # Transform quality indicators
    quality_indicators = {}
    raw_indicators = final_assessment.get("quality_indicator_detections", {})

    for indicator_name, detection in raw_indicators.items():
        quality_indicators[indicator_name] = {
            "detected": (
                detection.detected
                if hasattr(detection, "detected")
                else detection.get("detected", False)
            ),
            "confidence": (
                detection.confidence.value
                if hasattr(detection, "confidence")
                else str(detection.get("confidence", "moderate"))
            ),
            "impact": health_score.get("indicator_results", {})
            .get(indicator_name, {})
            .get("score_impact", 0),
            "reasoning": (
                detection.reasoning
                if hasattr(detection, "reasoning")
                else str(detection.get("reasoning", ""))
            ),
            "color": get_color_for_impact(
                health_score.get("indicator_results", {})
                .get(indicator_name, {})
                .get("score_impact", 0)
            ),
        }

    # Overall assessment
    overall_assessment = final_assessment.get(
        "overall_assessment", "Analysis completed successfully"
    )

    # Uncertainty info
    uncertainty_info = health_score.get("uncertainty_info", {})

    return {
        "finalScore": final_score,
        "healthLevel": health_level,
        "overallAssessment": overall_assessment,
        "overallConfidence": "high",  # You can extract this from your graph if available
        "criteriaEvaluations": criteria_evaluations,
        "qualityIndicators": quality_indicators,
        "uncertaintyInfo": {
            "excludedCriteria": uncertainty_info.get("excluded_criteria", []),
            "excludedIndicators": uncertainty_info.get("excluded_indicators", []),
            "lowConfidenceCount": len(uncertainty_info.get("excluded_criteria", []))
            + len(uncertainty_info.get("excluded_indicators", [])),
        },
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "test_case": test_case,
            "processing_time": 1.5,  # You can measure actual processing time
            "source": "graph_analysis",
            "total_criteria_points": health_score.get("total_criteria_points", 0),
            "total_indicator_adjustment": health_score.get(
                "total_indicator_adjustment", 0
            ),
            "raw_score": health_score.get("raw_score", 0),
        },
    }


def get_color_for_response(response):
    """Get color based on response type"""
    if not response:
        return "#6b7280"

    response_str = str(response).lower()

    if any(
        word in response_str
        for word in ["positive", "excellent", "comprehensive", "crystal"]
    ):
        return "#10b981"
    elif any(
        word in response_str
        for word in ["negative", "poor", "unaddressed", "incomprehensible"]
    ):
        return "#ef4444"
    elif any(word in response_str for word in ["moderate", "mostly", "substantial"]):
        return "#3b82f6"
    elif any(word in response_str for word in ["partial", "surface", "somewhat"]):
        return "#f59e0b"
    else:
        return "#6b7280"


def get_color_for_impact(impact):
    """Get color based on impact value"""
    if impact > 0:
        return "#10b981"  # Green for positive
    elif impact < 0:
        return "#ef4444"  # Red for negative
    else:
        return "#6b7280"  # Gray for neutral


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
