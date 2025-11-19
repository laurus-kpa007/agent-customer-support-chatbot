"""Ask Symptoms Node - 증상 명확화 질문

모호한 문제 표현("메신저가 이상해")에 대해 구체적인 증상을 물어봅니다.
Human-in-the-Loop 적용.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from langchain_core.messages import AIMessage

from src.models.state import SupportState


def ask_symptoms_node(state: SupportState) -> Dict[str, Any]:
    """
    증상 명확화 질문 노드
    - 모호한 문제에 대해 구체적인 증상 질문
    - Human-in-the-Loop: 사용자 응답 대기

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (AI 질문 메시지 추가)
    """

    # 사용자가 언급한 모호한 문제 가져오기
    last_user_message = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human":
            last_user_message = msg.content
            break

    # 구체적인 증상을 물어보는 메시지 생성
    clarification_message = (
        f"네, '{last_user_message}'라고 하셨네요.\n\n"
        "문제를 정확히 파악하기 위해 몇 가지 여쭤볼게요:\n\n"
        "**어떤 증상이 나타나나요?**\n"
        "예를 들어:\n"
        "- 특정 기능이 작동하지 않나요?\n"
        "- 오류 메시지가 표시되나요?\n"
        "- 느리거나 멈추는 현상이 있나요?\n"
        "- 그 외 다른 증상이 있나요?\n\n"
        "최대한 구체적으로 알려주시면 더 정확한 해결 방법을 안내해드릴 수 있습니다. 😊"
    )

    # AI 응답 추가
    state["messages"].append(AIMessage(content=clarification_message))
    state["status"] = "waiting_user"  # 사용자 응답 대기

    return state
