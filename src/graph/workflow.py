"""Workflow - LangGraph StateGraph 구성

고객지원 챗봇의 전체 워크플로우를 정의합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.models.state import SupportState
from src.nodes import (
    initialize_node,
    search_knowledge_node,
    plan_response_node,
    respond_step_node,
    evaluate_status_node,
    create_ticket_node,
    send_notification_node,
)
from src.graph.routing import route_after_respond, route_after_evaluate


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
    workflow.add_node("search_knowledge", search_knowledge_node)
    workflow.add_node("plan_response", plan_response_node)
    workflow.add_node("respond_step", respond_step_node)
    workflow.add_node("evaluate_status", evaluate_status_node)
    workflow.add_node("create_ticket", create_ticket_node)
    workflow.add_node("send_notification", send_notification_node)

    # 엣지 정의
    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "search_knowledge")
    workflow.add_edge("search_knowledge", "plan_response")
    workflow.add_edge("plan_response", "respond_step")

    # respond_step 후 조건부 라우팅 (Human-in-the-Loop)
    workflow.add_conditional_edges(
        "respond_step",
        route_after_respond,
        {
            "wait_user": END,                # 첫 응답 - 사용자 답변 대기
            "evaluate": "evaluate_status"    # 사용자가 답변함 - 평가
        }
    )

    # 조건부 라우팅: evaluate_status 이후
    workflow.add_conditional_edges(
        "evaluate_status",
        route_after_evaluate,
        {
            "continue": "respond_step",      # 다음 단계 계속
            "resolved": END,                 # 해결 완료
            "escalate": "create_ticket"      # 티켓 생성
        }
    )

    workflow.add_edge("create_ticket", "send_notification")
    workflow.add_edge("send_notification", END)

    # 체크포인터 추가 (대화 상태 유지 - 메모리 기반)
    memory = MemorySaver()

    # 컴파일
    app = workflow.compile(checkpointer=memory)

    return app


def get_workflow_graph():
    """
    워크플로우 그래프 시각화용

    Returns:
        그래프 다이어그램
    """
    app = create_workflow()
    return app.get_graph()
