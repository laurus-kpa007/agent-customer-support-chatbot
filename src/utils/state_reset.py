"""State Reset Utility - 대화 상태 초기화

문제 해결 완료 또는 티켓 생성 후 상태를 초기화합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from src.models.state import SupportState


def reset_conversation_state(state: SupportState) -> Dict[str, Any]:
    """
    대화 상태 초기화
    - 새로운 대화를 시작할 수 있도록 상태를 리셋
    - session_id, user_id, messages는 유지 (대화 연속성)
    - 문제 해결 관련 상태는 모두 초기화

    Args:
        state: 현재 상태

    Returns:
        초기화된 상태
    """

    # 초기화할 필드들
    state["solution_steps"] = []
    state["current_step"] = 0
    state["retrieved_docs"] = []
    state["relevance_score"] = 0.0
    state["unresolved_reason"] = None
    state["ticket_id"] = None
    state["is_continuing"] = False
    state["attempts"] = 0
    state["intent"] = None
    state["intent_confidence"] = None
    state["ticket_confirmed"] = None
    state["current_query"] = ""

    # status는 초기 상태로 변경하지 않음 (END 노드로 가기 위해)
    # status는 각 노드에서 설정 (resolved, ticket_created 등)

    return state
