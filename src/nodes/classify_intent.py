"""Classify Intent Node - 사용자 의도 분류

사용자 입력을 LLM으로 분석하여 의도를 분류합니다.
- small_talk: 인사, 잡담
- technical_support: 기술 지원 요청
- continue_conversation: 기존 대화 계속
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from src.models.state import SupportState


def classify_intent_node(state: SupportState) -> Dict[str, Any]:
    """
    사용자 의도 분류 노드
    - LLM을 사용하여 정확한 의도 파악
    - 문맥을 고려한 분류

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (intent 설정)
    """

    # 대화 계속 여부 먼저 확인 (빠른 경로)
    has_steps = state.get("solution_steps") and len(state.get("solution_steps", [])) > 0
    was_waiting = state.get("status") == "waiting_user"

    if has_steps and was_waiting:
        # 기존 대화 계속
        state["intent"] = "continue_conversation"
        state["status"] = "evaluating"
        return state

    # 새 입력인 경우 LLM으로 분류
    last_user_message = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human":
            last_user_message = msg.content
            break

    # LLM 초기화
    llm_model = os.getenv("OLLAMA_LLM_MODEL", "gemma2:27b")
    llm = ChatOllama(
        model=llm_model,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0
    )

    # 의도 분류 프롬프트
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 고객 문의 의도를 분류하는 전문가입니다.

사용자 입력을 다음 중 하나로 분류하세요:

1. "small_talk": 인사, 잡담, 감사 인사
   예시:
   - "안녕하세요", "Hello", "Hi", "좋은 아침"
   - "반갑습니다", "오랜만이에요"
   - "감사합니다", "고마워요", "잘 부탁드립니다"
   - 단, "안녕하세요, 로그인이 안돼요"처럼 기술 문의가 포함되면 technical_support

2. "technical_support": 기술 지원, 문제 해결, 문의 요청
   예시:
   - "로그인이 안돼요", "파일 업로드 오류"
   - "비밀번호를 잊어버렸어요"
   - "메시지가 안 보내져요"
   - "계정을 삭제하고 싶어요"
   - "이 기능은 어떻게 사용하나요?"

중요: 인사와 문의가 함께 있으면 "technical_support"로 분류하세요.

JSON 형식으로 응답하세요:
{{"intent": "small_talk/technical_support", "reason": "분류 이유", "confidence": 0.0-1.0}}"""),
        ("user", f"사용자 입력: {last_user_message}")
    ])

    try:
        # LLM 호출
        chain = prompt | llm
        response = chain.invoke({})
        content = response.content.strip()

        # JSON 파싱 (코드 블록 제거)
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        classification = json.loads(content)
        intent = classification.get("intent", "technical_support")  # 기본값: 기술 지원
        confidence = classification.get("confidence", 0.0)

        # 상태 업데이트
        state["intent"] = intent
        state["intent_confidence"] = confidence

        if intent == "small_talk":
            state["status"] = "small_talking"
        else:  # technical_support
            state["status"] = "searching"

        # 디버그 정보 저장
        if state.get("debug_info") is None:
            state["debug_info"] = {}
        state["debug_info"]["intent_classification"] = {
            "intent": intent,
            "confidence": confidence,
            "reason": classification.get("reason", "")
        }

    except (json.JSONDecodeError, Exception) as e:
        # 에러 발생 시 안전하게 기술 지원으로 분류
        print(f"[ClassifyIntent] Warning: 분류 실패, 기술 지원으로 처리: {e}")
        state["intent"] = "technical_support"
        state["status"] = "searching"

    return state
