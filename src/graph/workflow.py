"""Workflow - LangGraph StateGraph 구성

고객지원 챗봇의 전체 워크플로우를 정의합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from langgraph.graph import StateGraph, END

from src.models.state import SupportState
from src.nodes import (
    initialize_node,
    classify_intent_node,
    handle_small_talk_node,
    search_knowledge_node,
    plan_response_node,
    respond_step_node,
    evaluate_status_node,
    confirm_ticket_node,
    evaluate_ticket_confirmation_node,
    create_ticket_node,
    send_notification_node,
)
from src.graph.routing import (
    route_after_initialize,
    route_after_respond,
    route_after_evaluate,
    route_after_ticket_confirmation
)


def create_workflow() -> StateGraph:
    """
    고객지원 챗봇 워크플로우 생성

    Returns:
        컴파일된 StateGraph 애플리케이션
    """

    # StateGraph 생성
    workflow = StateGraph(SupportState)

    # 노드 추가
    workflow.add_node("initialize", initialize_node)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("handle_small_talk", handle_small_talk_node)
    workflow.add_node("search_knowledge", search_knowledge_node)
    workflow.add_node("plan_response", plan_response_node)
    workflow.add_node("respond_step", respond_step_node)
    workflow.add_node("evaluate_status", evaluate_status_node)
    workflow.add_node("confirm_ticket", confirm_ticket_node)
    workflow.add_node("evaluate_ticket_confirmation", evaluate_ticket_confirmation_node)
    workflow.add_node("create_ticket", create_ticket_node)
    workflow.add_node("send_notification", send_notification_node)

    # 엣지 정의
    workflow.set_entry_point("initialize")

    # initialize 후 조건부 라우팅 (티켓 평가 / 의도 분류 / 평가)
    workflow.add_conditional_edges(
        "initialize",
        route_after_initialize,
        {
            "evaluate_ticket": "evaluate_ticket_confirmation",  # 티켓 확인 평가
            "classify": "classify_intent",                       # 의도 분류 (새 입력)
            "evaluate": "evaluate_status"                        # 기존 대화 - 평가
        }
    )

    # classify_intent 후 조건부 라우팅 (스몰톡 / 기술 지원)
    def route_after_classify(state):
        intent = state.get("intent", "technical_support")
        if intent == "small_talk":
            return "small_talk"
        else:  # technical_support or continue_conversation
            if intent == "continue_conversation":
                return "evaluate"
            return "search"

    workflow.add_conditional_edges(
        "classify_intent",
        route_after_classify,
        {
            "small_talk": "handle_small_talk",       # 스몰톡
            "search": "search_knowledge",             # 기술 지원 - 검색
            "evaluate": "evaluate_status"             # 대화 계속 - 평가
        }
    )

    # 스몰톡 후 사용자 대기
    workflow.add_edge("handle_small_talk", END)

    workflow.add_edge("search_knowledge", "plan_response")
    # plan_response 후 조건부 라우팅 (검색 실패 시 티켓 확인으로 이동)
    def route_after_plan(state):
        if state.get("status") == "escalated":
            return "confirm_ticket"
        return "respond_step"

    workflow.add_conditional_edges(
        "plan_response",
        route_after_plan,
        {
            "confirm_ticket": "confirm_ticket",
            "respond_step": "respond_step"
        }
    )

    # respond_step 후 항상 사용자 대기 (Human-in-the-Loop)
    workflow.add_edge("respond_step", END)

    # 조건부 라우팅: evaluate_status 이후
    workflow.add_conditional_edges(
        "evaluate_status",
        route_after_evaluate,
        {
            "continue": "respond_step",         # 다음 단계 계속
            "resolved": END,                    # 해결 완료
            "confirm_ticket": "confirm_ticket"  # 티켓 확인
        }
    )

    # 티켓 확인 후 사용자 대기
    workflow.add_edge("confirm_ticket", END)

    # 티켓 확인 평가 후 조건부 라우팅
    workflow.add_conditional_edges(
        "evaluate_ticket_confirmation",
        route_after_ticket_confirmation,
        {
            "create": "create_ticket",     # 티켓 생성
            "cancelled": END,               # 취소
            "wait": END                     # 재확인 대기
        }
    )

    workflow.add_edge("create_ticket", "send_notification")
    workflow.add_edge("send_notification", END)

    # 컴파일 (체크포인터 없이 - PoC용)
    app = workflow.compile()

    return app


def get_workflow_graph():
    """
    워크플로우 그래프 시각화용

    Returns:
        그래프 다이어그램
    """
    app = create_workflow()
    return app.get_graph()
