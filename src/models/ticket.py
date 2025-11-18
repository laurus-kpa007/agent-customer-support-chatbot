"""Ticket 데이터 모델

Q&A 게시판에 등록되는 티켓 구조를 정의합니다.
"""

from typing import TypedDict, List, Dict, Literal, Optional


class Ticket(TypedDict):
    """Q&A 게시판 티켓 구조"""
    ticket_id: str                           # 티켓 ID
    user_id: str                             # 사용자 ID
    session_id: str                          # 세션 ID
    title: str                               # 제목
    summary: str                             # 문제 상황 요약
    attempted_solutions: List[str]           # 시도한 해결방법들
    conversation_history: List[Dict]         # 전체 대화 내역
    category: str                            # 카테고리
    status: Literal["open", "answered", "closed"]  # 상태
    created_at: str                          # 생성 시간
    answered_at: Optional[str]               # 답변 시간
    answer: Optional[str]                    # 답변 내용
