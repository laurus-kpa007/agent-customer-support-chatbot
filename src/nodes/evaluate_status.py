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
from src.utils.state_reset import reset_conversation_state

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

    # 키워드 기반 빠른 판단 (매우 명확한 경우만, 나머지는 LLM에게)
    # 이렇게 하면 오타나 변형 표현은 LLM이 처리하여 더 강건함
    lower_msg = last_user_message.lower()

    # 1. 매우 명확한 해결 표현 (오타 가능성 낮음)
    if "해결됐어요" in lower_msg or "해결됐습니다" in lower_msg:
        if not ("안" in lower_msg or "못" in lower_msg):  # 부정어 없으면
            # print("[Evaluate] → 해결됨 (keyword: very clear)")  # 디버그
            state["status"] = "resolved"
            state["messages"].append(
                AIMessage(content="🎉 문제가 해결되어 다행입니다!\n\n추가로 도움이 필요하시면 언제든 문의해주세요. 😊")
            )
            state = reset_conversation_state(state)
            return state

    # 2. 매우 명확한 등록 요청 (오타 가능성 낮음)
    if "등록해주세요" in lower_msg or "등록해 주세요" in lower_msg:
        # print("[Evaluate] → 에스컬레이션 (keyword: direct request)")  # 디버그
        state["status"] = "escalated"
        state["unresolved_reason"] = "사용자가 직접 문의 등록 요청"
        return state

    # 나머지는 모두 LLM에게 위임 (오타, 변형, 애매한 표현 등 모두 처리)

    # LLM을 사용한 정밀 분석
    current_idx = state["current_step"]
    solution_steps = state.get("solution_steps", [])

    # solution_steps가 없거나 유효하지 않으면 에스컬레이션
    if not solution_steps or len(solution_steps) == 0:
        state["status"] = "escalated"
        state["unresolved_reason"] = "해결 단계가 없음"
        return state

    current_step = solution_steps[current_idx] if current_idx < len(solution_steps) else None

    # 3. 명확한 "행동만 보고" - continue 처리 (해결이 아님!)
    action_keywords = ["했어요", "했습니다", "해봤어요", "시도했어요", "확인했어요", "삭제했어요", "재설정했어요"]
    if any(keyword in lower_msg for keyword in action_keywords):
        # "됐어요"가 함께 있으면 해결일 수 있으므로 LLM에게 넘김
        if "됐어요" not in lower_msg and "됐습니다" not in lower_msg and "해결" not in lower_msg:
            # 순수하게 행동만 보고하는 경우 → 다음 단계로
            if current_step:
                current_step["completed"] = True
            state["current_step"] += 1
            state["status"] = "responding"
            # print(f"[Evaluate] → continue (keyword: action only)")  # 디버그
            return state

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 고객지원 대화를 분석하는 전문가입니다.
사용자의 응답을 분석하여 문제 해결 여부를 판단하세요.

**핵심 원칙: 단계를 수행했다는 것(행동)과 문제가 해결됐다는 것(결과)을 명확히 구분!**

판단 기준:

1. "resolved" (문제 해결됨) - 결과가 좋다고 명시:
   - "해결됐어요", "문제 없어요", "잘 돼요", "잘 됩니다", "정상이에요"
   - "됐어요!", "됐습니다!" (결과 긍정)
   - "괜찮아요", "다 고쳐졌어요"
   - "감사합니다" (단, "~했어요 감사합니다"는 제외 - 이건 continue)

2. "continue" (다음 단계 필요) - 행동만 했거나 여전히 문제:
   - **행동만 보고** (해결 아님!):
     * "했어요", "했습니다", "했네요" (예: "재설정했어요", "확인했어요", "삭제했어요")
     * "해봤어요", "시도했어요", "체크했어요"
   - **부정 표현**:
     * "안돼요", "안 됩니다", "안 되네요", "실패했어요"
     * "여전히", "그래도", "계속", "또", "똑같아요"
   - **행동 + 부정**:
     * "했는데 안돼요", "했지만 여전히", "해봤는데 그래도"
   - **대기/확인 중**:
     * "잠시만요", "확인해볼게요", "해볼게요", "시도해볼게요"
     * "알겠습니다", "네 그럴게요"
     * → 사용자가 단계를 수행하러 간 것, 결과 대기 필요

3. "escalate" (문의 등록 요청):
   - "등록해주세요", "상담원", "문의하겠습니다", "티켓"

**중요 예시:**
- "비밀번호 재설정했어요" → **continue** (행동만 보고, 로그인 성공은 아직)
- "비밀번호 재설정했어요 감사합니다" → **continue** (여전히 행동 보고)
- "삭제했어요" → **continue** (삭제는 행동, 문제 해결은 결과)
- "캐시 삭제했는데 안돼요" → **continue** (부정 표현)
- "잠시만요, 확인해볼게요" → **continue** (대기/확인 중)
- "네 알겠습니다 해볼게요" → **continue** (대기/확인 중)
- "이제 잘 돼요!" → **resolved** (결과 긍정)
- "해결됐어요 감사합니다" → **resolved** (명확한 해결 + 감사)
- "이제 정상이에요" → **resolved** (결과 긍정)

JSON 형식으로만 응답:
{{"decision": "resolved|continue|escalate", "reason": "판단 이유"}}"""),
        ("user", """현재 단계: {current_step}
사용자 응답: {user_response}

위 응답을 분석하여 JSON으로 판단 결과를 출력하세요.""")
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
            # 대화 상태 초기화
            state = reset_conversation_state(state)
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
