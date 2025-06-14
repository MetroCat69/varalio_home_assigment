def merge_dicts(left: dict, right: dict) -> dict:
    if left is None:
        left = {}
    if right is None:
        right = {}
    return {**left, **right}


def extract_health_score(result: dict) -> dict:
    if not result:
        return {}

    final_assessment = result.get("final_assessment", {})
    health_score = final_assessment.get("health_score", {})

    return health_score if isinstance(health_score, dict) else {}


def extract_overall_assessment(result: dict) -> str:
    if not result:
        return ""

    final_assessment = result.get("final_assessment", {})
    overall_assessment = final_assessment.get("overall_assessment", "")

    return overall_assessment if isinstance(overall_assessment, str) else ""
