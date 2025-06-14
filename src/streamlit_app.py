"""
Professional Streamlit application for conversation health analysis.
"""

import streamlit as st
import json
import os
import sys
from typing import Dict, Any, Optional
import time

# Add src to path

# Import your modules
from config_manager import ConversationHealthConfigManager
from graph_builder import create_default_conversation_health_system
from llm import get_llm
from logger import get_logger
from utils import extract_health_score, extract_overall_assessment

# Page config
st.set_page_config(
    page_title="Conversation Health Analysis",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .metric-card-positive {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    
    .metric-card-negative {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
    }
    
    .metric-card-neutral {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    
    .points-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .points-positive {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .points-negative {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .points-neutral {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .assessment-box {
        background-color: #f8f9fa;
        border-left: 4px solid #6f42c1;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .indicator-critical { border-left-color: #dc3545; }
    .indicator-warning { border-left-color: #ffc107; }
    .indicator-positive { border-left-color: #28a745; }
    .indicator-info { border-left-color: #17a2b8; }
    
    .export-button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .export-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_test_cases():
    """Load test cases from JSON file"""
    try:
        with open("test_cases.json", "r") as f:
            data = json.load(f)
            return data.get("test_cases", {})
    except FileNotFoundError:
        st.error(
            "test_cases.json file not found. Please ensure it exists in the project root."
        )
        return {}
    except json.JSONDecodeError:
        st.error("Invalid JSON format in test_cases.json")
        return {}


def run_analysis(transcript: str) -> Optional[Dict[str, Any]]:
    """Run the conversation health analysis"""
    try:
        with st.spinner("🔧 Initializing Conversation Health Analysis System..."):
            logger = get_logger("conversation_health")
            config_manager = ConversationHealthConfigManager("config.json")
            config = config_manager.get_configuration()
            llm = get_llm()
            graph = create_default_conversation_health_system(config, llm, logger)
            compiled_graph = graph.compile()

        with st.spinner("🔍 Running analysis..."):
            result = compiled_graph.invoke({"transcript": transcript})

        if not result or "final_assessment" not in result:
            st.error("Invalid response format - missing final_assessment")
            return None

        return result

    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None


def get_points_info(points: float) -> tuple[str, str, str]:
    """Get points display info (text, badge class, card class)"""
    if points > 0:
        return f"+{points:.1f} pts", "points-positive", "metric-card-positive"
    elif points < 0:
        return f"{points:.1f} pts", "points-negative", "metric-card-negative"
    else:
        return f"{points:.1f} pts", "points-neutral", "metric-card-neutral"


def display_overall_score(final_assessment: Dict[str, Any]):
    """Display the overall health score"""
    health_score = final_assessment.get("health_score", {})

    score = (
        health_score.get("final_score", "N/A")
        if isinstance(health_score, dict)
        else "N/A"
    )
    level = (
        health_score.get("health_level", "N/A")
        if isinstance(health_score, dict)
        else "N/A"
    )
    color = (
        health_score.get("health_color", "N/A")
        if isinstance(health_score, dict)
        else "N/A"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎯 Final Score", f"{score}/100")

    with col2:
        st.metric("📈 Health Level", level)


def display_overall_assessment(final_assessment: Dict[str, Any]):
    """Display the overall assessment"""
    assessment = final_assessment.get("overall_assessment", "N/A")

    st.markdown("### 💡 Overall Assessment")
    st.markdown(
        f"""
    <div class="assessment-box">
        {assessment}
    </div>
    """,
        unsafe_allow_html=True,
    )


def display_identified_issues(result: Dict[str, Any]):
    """Display identified issues"""
    identified_issues = result.get("identified_issues")

    if not identified_issues:
        return

    st.markdown("### 🔍 Identified Issues")

    # Handle Pydantic model
    if hasattr(identified_issues, "issues"):
        issues_list = identified_issues.issues
    elif isinstance(identified_issues, dict):
        issues_list = identified_issues.get("issues", [])
    else:
        st.warning("Unknown format for identified issues")
        return

    if not issues_list:
        st.success("✅ No issues identified")
        return

    for i, issue in enumerate(issues_list, 1):
        # Handle Pydantic model
        if hasattr(issue, "description"):
            description = issue.description
            resolution_level = getattr(issue, "resolution_level", "Unknown")
            reasoning = getattr(issue, "reasoning", "No reasoning")
        elif isinstance(issue, dict):
            description = issue.get("description", "No description")
            resolution_level = issue.get("resolution_level", "Unknown")
            reasoning = issue.get("reasoning", "No reasoning")
        else:
            description = str(issue)
            resolution_level = "Unknown"
            reasoning = "No reasoning"

        with st.expander(f"⚠️ Issue {i}: {description}"):
            st.write(f"**Resolution Level:** {resolution_level}")
            st.write(f"**Reasoning:** {reasoning}")


def display_criteria_evaluations(final_assessment: Dict[str, Any]):
    """Display evaluation criteria results with points information"""
    criteria_evaluations = final_assessment.get("criteria_evaluations", {})
    health_score = final_assessment.get("health_score", {})
    criteria_results = (
        health_score.get("criteria_results", {})
        if isinstance(health_score, dict)
        else {}
    )

    if not criteria_evaluations:
        return

    st.markdown("### 📈 Evaluation Criteria Results")

    # Create columns for better layout
    cols = st.columns(2)

    for i, (criteria_name, evaluation) in enumerate(criteria_evaluations.items()):
        with cols[i % 2]:
            # Handle Pydantic model
            if hasattr(evaluation, "selected_response"):
                selected_response = evaluation.selected_response
                reasoning = getattr(evaluation, "reasoning", "N/A")
                confidence = getattr(evaluation, "confidence", "N/A")
            elif isinstance(evaluation, dict):
                selected_response = evaluation.get("selected_response", "N/A")
                reasoning = evaluation.get("reasoning", "N/A")
                confidence = evaluation.get("confidence", "N/A")
            else:
                selected_response = str(evaluation)
                reasoning = "N/A"
                confidence = "N/A"

            # Get points information from health_score.criteria_results
            points = 0
            points_text = ""
            points_badge_class = "points-neutral"
            card_class = "metric-card"

            if criteria_name in criteria_results:
                criteria_result = criteria_results[criteria_name]
                if isinstance(criteria_result, dict):
                    points = criteria_result.get("earned_points", 0)
                    points_text, points_badge_class, card_class = get_points_info(
                        points
                    )

            st.markdown(
                f"""
            <div class="{card_class}">
                <h4>📌 {criteria_name.replace('_', ' ').title()}
                    {f'<span class="points-badge {points_badge_class}">{points_text}</span>' if points_text else ''}
                </h4>
                <p><strong>Response:</strong> {selected_response}</p>
                <p><strong>Confidence:</strong> {confidence}</p>
                <p><strong>Reasoning:</strong> {reasoning}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )


def display_quality_indicators(final_assessment: Dict[str, Any]):
    """Display quality indicator detections with points information"""
    quality_indicator_detections = final_assessment.get(
        "quality_indicator_detections", {}
    )
    health_score = final_assessment.get("health_score", {})
    indicator_results = (
        health_score.get("indicator_results", {})
        if isinstance(health_score, dict)
        else {}
    )

    if not quality_indicator_detections:
        return

    st.markdown("### 🚩 Quality Indicator Detections")

    # Group indicators by detection status and type
    detected_critical = []
    detected_warning = []
    detected_positive = []
    detected_info = []
    not_detected = []

    for indicator_name, detection in quality_indicator_detections.items():
        # Handle Pydantic model
        if hasattr(detection, "detected"):
            detected = detection.detected
            reasoning = getattr(detection, "reasoning", "No reasoning")
            confidence = getattr(detection, "confidence", "Unknown")
        elif isinstance(detection, dict):
            detected = detection.get("detected", False)
            reasoning = detection.get("reasoning", "No reasoning")
            confidence = detection.get("confidence", "Unknown")
        else:
            detected = bool(detection)
            reasoning = "No reasoning available"
            confidence = "Unknown"

        # Get points information
        points = 0
        points_text = ""
        points_badge_class = "points-neutral"
        card_class = "metric-card"

        if indicator_name in indicator_results:
            indicator_result = indicator_results[indicator_name]
            if isinstance(indicator_result, dict):
                points = indicator_result.get("score_impact", 0)
                points_text, points_badge_class, card_class = get_points_info(points)

        indicator_display = {
            "name": indicator_name.replace("_", " ").title(),
            "reasoning": reasoning,
            "confidence": confidence,
            "points_text": points_text,
            "points_badge_class": points_badge_class,
            "card_class": card_class,
        }

        if detected:
            # Categorize by type based on common patterns
            if any(
                word in indicator_name
                for word in [
                    "repetitive",
                    "escalation",
                    "tone_deterioration",
                    "shutdown",
                ]
            ):
                detected_critical.append(indicator_display)
            elif any(
                word in indicator_name
                for word in ["one_sided", "question_avoidance", "declining"]
            ):
                detected_warning.append(indicator_display)
            elif any(
                word in indicator_name
                for word in [
                    "mutual",
                    "constructive",
                    "collaboration",
                    "problem_solving",
                ]
            ):
                detected_positive.append(indicator_display)
            elif any(
                word in indicator_name for word in ["high_stakes", "external_pressure"]
            ):
                detected_info.append(indicator_display)
            else:
                detected_warning.append(indicator_display)  # Default to warning
        else:
            not_detected.append(indicator_display)

    # Display detected indicators with color coding and points
    if detected_critical:
        st.markdown("#### 🔴 CRITICAL Issues Detected")
        for indicator in detected_critical:
            st.markdown(
                f"""
            <div class="{indicator['card_class']} indicator-critical">
                <h5>⚠️ {indicator['name']}
                    {f'<span class="points-badge {indicator["points_badge_class"]}">{indicator["points_text"]}</span>' if indicator["points_text"] else ''}
                </h5>
                <p><strong>Confidence:</strong> {indicator['confidence']}</p>
                <p><strong>Reasoning:</strong> {indicator['reasoning']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    if detected_warning:
        st.markdown("#### 🟡 WARNING Issues Detected")
        for indicator in detected_warning:
            st.markdown(
                f"""
            <div class="{indicator['card_class']} indicator-warning">
                <h5>⚠️ {indicator['name']}
                    {f'<span class="points-badge {indicator["points_badge_class"]}">{indicator["points_text"]}</span>' if indicator["points_text"] else ''}
                </h5>
                <p><strong>Confidence:</strong> {indicator['confidence']}</p>
                <p><strong>Reasoning:</strong> {indicator['reasoning']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    if detected_positive:
        st.markdown("#### 🟢 POSITIVE Patterns Detected")
        for indicator in detected_positive:
            st.markdown(
                f"""
            <div class="{indicator['card_class']} indicator-positive">
                <h5>✅ {indicator['name']}
                    {f'<span class="points-badge {indicator["points_badge_class"]}">{indicator["points_text"]}</span>' if indicator["points_text"] else ''}
                </h5>
                <p><strong>Confidence:</strong> {indicator['confidence']}</p>
                <p><strong>Reasoning:</strong> {indicator['reasoning']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    if detected_info:
        st.markdown("#### 🔵 INFO Context Detected")
        for indicator in detected_info:
            st.markdown(
                f"""
            <div class="{indicator['card_class']} indicator-info">
                <h5>ℹ️ {indicator['name']}
                    {f'<span class="points-badge {indicator["points_badge_class"]}">{indicator["points_text"]}</span>' if indicator["points_text"] else ''}
                </h5>
                <p><strong>Confidence:</strong> {indicator['confidence']}</p>
                <p><strong>Reasoning:</strong> {indicator['reasoning']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    if not_detected:
        st.markdown("#### ⚪ Not Detected")
        not_detected_names = [indicator["name"] for indicator in not_detected]
        st.write(", ".join(not_detected_names))

    # Summary
    total_indicators = len(quality_indicator_detections)
    detected_count = (
        len(detected_critical)
        + len(detected_warning)
        + len(detected_positive)
        + len(detected_info)
    )
    st.info(f"📋 Summary: {detected_count}/{total_indicators} indicators detected")


def create_export_data(result: Dict[str, Any]) -> Dict[str, Any]:
    """Create export data with only health score and overall assessment"""
    return {
        "health_score": extract_health_score(result),
        "overall_assessment": extract_overall_assessment(result),
    }


def main():
    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>💬 Conversation Health Analysis</h1>
        <p>Analyze conversation quality with AI-powered evaluation metrics</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ ERROR: OPENAI_API_KEY environment variable not set")
        st.info("Please set your OpenAI API key to use this application.")
        return

    # Initialize session state for storing results
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "analysis_transcript" not in st.session_state:
        st.session_state.analysis_transcript = ""

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Input method selection
        input_method = st.radio(
            "Input Method:", ["Test Cases", "Custom Input", "Upload File"]
        )

        transcript = ""

        # Test case selection
        if input_method == "Test Cases":
            test_cases = load_test_cases()

            if test_cases:
                case_options = {
                    f"{case_data['name']}": key for key, case_data in test_cases.items()
                }
                selected_case_name = st.selectbox(
                    "Select Test Case:", list(case_options.keys())
                )

                if selected_case_name:
                    selected_case_key = case_options[selected_case_name]
                    case_data = test_cases[selected_case_key]

                    st.markdown(
                        f"**Description:** {case_data.get('description', 'N/A')}"
                    )
                    st.markdown(
                        f"**Expected Health Level:** {case_data.get('expected_health_level', 'N/A')}"
                    )

                    transcript = case_data.get("transcript", "")
            else:
                st.warning("No test cases available")

        elif input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload conversation file", type=["txt", "json", "csv"]
            )
            if uploaded_file:
                transcript = str(uploaded_file.read(), "utf-8")

        # Analysis button in sidebar
        analyze_button = st.button("🔍 Analyze Conversation", type="primary")

    # Main content area
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 Input")

        if input_method == "Custom Input":
            transcript = st.text_area(
                "Conversation Transcript:",
                height=400,
                placeholder="Enter your conversation transcript here...",
            )
        else:
            st.text_area(
                "Conversation Transcript:",
                value=transcript,
                height=400,
                disabled=True,
                help="This is a preview of the selected input",
            )

    with col2:
        st.subheader("📈 Results")

        # Handle analysis button click
        if analyze_button and transcript.strip():
            result = run_analysis(transcript)

            if result:
                # Store results in session state IMMEDIATELY after successful analysis
                st.session_state.analysis_result = result
                st.session_state.analysis_transcript = transcript
                st.session_state.analysis_timestamp = str(int(time.time()))

                # Force a rerun to update the sidebar export button
                st.rerun()

        elif analyze_button and not transcript.strip():
            st.warning("Please enter a conversation transcript first!")

        # Display results (either new or cached)
        if st.session_state.analysis_result:
            final_assessment = st.session_state.analysis_result.get(
                "final_assessment", {}
            )

            # Display results sections
            display_overall_score(final_assessment)
            st.markdown("---")
            display_overall_assessment(final_assessment)
            st.markdown("---")
            display_identified_issues(st.session_state.analysis_result)
            st.markdown("---")
            display_criteria_evaluations(final_assessment)
            st.markdown("---")
            display_quality_indicators(final_assessment)

        else:
            st.info("👆 Select an input method and click 'Analyze' to see results")

    # Export section in sidebar (moved to bottom to ensure it appears after results are stored)
    with st.sidebar:
        if st.session_state.analysis_result:
            st.markdown("---")
            st.markdown("### 📥 Export Results")

            export_data = create_export_data(st.session_state.analysis_result)
            export_json = json.dumps(export_data, indent=2, default=str)

            st.download_button(
                label="📄 Download JSON Report",
                data=export_json,
                file_name=f"conversation_health_analysis_{st.session_state.get('analysis_timestamp', 'export')}.json",
                mime="application/json",
                help="Download complete analysis results as JSON file",
            )


if __name__ == "__main__":
    main()
