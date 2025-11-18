"""Streamlit WebUI - 메인 애플리케이션

고객지원 챗봇 웹 인터페이스
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import uuid

from src.graph.workflow import create_workflow


# 페이지 설정
st.set_page_config(
    page_title="고객지원 챗봇",
    page_icon="🤖",
    layout="wide"
)

# 세션 상태 초기화
if "app" not in st.session_state:
    st.session_state.app = create_workflow()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "config" not in st.session_state:
    st.session_state.config = {
        "configurable": {
            "thread_id": st.session_state.session_id
        }
    }

# 워크플로우 상태 저장 (대화 계속을 위해)
if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = {}

# 헤더
st.title("🤖 고객지원 챗봇")
st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    ### 사용 방법
    1. 아래 채팅창에 문제를 입력하세요
    2. AI가 단계별로 해결 방법을 안내합니다
    3. 각 단계의 결과를 알려주세요
    4. 해결되지 않으면 문의를 등록할 수 있습니다

    ### 기능
    - ✅ FAQ 기반 자동 응답
    - ✅ 단계별 문제 해결 가이드
    - ✅ Human-in-the-Loop 대화
    - ✅ 자동 티켓 생성

    ### 세션 정보
    - 세션 ID: `{}`
    """.format(st.session_state.session_id[:8]))

    if st.button("🔄 새 대화 시작"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.config = {
            "configurable": {
                "thread_id": st.session_state.session_id
            }
        }
        st.session_state.debug_info = None
        st.session_state.workflow_state = {}
        st.rerun()

    # 디버그 정보 표시
    st.markdown("---")
    st.header("🔍 디버그 정보")

    if "debug_info" in st.session_state and st.session_state.debug_info:
        debug = st.session_state.debug_info

        if "retrieved_docs" in debug and debug["retrieved_docs"]:
            with st.expander("📚 검색 결과", expanded=False):
                st.write(f"**검색된 문서 수**: {len(debug['retrieved_docs'])}개")
                for i, doc in enumerate(debug["retrieved_docs"][:3], 1):
                    st.markdown(f"""
                    **[{i}] {doc['title']}**
                    - 카테고리: {doc['category']}
                    - 유사도: {doc['score']:.4f}
                    - ID: {doc['id']}
                    """)

        if "solution_steps" in debug and debug["solution_steps"]:
            with st.expander("📝 해결 단계", expanded=False):
                for i, step in enumerate(debug["solution_steps"], 1):
                    st.markdown(f"""
                    **[단계 {i}]** {step.get('action', 'N/A')}
                    - {step.get('description', 'N/A')[:100]}...
                    """)
    else:
        st.info("채팅을 시작하면 디버그 정보가 표시됩니다")

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("🔍 처리 중..."):
            # 상태 준비 - 기존 워크플로우 상태와 병합
            input_state = {
                **st.session_state.workflow_state,  # 기존 상태 유지
                "messages": [
                    HumanMessage(content=msg["content"]) if msg["role"] == "user"
                    else AIMessage(content=msg["content"])
                    for msg in st.session_state.messages
                ],
                "user_id": "user_001"
            }

            # 워크플로우 실행
            try:
                result = None
                debug_info = {}

                for event in st.session_state.app.stream(
                    input_state,
                    st.session_state.config
                ):
                    # 마지막 이벤트 저장
                    result = event

                    # 디버그 정보 수집
                    for node_name, node_output in event.items():
                        if "retrieved_docs" in node_output:
                            debug_info["retrieved_docs"] = node_output["retrieved_docs"]
                        if "solution_steps" in node_output:
                            debug_info["solution_steps"] = node_output["solution_steps"]
                        if "relevance_score" in node_output:
                            debug_info["relevance_score"] = node_output["relevance_score"]

                # 디버그 정보 저장
                st.session_state.debug_info = debug_info

                # 최신 AI 응답 추출 및 상태 저장
                if result:
                    # 결과에서 메시지 추출
                    for node_name, node_output in result.items():
                        # 워크플로우 상태 저장 (다음 대화를 위해)
                        st.session_state.workflow_state = {
                            k: v for k, v in node_output.items()
                            if k not in ["messages"]  # messages는 UI에서 관리
                        }

                        if "messages" in node_output:
                            messages = node_output["messages"]
                            # 마지막 AI 메시지 찾기
                            for msg in reversed(messages):
                                if isinstance(msg, AIMessage):
                                    ai_response = msg.content
                                    st.markdown(ai_response)
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": ai_response
                                    })
                                    break
                            break

            except Exception as e:
                error_msg = f"⚠️ 오류가 발생했습니다: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# 하단 정보
st.markdown("---")
st.caption("🤖 LangGraph 기반 고객지원 챗봇 PoC | Powered by Ollama")
