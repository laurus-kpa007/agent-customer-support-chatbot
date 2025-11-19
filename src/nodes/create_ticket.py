"""Create Ticket Node - 티켓 생성

대화 내용을 요약하여 Q&A 게시판에 티켓을 생성합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
import json
from datetime import datetime
import uuid
from typing import Dict, Any

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from dotenv import load_dotenv

from src.models.state import SupportState
from src.utils.state_reset import reset_conversation_state

# 환경 변수 로드
load_dotenv()


def create_ticket_node(state: SupportState) -> Dict[str, Any]:
    """
    티켓 생성 노드
    - 대화 내용 요약
    - Q&A 게시판에 등록 (PoC: JSON 파일 저장)

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태 (ticket_id 추가)
    """

    # LLM 초기화
    llm_model = os.getenv("OLLAMA_LLM_MODEL", "gemma2:27b")
    llm = ChatOllama(
        model=llm_model,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0
    )

    # 대화 내용 포맷팅
    conversation = "\n".join([
        f"{'사용자' if msg.type == 'human' else 'Agent'}: {msg.content}"
        for msg in state["messages"]
    ])

    # 요약 생성
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", """대화 내용을 요약하여 Q&A 게시판 제목과 본문을 작성하세요.

JSON 형식으로 응답:
{{
  "title": "간결한 제목 (30자 이내)",
  "summary": "문제 상황 요약 (200자 이내)",
  "attempted_solutions": ["시도한 해결방법 1", "시도한 해결방법 2"]
}}

JSON만 출력하세요."""),
        ("user", "대화 내용:\n{conversation}")
    ])

    try:
        response = llm.invoke(
            summary_prompt.format_messages(conversation=conversation)
        )

        # JSON 파싱
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        summary = json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: 요약 생성 실패, 기본 요약 사용: {e}")
        summary = {
            "title": "고객 문의",
            "summary": state["current_query"],
            "attempted_solutions": []
        }

    # 티켓 생성
    ticket_id = str(uuid.uuid4())[:8]
    ticket = {
        "ticket_id": ticket_id,
        "user_id": state.get("user_id", "anonymous"),
        "session_id": state["session_id"],
        "title": summary.get("title", "고객 문의"),
        "summary": summary.get("summary", state["current_query"]),
        "additional_info": state.get("ticket_additional_info"),
        "attempted_solutions": summary.get("attempted_solutions", []),
        "conversation_history": [
            {
                "role": msg.type,
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            }
            for msg in state["messages"]
        ],
        "category": state["retrieved_docs"][0]["category"] if state.get("retrieved_docs") else "기타",
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "answered_at": None,
        "answer": None
    }

    # 티켓 디렉토리 생성
    tickets_path = os.getenv("TICKETS_PATH", "data/tickets")
    os.makedirs(tickets_path, exist_ok=True)

    # 파일로 저장 (PoC)
    ticket_file = os.path.join(tickets_path, f"ticket_{ticket_id}.json")
    with open(ticket_file, "w", encoding="utf-8") as f:
        json.dump(ticket, f, ensure_ascii=False, indent=2)

    state["ticket_id"] = ticket_id
    state["status"] = "ticket_created"

    # 사용자에게 안내
    response_text = f"""📋 **문의가 등록되었습니다**

**문의 번호**: `{ticket_id}`
**제목**: {ticket['title']}
**요약**: {ticket['summary']}

담당자가 확인 후 답변을 드리겠습니다.
답변이 등록되면 알림을 보내드리겠습니다. 📬

감사합니다! 😊"""

    state["messages"].append(AIMessage(content=response_text))

    # 대화 상태 초기화는 send_notification_node에서 수행
    # state = reset_conversation_state(state)

    return state
