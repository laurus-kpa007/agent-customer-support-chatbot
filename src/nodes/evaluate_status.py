"""Evaluate Status Node - 상태 평가

사용자 응답을 분석하여 문제 해결 여부를 판단합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
import json
from typing import Dict, Any

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from dotenv import load_dotenv

from src.models.state import SupportState

# 환경 변수 로드
load_dotenv()


def evaluate_status_node(state: SupportState) -> Dict[str, Any]:
    """
    사용자 응답 평가
    - 문제가 해결되었는지 판단
    - 다음 단계로 진행할지 결정

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (status 업데이트)
    """

    # print(f"[Evaluate] 시작 - current_step={state.get('current_step')}, total_steps={len(state.get('solution_steps', []))}")  # 디버그

    # LLM 초기화
    llm_model = os.getenv("OLLAMA_LLM_MODEL", "gemma2:27b")
    llm = ChatOllama(
        model=llm_model,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0
    )

    # 마지막 사용자 응답 가져오기
    last_user_message = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human":
            last_user_message = msg.content
            break

    # print(f"[Evaluate] 사용자 응답: {last_user_message}")  # 디버그

    # 간단한 키워드 기반 판단 (빠른 응답)
    lower_msg = last_user_message.lower()

    # 해결됨
    if any(keyword in lower_msg for keyword in ["해결", "됐어요", "됐습니다", "감사", "고마워"]):
        # print("[Evaluate] → 해결됨 (resolved)")  # 디버그
        state["status"] = "resolved"
        state["messages"].append(
            AIMessage(content="🎉 문제가 해결되어 다행입니다!\n\n추가로 도움이 필요하시면 언제든 문의해주세요. 😊")
        )
        return state

    # 에스컬레이션
    if any(keyword in lower_msg for keyword in ["등록", "문의", "티켓", "상담원"]):
        # print("[Evaluate] → 에스컬레이션 (escalated)")  # 디버그
        state["status"] = "escalated"
        state["unresolved_reason"] = "사용자가 직접 문의 등록 요청"
        return state

    # LLM을 사용한 정밀 분석
    current_idx = state["current_step"]
    solution_steps = state.get("solution_steps", [])

    # solution_steps가 없거나 유효하지 않으면 에스컬레이션
    if not solution_steps or len(solution_steps) == 0:
        state["status"] = "escalated"
        state["unresolved_reason"] = "해결 단계가 없음"
        return state

    current_step = solution_steps[current_idx] if current_idx < len(solution_steps) else None

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 고객지원 대화를 분석하는 전문가입니다.
사용자의 응답을 분석하여 다음 중 하나를 판단하세요:

1. "resolved": 문제가 해결됨
2. "continue": 현재 단계가 효과 없음, 다음 단계 필요
3. "escalate": 사용자가 명시적으로 문의 등록 요청

판단 기준:
- "해결됐어요", "됐어요", "감사합니다" 등 → resolved
- "안돼요", "여전히", "체크되어 있는데", "안 됩니다" 등 → continue
- "등록해주세요", "문의할게요", "상담원" 등 → escalate

JSON 형식으로 응답:
{{"decision": "resolved|continue|escalate", "reason": "판단 이유"}}

JSON만 출력하세요."""),
        ("user", """현재 단계: {current_step}
사용자 응답: {user_response}""")
    ])

    try:
        response = llm.invoke(
            prompt.format_messages(
                current_step=str(current_step) if current_step else "N/A",
                user_response=last_user_message
            )
        )

        # JSON 파싱
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        evaluation = json.loads(content)
        decision = evaluation.get("decision", "continue")

        if decision == "resolved":
            # print("[Evaluate] LLM 판단 → resolved")  # 디버그
            state["status"] = "resolved"
            state["messages"].append(
                AIMessage(content="🎉 문제가 해결되어 다행입니다!\n\n추가로 도움이 필요하시면 언제든 문의해주세요. 😊")
            )
        elif decision == "escalate":
            # print("[Evaluate] LLM 판단 → escalate")  # 디버그
            state["status"] = "escalated"
            state["unresolved_reason"] = evaluation.get("reason", "사용자 요청")
        else:  # continue
            # print(f"[Evaluate] LLM 판단 → continue (step {current_idx} → {current_idx + 1})")  # 디버그
            # 현재 단계를 완료로 표시하고 다음 단계로
            if current_step:
                current_step["completed"] = True
            state["current_step"] += 1
            state["status"] = "responding"

    except (json.JSONDecodeError, Exception) as e:
        # 기본 동작: 다음 단계로
        # print(f"[Evaluate] Warning: 평가 실패, 다음 단계로 진행: {e}")  # 디버그
        if current_step:
            current_step["completed"] = True
        state["current_step"] += 1
        state["status"] = "responding"

    # print(f"[Evaluate] 완료 - status={state['status']}, current_step={state.get('current_step')}")  # 디버그
    return state
