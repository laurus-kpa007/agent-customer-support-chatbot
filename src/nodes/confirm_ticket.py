"""Confirm Ticket Node - 티켓 생성 확인

티켓을 생성하기 전에 사용자에게 확인을 요청합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from langchain_core.messages import AIMessage

from src.models.state import SupportState


def confirm_ticket_node(state: SupportState) -> Dict[str, Any]:
    """
    티켓 생성 확인 노드
    - 현재까지의 대화 내용 요약
    - 티켓 등록 의사 확인

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (messages에 확인 요청 추가)
    """

    # 문의 내용 요약
    query = state.get("current_query", "문의 내용")
    attempted_steps = state.get("current_step", 0)
    total_steps = len(state.get("solution_steps", []))

    # 확인 메시지 생성
    response_text = (
        "😔 불편을 드려 죄송합니다.\n\n"
    )

    if attempted_steps > 0:
        response_text += f"지금까지 {attempted_steps}단계를 시도하셨지만 문제가 해결되지 않은 것 같습니다.\n"

    response_text += (
        "담당 부서의 확인이 필요한 상황입니다.\n\n"
        "📋 **등록될 문의 내용:**\n"
        f"- 문제: {query}\n"
    )

    if attempted_steps > 0:
        response_text += f"- 시도한 해결 방법: {attempted_steps}개 단계\n"

    response_text += (
        "\n"
        "💬 **이 내용으로 문의를 등록하시겠습니까?**\n\n"
        "답변해주세요:\n"
        "- '네' 또는 '등록해주세요' → 문의 등록\n"
        "- '아니요' 또는 '취소' → 문의 등록 취소"
    )

    # 응답 메시지 추가
    state["messages"].append(AIMessage(content=response_text))
    state["status"] = "confirming_ticket"

    return state
