"""Routing Logic - 워크플로우 라우팅

조건부 엣지를 위한 라우팅 로직을 정의합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import SupportState


def route_after_evaluate(state: SupportState) -> str:
    """
    evaluate_status 노드 이후 다음 액션 결정

    Args:
        state: 현재 상태

    Returns:
        다음 노드 이름 ("continue", "resolved", "escalate")
    """

    # 해결됨으로 표시된 경우
    if state["status"] == "resolved":
        return "resolved"

    # 에스컬레이션 (티켓 생성)
    if state["status"] == "escalated":
        return "escalate"

    # 모든 단계를 시도했는데도 해결 안됨
    if state["current_step"] >= len(state["solution_steps"]):
        return "escalate"

    # 최대 시도 횟수 초과
    if state.get("attempts", 0) >= 10:
        return "escalate"

    # 다음 단계 계속
    return "continue"
