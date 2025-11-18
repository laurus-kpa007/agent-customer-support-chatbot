"""Confirm Ticket Node - 티켓 생성 확인

티켓을 생성하기 전에 사용자에게 확인을 요청합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
import json
from typing import Dict, Any
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from src.models.state import SupportState


def confirm_ticket_node(state: SupportState) -> Dict[str, Any]:
    """
    티켓 생성 확인 노드
    - 현재까지의 대화 내용 요약 (LLM 사용)
    - 티켓 등록 의사 확인

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (messages에 확인 요청 추가)
    """

    # LLM 초기화
    llm_model = os.getenv("OLLAMA_LLM_MODEL", "gemma2:27b")
    llm = ChatOllama(
        model=llm_model,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0
    )

    # 대화 내용 포맷팅
    conversation_history = []
    for msg in state["messages"]:
        role = "사용자" if msg.type == "human" else "상담원"
        conversation_history.append(f"{role}: {msg.content[:100]}..." if len(msg.content) > 100 else f"{role}: {msg.content}")

    conversation_text = "\n".join(conversation_history)

    # 대화 요약 생성 (LLM)
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", """대화 내용을 요약하여 간결한 제목을 생성하세요.

JSON 형식으로 응답:
{{
  "title": "간결한 제목 (30자 이내, 주요 문제만)",
  "main_issue": "핵심 문제 설명 (50자 이내)"
}}

JSON만 출력하세요."""),
        ("user", "대화 내용:\n{conversation}")
    ])

    try:
        # 전체 대화 내용
        full_conversation = "\n".join([
            f"{'사용자' if msg.type == 'human' else '상담원'}: {msg.content}"
            for msg in state["messages"]
        ])

        response = llm.invoke(
            summary_prompt.format_messages(conversation=full_conversation)
        )

        # JSON 파싱
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        summary = json.loads(content)
        title = summary.get("title", "고객 문의")
        main_issue = summary.get("main_issue", state.get("current_query", "문의 내용"))
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: 요약 생성 실패, 기본 요약 사용: {e}")
        title = "고객 문의"
        main_issue = state.get("current_query", "문의 내용")

    # 확인 메시지 생성
    attempted_steps = state.get("current_step", 0)

    response_text = "😔 불편을 드려 죄송합니다.\n\n"

    if attempted_steps > 0:
        response_text += f"지금까지 {attempted_steps}단계를 시도하셨지만 문제가 해결되지 않은 것 같습니다.\n"

    response_text += (
        "담당 부서의 확인이 필요한 상황입니다.\n\n"
        "📋 **등록될 문의 내용:**\n\n"
        f"**제목**: {title}\n"
        f"**핵심 문제**: {main_issue}\n\n"
        "**대화 내역** (최근 5개 메시지):\n"
        f"```\n{conversation_text[-5:]}\n```\n\n"
        "💬 **이 내용으로 문의를 등록하시겠습니까?**\n\n"
        "답변해주세요:\n"
        "- '네' 또는 '등록해주세요' → 문의 등록\n"
        "- '아니요' 또는 '취소' → 문의 등록 취소"
    )

    # 응답 메시지 추가
    state["messages"].append(AIMessage(content=response_text))
    state["status"] = "confirming_ticket"

    return state
