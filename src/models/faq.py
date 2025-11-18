"""FAQ 데이터 모델

FAQ 문서 구조를 정의합니다.
증상(symptom), 원인(cause), 해결방법(solutions) 구조를 사용합니다.
"""

from typing import TypedDict, List, Literal


class FAQSolution(TypedDict):
    """개별 해결 방법 구조"""
    method: int                              # 방법 번호 (1, 2, 3, ...)
    title: str                               # 방법 제목
    steps: List[str]                         # 실행 단계들
    expected_result: str                     # 기대되는 결과


class FAQContent(TypedDict):
    """FAQ 본문 구조 (증상/원인/임시조치)"""
    symptom: str                             # 증상 설명
    cause: str                               # 원인 설명
    solutions: List[FAQSolution]             # 임시조치 방법들 (방법1, 방법2, ...)


class FAQDocument(TypedDict):
    """FAQ 문서 구조"""
    id: str                                  # 문서 ID (예: FAQ-001)
    category: str                            # 카테고리 (메신저, 로그인, 알림 등)
    title: str                               # 게시글 제목
    content: FAQContent                      # 본문 (증상/원인/임시조치)
    tags: List[str]                          # 태그
    created_at: str                          # 생성일
    updated_at: str                          # 수정일
    view_count: int                          # 조회수
    helpful_count: int                       # 도움됨 수
    source: Literal["faq", "qa_board"]       # 출처
