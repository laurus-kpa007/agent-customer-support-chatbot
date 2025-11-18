"""Routing Logic - 워크플로우 라우팅

조건부 엣지를 위한 라우팅 로직을 정의합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import SupportState


def route_after_respond(state: SupportState) -> str:
    """
    respond_step 노드 이후 다음 액션 결정
    - 첫 응답이면 END (사용자 답변 대기)
    - 사용자가 이미 답변했으면 evaluate로

    Args:
        state: 현재 상태

    Returns:
        다음 노드 이름 ("wait_user", "evaluate")
    """

    # 메시지 수를 체크해서 첫 응답인지 판단
    # 첫 질문(1개) + AI 첫 응답(1개) = 2개이면 사용자 대기
    # 그 이상이면 사용자가 이미 답변한 것
    message_count = len(state.get("messages", []))

    # AI가 방금 응답을 추가했으므로
    # 2개 이하면 첫 응답 (사용자 1 + AI 1)
    if message_count <= 2:
        return "wait_user"

    # 그 이상이면 사용자가 답변한 것이므로 evaluate
    return "evaluate"


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
