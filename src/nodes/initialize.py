"""Initialize Node - 세션 초기화

대화 초기화 및 세션 정보 설정을 담당합니다.
"""

from datetime import datetime
import uuid
from typing import Dict, Any

from ..models.state import SupportState


def initialize_node(state: SupportState) -> Dict[str, Any]:
    """
    대화 초기화 노드
    - 세션 정보 설정
    - 초기 상태 설정

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태
    """

    # 첫 실행시에만 초기화
    if "session_id" not in state or not state.get("session_id"):
        state["session_id"] = str(uuid.uuid4())
        state["started_at"] = datetime.now().isoformat()
        state["attempts"] = 0
        state["current_step"] = 0
        state["max_steps"] = 3
        state["solution_steps"] = []
        state["retrieved_docs"] = []
        state["relevance_score"] = 0.0
        state["unresolved_reason"] = None
        state["ticket_id"] = None

        # 사용자 ID가 없으면 기본값 설정
        if "user_id" not in state or not state.get("user_id"):
            state["user_id"] = "anonymous"

    # 현재 쿼리 추출 (마지막 사용자 메시지)
    if state.get("messages"):
        for msg in reversed(state["messages"]):
            if msg.type == "human":
                state["current_query"] = msg.content
                break

    # 시도 횟수 증가
    state["attempts"] = state.get("attempts", 0) + 1
    state["status"] = "searching"

    return state
