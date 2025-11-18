"""Plan Response Node - 답변 계획

검색된 FAQ를 바탕으로 단계별 해결 방법을 생성합니다.
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
from dotenv import load_dotenv

from src.models.state import SupportState

# 환경 변수 로드
load_dotenv()


def plan_response_node(state: SupportState) -> Dict[str, Any]:
    """
    답변 계획 노드
    - 검색된 문서를 바탕으로 단계별 해결 방법 생성
    - LLM을 활용한 계획 수립

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (solution_steps 포함)
    """

    # LLM 초기화
    llm_model = os.getenv("OLLAMA_LLM_MODEL", "gemma2:27b")
    llm = ChatOllama(
        model=llm_model,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0
    )

    # 검색된 문서가 없는 경우
    if not state["retrieved_docs"]:
        state["solution_steps"] = [{
            "step": 1,
            "action": "관련 정보 없음",
            "description": "죄송합니다. 해당 질문과 관련된 FAQ를 찾을 수 없습니다.",
            "expected_result": "고객센터에 문의해주세요.",
            "completed": False
        }]
        state["current_step"] = 0
        state["status"] = "responding"
        return state

    # 검색된 문서들 포맷팅
    docs_context = "\n\n".join([
        f"[문서 {i+1}] (관련도: {doc['score']:.3f})\n"
        f"제목: {doc['title']}\n"
        f"카테고리: {doc['category']}\n"
        f"내용:\n{doc['content'][:500]}..."  # 처음 500자만
        for i, doc in enumerate(state["retrieved_docs"])
    ])

    # 프롬프트 생성
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 고객지원 전문가입니다.
사용자의 문제를 해결하기 위한 단계별 가이드를 작성하세요.

검색된 관련 문서:
{docs_context}

다음 JSON 형식으로 응답하세요:
{{
  "steps": [
    {{
      "step": 1,
      "action": "확인할 항목 또는 수행할 작업",
      "description": "상세 설명 (한국어로 친절하게)",
      "expected_result": "기대되는 결과"
    }}
  ]
}}

규칙:
- 최대 3단계까지만 작성
- 각 단계는 명확하고 실행 가능해야 함
- 간단한 것부터 복잡한 순서로 배치
- 한국어로 작성
- JSON 형식만 출력 (다른 설명 없이)"""),
        ("user", "사용자 문제: {query}")
    ])

    # LLM 호출
    try:
        response = llm.invoke(
            prompt.format_messages(
                docs_context=docs_context,
                query=state["current_query"]
            )
        )

        # JSON 파싱
        content = response.content.strip()

        # JSON 코드 블록 제거 (```json ... ``` 형태인 경우)
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        plan = json.loads(content)
        steps = plan.get("steps", [])

        # 각 단계에 완료 여부 추가
        for step in steps:
            step["completed"] = False

        state["solution_steps"] = steps

    except (json.JSONDecodeError, Exception) as e:
        # 파싱 실패시 검색된 문서의 첫 번째 항목을 기본 단계로 사용
        print(f"Warning: LLM 응답 파싱 실패: {e}")

        first_doc = state["retrieved_docs"][0]
        state["solution_steps"] = [{
            "step": 1,
            "action": first_doc["title"],
            "description": first_doc["content"][:200] + "...",
            "expected_result": "문제가 해결되어야 합니다",
            "completed": False
        }]

    state["current_step"] = 0
    state["status"] = "responding"

    return state
