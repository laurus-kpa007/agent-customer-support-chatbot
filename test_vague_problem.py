"""
Test Scenario: Vague Problem → Symptom Clarification → Search Flow
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.graph.workflow import create_workflow
from src.models.state import SupportState


def test_vague_problem_flow():
    """
    시나리오: 모호한 문제 진술 → 증상 질문 → 구체적 답변 → 검색 → 해결
    """

    print("=" * 80)
    print("시나리오: 모호한 문제 처리 (메신저가 이상해)")
    print("=" * 80)

    # 워크플로우 생성
    app = create_workflow()

    # 초기 상태
    state = SupportState(
        messages=[],
        current_query="",
        retrieved_docs=[],
        relevance_score=0.0,
        solution_steps=[],
        current_step=0,
        max_steps=3,
        status="initialized",
        attempts=0,
        unresolved_reason=None,
        ticket_id=None,
        ticket_confirmed=None,
        ticket_additional_info=None,
        intent=None,
        intent_confidence=None,
        needs_clarification=None,
        user_id="test_user_vague",
        session_id="",
        started_at="",
        debug_info=None
    )

    # === 턴 1: 모호한 문제 진술 ===
    print("\n" + "=" * 80)
    print("턴 1: 사용자가 모호한 문제를 제기")
    print("=" * 80)
    print("\n👤 사용자: 메신저가 이상해")

    from langchain_core.messages import HumanMessage
    state["messages"].append(HumanMessage(content="메신저가 이상해"))

    result = app.invoke(state)

    print(f"\n🤖 시스템 상태: {result.get('status')}")
    print(f"🤖 의도 분류: {result.get('intent')}")
    print(f"🤖 명확화 필요: {result.get('needs_clarification')}")

    # AI 응답 확인
    last_ai_message = None
    for msg in reversed(result["messages"]):
        if msg.type == "ai":
            last_ai_message = msg.content
            break

    if last_ai_message:
        print(f"\n🤖 챗봇: {last_ai_message}")

    # 증상 질문을 받았는지 확인
    if result.get("needs_clarification") or "증상" in last_ai_message:
        print("\n✅ 증상 명확화 질문을 올바르게 생성했습니다")
    else:
        print("\n❌ 증상 질문이 없습니다 - 문제!")
        return

    # === 턴 2: 구체적인 증상 제공 ===
    print("\n" + "=" * 80)
    print("턴 2: 사용자가 구체적인 증상 제공")
    print("=" * 80)
    print("\n👤 사용자: 메시지를 보내려고 하면 '전송 실패' 오류가 나요")

    result["messages"].append(HumanMessage(content="메시지를 보내려고 하면 '전송 실패' 오류가 나요"))

    result = app.invoke(result)

    print(f"\n🤖 시스템 상태: {result.get('status')}")
    print(f"🤖 현재 쿼리: {result.get('current_query')}")
    print(f"🤖 검색 결과 수: {len(result.get('retrieved_docs', []))}")

    # AI 응답 확인
    last_ai_message = None
    for msg in reversed(result["messages"]):
        if msg.type == "ai":
            last_ai_message = msg.content
            break

    if last_ai_message:
        print(f"\n🤖 챗봇: {last_ai_message[:200]}...")

    # 검색이 수행되었는지 확인
    if result.get("retrieved_docs") and len(result.get("retrieved_docs", [])) > 0:
        print("\n✅ 구체적인 증상으로 검색을 올바르게 수행했습니다")
        print(f"   - 검색된 문서 수: {len(result['retrieved_docs'])}")
        print(f"   - 해결 단계 수: {len(result.get('solution_steps', []))}")
    else:
        print("\n⚠️ 검색 결과가 없습니다")

    # === 턴 3: 단계 수행 ===
    print("\n" + "=" * 80)
    print("턴 3: 첫 번째 단계 수행")
    print("=" * 80)
    print("\n👤 사용자: 네트워크 설정 확인했어요")

    result["messages"].append(HumanMessage(content="네트워크 설정 확인했어요"))

    result = app.invoke(result)

    print(f"\n🤖 시스템 상태: {result.get('status')}")
    print(f"🤖 현재 단계: {result.get('current_step')}")

    # AI 응답 확인
    last_ai_message = None
    for msg in reversed(result["messages"]):
        if msg.type == "ai":
            last_ai_message = msg.content
            break

    if last_ai_message:
        print(f"\n🤖 챗봇: {last_ai_message[:200]}...")

    # "했어요"가 올바르게 처리되었는지 확인 (continue로 처리되어야 함)
    if result.get("status") == "waiting_user" and result.get("current_step") > 0:
        print("\n✅ '했어요' 표현을 올바르게 처리했습니다 (다음 단계 제시)")
    elif result.get("status") == "resolved":
        print("\n❌ '했어요'를 해결로 잘못 인식했습니다!")

    # === 턴 4: 해결 확인 ===
    print("\n" + "=" * 80)
    print("턴 4: 문제 해결")
    print("=" * 80)
    print("\n👤 사용자: 이제 메시지 전송이 잘 돼요!")

    result["messages"].append(HumanMessage(content="이제 메시지 전송이 잘 돼요!"))

    result = app.invoke(result)

    print(f"\n🤖 시스템 상태: {result.get('status')}")

    # AI 응답 확인
    last_ai_message = None
    for msg in reversed(result["messages"]):
        if msg.type == "ai":
            last_ai_message = msg.content
            break

    if last_ai_message:
        print(f"\n🤖 챗봇: {last_ai_message}")

    if result.get("status") == "resolved":
        print("\n✅ 문제 해결을 올바르게 인식했습니다")
    else:
        print(f"\n❌ 해결 상태가 아닙니다: {result.get('status')}")

    print("\n" + "=" * 80)
    print("시나리오 완료")
    print("=" * 80)


if __name__ == "__main__":
    test_vague_problem_flow()
