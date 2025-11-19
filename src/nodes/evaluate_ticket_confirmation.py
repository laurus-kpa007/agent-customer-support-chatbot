"""Evaluate Ticket Confirmation - 티켓 확인 평가

사용자의 티켓 등록 의사를 평가합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
import json
from typing import Dict, Any
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from src.models.state import SupportState


def evaluate_ticket_confirmation_node(state: SupportState) -> Dict[str, Any]:
    """
    티켓 확인 평가 노드
    - LLM을 사용하여 사용자의 긍정/부정 의사를 정확히 판단

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (ticket_confirmed 설정)
    """

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

    # LLM 프롬프트
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 사용자의 의사를 정확히 파악하는 전문가입니다.

사용자가 문의 티켓 등록을 원하는지 판단하세요.
또한, 사용자가 추가로 언급한 내용이 있다면 추출하세요.

다음 중 하나로 분류하세요:
1. "yes": 티켓 등록을 원함 (긍정 표현)
   예: 네, yes, 응, ㅇㅇ, 좋아, 그래, 등록해줘, 부탁해, 해주세요, ok, okay, y 등
2. "no": 티켓 등록을 원하지 않음 (부정 표현)
   예: 아니, no, 안해, 취소, 싫어, ㄴㄴ, 괜찮아, 됐어, 필요없어, 그만, n 등
3. "unclear": 의사가 명확하지 않음

JSON 형식으로 응답하세요:
{{
  "decision": "yes/no/unclear",
  "reason": "판단 이유",
  "additional_info": "사용자가 덧붙인 추가 정보 (없으면 null)"
}}"""),
        ("user", f"사용자 응답: {last_user_message}")
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

        evaluation = json.loads(content)
        decision = evaluation.get("decision", "unclear")

        if decision == "yes":
            state["ticket_confirmed"] = True
            state["status"] = "escalated"
            state["ticket_additional_info"] = evaluation.get("additional_info")
        elif decision == "no":
            state["ticket_confirmed"] = False
            state["status"] = "cancelled"
            state["messages"].append(
                AIMessage(content=(
                    "알겠습니다. 문의 등록을 취소했습니다.\n\n"
                    "다른 도움이 필요하시면 언제든 말씀해주세요. 😊"
                ))
            )
        else:  # unclear
            state["ticket_confirmed"] = None
            state["messages"].append(
                AIMessage(content=(
                    "죄송합니다. 명확하게 이해하지 못했습니다.\n\n"
                    "문의를 등록하시려면 '네' 또는 '등록해주세요'라고 답변해주세요.\n"
                    "등록을 원하지 않으시면 '아니요' 또는 '취소'라고 답변해주세요."
                ))
            )

    except (json.JSONDecodeError, Exception) as e:
        # 에러 발생 시 재확인
        print(f"[EvaluateTicketConfirmation] Warning: LLM 평가 실패: {e}")
        state["ticket_confirmed"] = None
        state["messages"].append(
            AIMessage(content=(
                "죄송합니다. 명확하게 이해하지 못했습니다.\n\n"
                "문의를 등록하시려면 '네' 또는 '등록해주세요'라고 답변해주세요.\n"
                "등록을 원하지 않으시면 '아니요' 또는 '취소'라고 답변해주세요."
            ))
        )

    return state
