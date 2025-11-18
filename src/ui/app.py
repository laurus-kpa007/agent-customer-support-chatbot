"""Streamlit WebUI - 메인 애플리케이션

고객지원 챗봇 웹 인터페이스
"""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import uuid

from ..graph.workflow import create_workflow


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
        st.rerun()

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
        with st.spinner("🔍 검색 중..."):
            # 상태 준비
            input_state = {
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
                for event in st.session_state.app.stream(
                    input_state,
                    st.session_state.config
                ):
                    # 마지막 이벤트 저장
                    result = event

                # 최신 AI 응답 추출
                if result:
                    # 결과에서 메시지 추출
                    for node_name, node_output in result.items():
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
