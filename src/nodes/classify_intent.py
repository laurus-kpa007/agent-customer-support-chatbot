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

1. "small_talk": 인사, 잡담, 감사 인사, 챗봇에 대한 질문
   예시:
   - 인사: "안녕하세요", "Hello", "Hi", "좋은 아침", "반갑습니다"
   - 감사: "감사합니다", "고마워요", "잘 부탁드립니다"
   - 챗봇 관련: "넌 누구니?", "당신은 누구세요?", "무엇을 도와주나요?"
   - 잡담: "날씨가 좋네요", "요즘 어때요?"

2. "technical_support": 명확하고 구체적인 기술 문제/요청
   예시:
   - 구체적 문제: "로그인이 안돼요", "파일 업로드 오류", "메시지가 안 보내져요"
   - 구체적 요청: "비밀번호를 잊어버렸어요", "계정을 삭제하고 싶어요"
   - 사용법: "이 기능은 어떻게 사용하나요?", "설정을 변경하려면?"

3. "vague_problem": 문제가 있지만 증상이 불명확한 경우 (Human-in-the-Loop 필요)
   예시:
   - 모호한 표현: "메신저가 이상해", "앱이 좀 그래", "뭔가 안 돼"
   - 추상적: "문제가 생겼어", "잘 안 돼요", "이상한데요"
   - 감정만 표현: "답답해요", "짜증나네요", "속상해"
   → 이 경우 구체적인 증상을 먼저 물어봐야 함!

판단 기준:
- 구체적인 기능/증상 언급 → technical_support
- 문제는 있지만 증상 불명확 → vague_problem
- 인사와 명확한 문의가 함께 → technical_support
- 인사와 모호한 문제가 함께 → vague_problem

JSON 형식으로 응답하세요:
{{"intent": "small_talk/technical_support/vague_problem", "reason": "분류 이유", "confidence": 0.0-1.0}}"""),
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
        elif intent == "vague_problem":
            state["status"] = "clarifying"  # 증상 명확화 필요
            state["needs_clarification"] = True
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
