"""Routing Logic - 워크플로우 라우팅

조건부 엣지를 위한 라우팅 로직을 정의합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.state import SupportState


def route_after_initialize(state: SupportState) -> str:
    """
    initialize 노드 이후 다음 액션 결정
    - 티켓 확인 중이면 티켓 평가 (evaluate_ticket_confirmation)
    - 기존 대화 계속이면 평가 (evaluate_status)
    - 새 입력이면 의도 분류 (classify_intent)

    Args:
        state: 현재 상태

    Returns:
        다음 노드 이름 ("evaluate_ticket", "classify", "evaluate")
    """

    status = state.get("status")

    # 티켓 확인 평가 우선
    if status == "evaluating_ticket":
        return "evaluate_ticket"

    # 대화 평가 vs 의도 분류 (새 입력)
    route = "evaluate" if status == "evaluating" else "classify"
    # print(f"[RouteAfterInit] status={status} → {route}")  # 디버그

    return route


def route_after_respond(state: SupportState) -> str:
    """
    respond_step 노드 이후 다음 액션 결정
    - 항상 사용자 답변 대기 (Human-in-the-Loop)

    Args:
        state: 현재 상태

    Returns:
        다음 노드 이름 ("wait_user")
    """

    # respond_step은 항상 사용자 응답을 기다림
    # 사용자가 응답하면 initialize → evaluate 경로로 재진입
    return "wait_user"


def route_after_evaluate(state: SupportState) -> str:
    """
    evaluate_status 노드 이후 다음 액션 결정

    Args:
        state: 현재 상태

    Returns:
        다음 노드 이름 ("continue", "resolved", "confirm_ticket")
    """

    # 해결됨으로 표시된 경우
    if state["status"] == "resolved":
        return "resolved"

    # 에스컬레이션 (티켓 확인 단계로)
    if state["status"] == "escalated":
        return "confirm_ticket"

    # 모든 단계를 시도했는데도 해결 안됨 → 티켓 확인
    if state["current_step"] >= len(state["solution_steps"]):
        return "confirm_ticket"

    # 최대 시도 횟수 초과 → 티켓 확인
    if state.get("attempts", 0) >= 10:
        return "confirm_ticket"

    # 다음 단계 계속
    return "continue"


def route_after_ticket_confirmation(state: SupportState) -> str:
    """
    티켓 확인 평가 후 다음 액션 결정

    Args:
        state: 현재 상태

    Returns:
        다음 노드 이름 ("create", "cancelled", "wait")
    """

    ticket_confirmed = state.get("ticket_confirmed")

    if ticket_confirmed is True:
        return "create"
    elif ticket_confirmed is False:
        return "cancelled"
    else:
        # 명확하지 않은 응답 - 재확인 대기
        return "wait"
