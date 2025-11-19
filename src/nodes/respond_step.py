"""Respond Step Node - 단계별 응답

현재 단계의 해결 방법을 사용자에게 안내합니다.
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


def respond_step_node(state: SupportState) -> Dict[str, Any]:
    """
    현재 단계의 답변 제공
    - 사용자에게 현재 단계 안내
    - Human-in-the-Loop을 위한 응답 생성

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (messages에 응답 추가)
    """

    current_idx = state["current_step"]
    steps = state["solution_steps"]

    # 첫 응답시 검색 결과 정보 포함
    # 조건: 현재 단계가 0이고, retrieved_docs가 있으면 (새 검색 직후)
    is_first_response = current_idx == 0 and state.get("retrieved_docs") and len(state.get("retrieved_docs", [])) > 0

    # 현재 단계가 없으면 에스컬레이션
    if current_idx >= len(steps):
        state["status"] = "escalated"
        state["unresolved_reason"] = "모든 단계를 시도했으나 해결되지 않음"

        response_text = (
            "😔 불편을 드려 죄송합니다.\n\n"
            "제안드린 모든 해결 방법을 시도하셨지만 문제가 해결되지 않은 것 같습니다.\n"
            "담당 부서의 확인이 필요한 상황입니다.\n\n"
            "💬 **현재까지의 문의 내용으로 문의를 등록하시겠습니까?**\n"
            "(답변: '네, 등록해주세요' 또는 '아니요')"
        )
    else:
        current_step = steps[current_idx]
        step_num = current_step["step"]
        total_steps = len(steps)

        # 첫 응답시 검색 정보 추가
        search_info = ""
        if is_first_response and state.get("retrieved_docs"):
            docs = state["retrieved_docs"]
            search_info = f"🔍 **검색 결과**: {len(docs)}개의 관련 FAQ를 찾았습니다.\n"
            search_info += f"가장 관련성 높은 문서: **{docs[0]['title']}** (카테고리: {docs[0]['category']})\n\n"

        # LLM 초기화
        llm_model = os.getenv("OLLAMA_LLM_MODEL", "gemma2:27b")
        llm = ChatOllama(
            model=llm_model,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.3  # 명확한 지시를 위해 낮은 온도
        )

        # 단계별 응답 프롬프트
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 친절하고 꼼꼼한 기술 지원 AI 상담원입니다.
            
            사용자에게 문제 해결을 위한 다음 단계를 안내하세요.
            
            현재 단계 정보:
            - 단계 번호: {step_num}/{total_steps}
            - 조치: {action}
            - 설명: {description}
            - 기대 결과: {expected_result}
            
            지침:
            1. 사용자에게 이 단계를 수행하도록 정중하게 요청하세요.
            2. 설명 부분을 이해하기 쉽게 풀어서 이야기하세요.
            3. 기대 결과를 언급하며 무엇을 확인해야 하는지 알려주세요.
            4. 이 단계를 시도한 후 결과를 알려달라고(해결되었는지, 안되었는지) 명확히 요청하세요.
            5. 이전 검색 결과가 있다면(search_info) 참고하여 언급하세요.
            
            어조:
            - 격려하고 지지하는 태도
            - 명확하고 이해하기 쉽게
            - "다음과 같이 해보시겠어요?", "확인 부탁드립니다" 등의 정중한 표현 사용
            """),
            ("user", f"검색 정보: {{search_info}}\n\n현재 단계 내용을 바탕으로 사용자에게 안내 메시지를 작성해주세요.")
        ])

        # LLM 호출
        chain = prompt | llm
        response = chain.invoke({
            "step_num": step_num,
            "total_steps": total_steps,
            "action": current_step['action'],
            "description": current_step['description'],
            "expected_result": current_step['expected_result'],
            "search_info": search_info
        })
        response_text = response.content

    # 응답 메시지 추가
    state["messages"].append(AIMessage(content=response_text))
    state["status"] = "waiting_user"

    return state
