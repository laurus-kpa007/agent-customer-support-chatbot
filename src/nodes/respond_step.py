"""Respond Step Node - 단계별 응답

현재 단계의 해결 방법을 사용자에게 안내합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from langchain_core.messages import AIMessage

from src.models.state import SupportState


def respond_step_node(state: SupportState) -> Dict[str, Any]:
    """
    현재 단계의 답변 제공
    - 사용자에게 현재 단계 안내
    - Human-in-the-Loop을 위한 응답 생성

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (messages에 응답 추가)
    """

    current_idx = state["current_step"]
    steps = state["solution_steps"]

    # 현재 단계가 없으면 에스컬레이션
    if current_idx >= len(steps):
        state["status"] = "escalated"
        state["unresolved_reason"] = "모든 단계를 시도했으나 해결되지 않음"

        response_text = (
            "😔 불편을 드려 죄송합니다.\n\n"
            "제안드린 모든 해결 방법을 시도하셨지만 문제가 해결되지 않은 것 같습니다.\n"
            "담당 부서의 확인이 필요한 상황입니다.\n\n"
            "💬 **현재까지의 문의 내용으로 문의를 등록하시겠습니까?**\n"
            "(답변: '네, 등록해주세요' 또는 '아니요')"
        )
    else:
        current_step = steps[current_idx]
        step_num = current_step["step"]
        total_steps = len(steps)

        response_text = (
            f"**[단계 {step_num}/{total_steps}]** {current_step['action']}\n\n"
            f"📝 {current_step['description']}\n\n"
            f"✅ **기대 결과**: {current_step['expected_result']}\n\n"
            f"---\n"
            f"이 단계를 확인하셨나요? 결과를 알려주세요.\n"
            f"(예: '해결됐어요', '안돼요', '다음 단계', '등록해주세요')"
        )

    # 응답 메시지 추가
    state["messages"].append(AIMessage(content=response_text))
    state["status"] = "waiting_user"

    return state
