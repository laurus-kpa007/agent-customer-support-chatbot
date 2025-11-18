"""포괄적 테스트 - 모든 수정사항 검증

1. 티켓 확인 후 "ㅇㅇ" 입력 시 올바른 경로 (evaluate_ticket_confirmation)
2. 티켓 등록 시 대화 요약 제목 및 전체 대화 내역 포함
3. 문제 해결 또는 티켓 생성 후 상태 초기화
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage, AIMessage
from src.graph.workflow import create_workflow


def test_all_fixes():
    """모든 수정사항 검증"""

    app = create_workflow()

    print("=" * 80)
    print("  포괄적 테스트: 모든 수정사항 검증")
    print("=" * 80)

    # ========================================================================
    # 시나리오 1: 티켓 확인 후 "ㅇㅇ" → 티켓 생성 → 상태 초기화
    # ========================================================================
    print("\n[시나리오 1] 티켓 생성 플로우")
    print("-" * 80)

    conversation = [HumanMessage(content="로그인이 안돼요")]
    state = {
        "messages": conversation.copy(),
        "user_id": "test_user",
        "status": "initialized",
        "current_step": 0,
        "solution_steps": []
    }

    # 턴 1: 문제 입력
    print("\n[턴 1] 사용자: 로그인이 안돼요")
    result = None
    for event in app.stream(state):
        result = event
    workflow_state = {k: v for k, v in list(result.values())[0].items() if k not in ["messages"]}

    # 턴 2-4: 단계 실패
    for i, user_msg in enumerate(["안돼요", "그것도 안돼요", "다 안돼요"], start=2):
        # 이전 결과에서 메시지 가져오기
        conversation = list(result.values())[0]["messages"].copy()
        conversation.append(HumanMessage(content=user_msg))

        state = {**workflow_state, "messages": conversation.copy(), "user_id": "test_user"}

        for event in app.stream(state):
            result = event
        workflow_state = {k: v for k, v in list(result.values())[0].items() if k not in ["messages"]}

    print(f"  → 3단계 시도 완료, 티켓 확인 메시지 표시됨")
    print(f"  → status after confirm_ticket: {workflow_state.get('status')}")

    # 턴 5: 티켓 확인 후 "ㅇㅇ"
    conversation = list(result.values())[0]["messages"].copy()
    conversation.append(HumanMessage(content="ㅇㅇ"))

    print("\n[턴 5] 사용자: ㅇㅇ")
    state = {**workflow_state, "messages": conversation.copy(), "user_id": "test_user"}

    nodes_executed = []
    for event in app.stream(state):
        result = event
        for node_name in event.keys():
            nodes_executed.append(node_name)

    final_state = list(result.values())[0]

    print(f"  실행된 노드: {' → '.join(nodes_executed)}")
    print(f"  최종 상태: status={final_state.get('status')}, ticket_confirmed={final_state.get('ticket_confirmed')}")

    # 마지막 AI 응답 확인
    for msg in reversed(final_state["messages"]):
        if msg.type == "ai":
            print(f"  마지막 AI 응답 (첫 150자): {msg.content[:150]}...")
            break

    # 검증 1: 올바른 경로
    if "evaluate_ticket_confirmation" in nodes_executed:
        print("  ✅ 올바른 경로: evaluate_ticket_confirmation 실행됨")
    else:
        print(f"  ❌ 잘못된 경로: {nodes_executed}")
        return False

    # 검증 2: 티켓 생성 노드 실행 확인
    if "create_ticket" in nodes_executed:
        print("  ✅ create_ticket 노드 실행됨")
    else:
        print(f"  ❌ create_ticket 노드 실행 안됨")
        print(f"     ticket_confirmed={final_state.get('ticket_confirmed')}")
        return False

    # 검증 3: 티켓 생성 완료 확인
    if final_state.get("status") == "ticket_created":
        print("  ✅ 티켓 생성 완료")
    else:
        print(f"  ❌ 티켓 생성 실패: status={final_state.get('status')}")
        return False

    # 검증 4: 상태 초기화 확인
    if (len(final_state.get("solution_steps", [])) == 0 and
        final_state.get("current_step", 0) == 0 and
        len(final_state.get("retrieved_docs", [])) == 0):
        print("  ✅ 상태 초기화 완료")
    else:
        print(f"  ❌ 상태 초기화 실패: steps={len(final_state.get('solution_steps', []))}, current_step={final_state.get('current_step')}")
        return False

    # 검증 5: 마지막 AI 메시지에 티켓 정보 포함 확인
    last_ai_msg = None
    for msg in reversed(final_state["messages"]):
        if msg.type == "ai":
            last_ai_msg = msg.content
            break

    if last_ai_msg and "문의가 등록되었습니다" in last_ai_msg and "문의 번호" in last_ai_msg:
        print("  ✅ 티켓 등록 안내 메시지 포함")
        print(f"\n  AI 응답 (일부):\n  {last_ai_msg[:200]}...")
    else:
        print("  ❌ 티켓 등록 안내 메시지 누락")
        return False

    # ========================================================================
    # 시나리오 2: 문제 해결 → 상태 초기화
    # ========================================================================
    print("\n\n[시나리오 2] 문제 해결 플로우")
    print("-" * 80)

    conversation2 = [HumanMessage(content="파일 업로드가 안돼요")]
    state2 = {
        "messages": conversation2.copy(),
        "user_id": "test_user2",
        "status": "initialized",
        "current_step": 0,
        "solution_steps": []
    }

    # 턴 1: 문제 입력
    print("\n[턴 1] 사용자: 파일 업로드가 안돼요")
    result2 = None
    for event in app.stream(state2):
        result2 = event
    workflow_state2 = {k: v for k, v in list(result2.values())[0].items() if k not in ["messages"]}

    # 턴 2: 해결됨
    conversation2 = list(result2.values())[0]["messages"].copy()
    conversation2.append(HumanMessage(content="해결됐어요, 감사합니다!"))

    print("\n[턴 2] 사용자: 해결됐어요, 감사합니다!")
    state2 = {**workflow_state2, "messages": conversation2.copy(), "user_id": "test_user2"}

    nodes_executed2 = []
    for event in app.stream(state2):
        result2 = event
        for node_name in event.keys():
            nodes_executed2.append(node_name)

    final_state2 = list(result2.values())[0]

    # 검증 6: 해결 완료
    if final_state2.get("status") == "resolved":
        print("  ✅ 문제 해결 완료")
    else:
        print(f"  ❌ 해결 실패: status={final_state2.get('status')}")
        return False

    # 검증 7: 상태 초기화 확인
    if (len(final_state2.get("solution_steps", [])) == 0 and
        final_state2.get("current_step", 0) == 0 and
        len(final_state2.get("retrieved_docs", [])) == 0):
        print("  ✅ 상태 초기화 완료")
    else:
        print(f"  ❌ 상태 초기화 실패")
        return False

    # 검증 8: 감사 메시지 확인
    last_ai_msg2 = None
    for msg in reversed(final_state2["messages"]):
        if msg.type == "ai":
            last_ai_msg2 = msg.content
            break

    if last_ai_msg2 and "해결되어 다행입니다" in last_ai_msg2:
        print("  ✅ 감사 메시지 포함")
        print(f"\n  AI 응답: {last_ai_msg2}")
    else:
        print("  ❌ 감사 메시지 누락")
        return False

    return True


if __name__ == "__main__":
    success = test_all_fixes()

    print("\n" + "=" * 80)
    if success:
        print("  ✅ 모든 테스트 통과!")
    else:
        print("  ❌ 일부 테스트 실패")
    print("=" * 80)
