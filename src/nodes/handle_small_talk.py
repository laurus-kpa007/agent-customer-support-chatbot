"""Handle Small Talk Node - 스몰톡 처리

인사말 등 일반적인 대화에 대응합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
import os
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

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

    # LLM 초기화
    llm_model = os.getenv("OLLAMA_LLM_MODEL", "gemma2:27b")
    llm = ChatOllama(
        model=llm_model,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.7  # 약간의 창의성 허용
    )

    # 마지막 사용자 메시지 가져오기
    last_user_message = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human":
            last_user_message = msg.content
            break

    # 스몰톡 응답 프롬프트
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 친절하고 전문적인 고객 지원 AI 상담원입니다.
        
        사용자의 인사나 잡담에 대해 자연스럽고 인간적으로 응답하세요.
        응답 후에는 부드럽게 도움이 필요한 부분이 있는지 물어보세요.
        
        다음과 같은 문제들을 도와줄 수 있음을 자연스럽게 언급해도 좋습니다(매번 언급할 필요는 없음):
        - 로그인/비밀번호 문제
        - 메신저 기능 오류
        - 파일 업로드/다운로드 문제
        - 계정 관련 문의
        
        어조:
        - 공감하고 친근하게
        - 이모지(👋, 😊 등)를 적절히 사용하여 딱딱하지 않게
        - 너무 길지 않게 간결하게
        """),
        ("user", f"{last_user_message}")
    ])

    # LLM 호출 및 응답 생성
    chain = prompt | llm
    response = chain.invoke({})
    response_text = response.content

    # 응답 메시지 추가
    state["messages"].append(AIMessage(content=response_text))
    state["status"] = "waiting_user"

    # 스몰톡 플래그 초기화 (다음 입력은 실제 문의일 것)
    state["is_small_talk"] = False

    return state
