"""Initialize Node - 세션 초기화

대화 초기화 및 세션 정보 설정을 담당합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
import uuid
from typing import Dict, Any

from src.models.state import SupportState


def initialize_node(state: SupportState) -> Dict[str, Any]:
    """
    대화 초기화 노드
    - 세션 정보 설정
    - 초기 상태 설정
    - 신규 vs 계속 대화 구분

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
        state["is_continuing"] = False

        # 사용자 ID가 없으면 기본값 설정
        if "user_id" not in state or not state.get("user_id"):
            state["user_id"] = "anonymous"

    # 현재 쿼리 추출 (마지막 사용자 메시지)
    current_query = ""
    if state.get("messages"):
        for msg in reversed(state["messages"]):
            if msg.type == "human":
                current_query = msg.content
                state["current_query"] = current_query
                break

    # 스몰톡 감지 (인사말만 있는 경우)
    is_small_talk = False
    if current_query:
        lower_query = current_query.lower().strip()
        small_talk_keywords = ["안녕", "hello", "hi", "헬로", "하이", "반가워", "ㅎㅇ"]
        # 짧은 인사말이고 다른 내용이 없으면 스몰톡
        if len(lower_query) < 20 and any(kw in lower_query for kw in small_talk_keywords):
            is_small_talk = True

    state["is_small_talk"] = is_small_talk

    # 스몰톡이면 바로 처리
    if is_small_talk:
        state["status"] = "small_talking"
        return state

    # 티켓 확인 상태인지 확인
    is_confirming_ticket = state.get("status") == "confirming_ticket"

    if is_confirming_ticket:
        # 티켓 확인 응답 평가로
        state["status"] = "evaluating_ticket"
        return state

    # 대화 계속 여부 판단
    # 조건: 기존에 solution_steps가 있고, 현재 waiting_user 상태였다면 계속
    has_steps = state.get("solution_steps") and len(state.get("solution_steps", [])) > 0
    was_waiting = state.get("status") == "waiting_user"

    is_continuing = has_steps and was_waiting

    # 디버그 로그 (필요시 활성화)
    # print(f"[Initialize] has_steps={has_steps}, was_waiting={was_waiting}, is_continuing={is_continuing}")
    # print(f"[Initialize] status={state.get('status')}, steps={len(state.get('solution_steps', []))}")

    state["is_continuing"] = is_continuing

    if is_continuing:
        # 대화 계속: 검색 건너뛰고 evaluate로
        state["status"] = "evaluating"
        # print("[Initialize] → 대화 계속 (evaluating)")
    else:
        # 새 대화: 검색 시작
        state["status"] = "searching"
        # 시도 횟수 증가
        state["attempts"] = state.get("attempts", 0) + 1
        # print("[Initialize] → 새 대화 (searching)")

    return state
