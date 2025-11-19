"""LangGraph State 모델

고객지원 챗봇의 전체 상태를 관리하는 State 객체를 정의합니다.
"""

from typing import TypedDict, List, Dict, Literal, Optional
from langchain_core.messages import BaseMessage


class SolutionStep(TypedDict):
    """해결 단계 구조"""
    step: int                                # 단계 번호
    action: str                              # 수행할 작업
    description: str                         # 상세 설명
    expected_result: str                     # 기대 결과
    completed: bool                          # 완료 여부


class SupportState(TypedDict):
    """고객지원 챗봇의 전체 상태"""

    # 대화 관련
    messages: List[BaseMessage]              # 전체 대화 히스토리
    current_query: str                       # 현재 사용자 질의

    # RAG 검색 결과
    retrieved_docs: List[Dict]               # 검색된 FAQ 문서들
    relevance_score: float                   # 관련성 점수

    # 단계별 답변 계획
    solution_steps: List[SolutionStep]       # 해결 단계 목록
    current_step: int                        # 현재 진행 중인 단계 (0부터 시작)
    max_steps: int                           # 최대 단계 수 (기본 3)

    # 상태 추적
    status: Literal[
        "initialized",        # 초기화됨
        "searching",          # 검색 중
        "small_talking",      # 스몰톡 중
        "planning",           # 답변 계획 중
        "responding",         # 응답 중
        "waiting_user",       # 사용자 응답 대기
        "evaluating",         # 평가 중
        "resolved",           # 해결됨
        "escalated",          # 에스컬레이션
        "confirming_ticket",  # 티켓 확인 중
        "evaluating_ticket",  # 티켓 응답 평가 중
        "ticket_created",     # 티켓 생성됨
        "cancelled"           # 티켓 취소됨
    ]

    # 에스컬레이션 관련
    attempts: int                            # 시도 횟수
    unresolved_reason: Optional[str]         # 미해결 사유
    ticket_id: Optional[str]                 # 생성된 티켓 ID
    ticket_confirmed: Optional[bool]         # 티켓 생성 확인 (True: 생성, False: 취소, None: 미정)
    ticket_additional_info: Optional[str]    # 티켓 추가 정보 (사용자 입력)

    # 의도 분류
    intent: Optional[Literal["small_talk", "technical_support", "continue_conversation"]]  # 사용자 의도
    intent_confidence: Optional[float]       # 의도 분류 신뢰도

    # 메타데이터
    user_id: str                             # 사용자 ID
    session_id: str                          # 세션 ID
    started_at: str                          # 시작 시간

    # 디버그 정보
    debug_info: Optional[Dict]               # 디버그 정보
