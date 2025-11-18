"""Evaluate Ticket Confirmation - 티켓 확인 평가

사용자의 티켓 등록 의사를 평가합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from langchain_core.messages import AIMessage

from src.models.state import SupportState


def evaluate_ticket_confirmation_node(state: SupportState) -> Dict[str, Any]:
    """
    티켓 확인 평가 노드
    - 사용자가 '네' 또는 '아니요'를 선택했는지 판단

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (ticket_confirmed 설정)
    """

    # 마지막 사용자 응답 가져오기
    last_user_message = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human":
            last_user_message = msg.content
            break

    lower_msg = last_user_message.lower().strip()

    # 긍정 응답
    if any(keyword in lower_msg for keyword in ["네", "yes", "등록", "예", "응", "ㅇㅇ", "ok", "okay"]):
        state["ticket_confirmed"] = True
        state["status"] = "escalated"
    # 부정 응답
    elif any(keyword in lower_msg for keyword in ["아니", "no", "취소", "안", "ㄴㄴ"]):
        state["ticket_confirmed"] = False
        state["status"] = "cancelled"
        state["messages"].append(
            AIMessage(content=(
                "알겠습니다. 문의 등록을 취소했습니다.\n\n"
                "다른 도움이 필요하시면 언제든 말씀해주세요. 😊"
            ))
        )
    else:
        # 명확하지 않은 응답 - 재확인
        state["ticket_confirmed"] = None
        state["messages"].append(
            AIMessage(content=(
                "죄송합니다. 명확하게 이해하지 못했습니다.\n\n"
                "문의를 등록하시려면 '네' 또는 '등록해주세요'라고 답변해주세요.\n"
                "등록을 원하지 않으시면 '아니요' 또는 '취소'라고 답변해주세요."
            ))
        )

    return state
