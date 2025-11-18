"""Handle Small Talk Node - 스몰톡 처리

인사말 등 일반적인 대화에 대응합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from langchain_core.messages import AIMessage

from src.models.state import SupportState


def handle_small_talk_node(state: SupportState) -> Dict[str, Any]:
    """
    스몰톡 처리 노드
    - 인사말에 적절히 응답
    - 도움이 필요한지 물어봄

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (messages에 응답 추가)
    """

    response_text = (
        "안녕하세요! 👋\n\n"
        "고객지원 챗봇입니다. 무엇을 도와드릴까요?\n\n"
        "예를 들어 다음과 같은 문제를 도와드릴 수 있습니다:\n"
        "- 로그인/비밀번호 문제\n"
        "- 메신저 기능 오류\n"
        "- 파일 업로드/다운로드 문제\n"
        "- 계정 관련 문의\n\n"
        "어떤 문제가 있으신가요?"
    )

    # 응답 메시지 추가
    state["messages"].append(AIMessage(content=response_text))
    state["status"] = "waiting_user"

    # 스몰톡 플래그 초기화 (다음 입력은 실제 문의일 것)
    state["is_small_talk"] = False

    return state
