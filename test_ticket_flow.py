"""티켓 등록 플로우 테스트

티켓 확인 후 "ㅇㅇ" 입력 시 어떤 경로로 가는지 확인
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage, AIMessage
from src.graph.workflow import create_workflow


def test_ticket_confirmation_flow():
    """티켓 확인 플로우 테스트"""

    app = create_workflow()

    print("=" * 80)
    print("  티켓 확인 후 'ㅇㅇ' 입력 테스트")
    print("=" * 80)

    # 시나리오: 문제 → 단계 실패 → 티켓 확인 → "ㅇㅇ"
    conversation = [
        HumanMessage(content="로그인이 안돼요"),
    ]

    # 첫 턴: 문제 입력
    print("\n[턴 1] 사용자: 로그인이 안돼요")
    print("-" * 80)

    state_1 = {
        "messages": conversation.copy(),
        "user_id": "test_user",
        "status": "initialized",
        "current_step": 0,
        "solution_steps": []
    }

    result_1 = None
    nodes_1 = []
    for event in app.stream(state_1):
        result_1 = event
        for node_name in event.keys():
            nodes_1.append(node_name)

    print(f"실행된 노드: {' → '.join(nodes_1)}")

    # 워크플로우 상태 저장
    workflow_state_1 = {k: v for k, v in list(result_1.values())[0].items() if k not in ["messages"]}

    # 턴 2-4: 단계 실패
    for i, user_msg in enumerate(["안돼요", "그것도 안돼요", "다 안돼요"], start=2):
        conversation.append(AIMessage(content=f"[단계 {i-1}/3] ..."))
        conversation.append(HumanMessage(content=user_msg))

        print(f"\n[턴 {i}] 사용자: {user_msg}")
        print("-" * 80)

        state = {
            **workflow_state_1,
            "messages": conversation.copy(),
            "user_id": "test_user"
        }

        result = None
        nodes = []
        for event in app.stream(state):
            result = event
            for node_name in event.keys():
                nodes.append(node_name)

        print(f"실행된 노드: {' → '.join(nodes)}")
        workflow_state_1 = {k: v for k, v in list(result.values())[0].items() if k not in ["messages"]}

        # 마지막 AI 응답
        for msg in reversed(list(result.values())[0]["messages"]):
            if msg.type == "ai":
                print(f"AI 응답 (첫 100자): {msg.content[:100]}...")
                break

    # 턴 5: 티켓 확인 후 "ㅇㅇ"
    conversation.append(AIMessage(content="티켓을 등록하시겠습니까?"))
    conversation.append(HumanMessage(content="ㅇㅇ"))

    print(f"\n[턴 5] 사용자: ㅇㅇ")
    print("-" * 80)

    state_5 = {
        **workflow_state_1,
        "messages": conversation.copy(),
        "user_id": "test_user"
    }

    print(f"현재 상태: status={state_5.get('status')}, current_step={state_5.get('current_step')}")

    result_5 = None
    nodes_5 = []
    for event in app.stream(state_5):
        result_5 = event
        for node_name in event.keys():
            nodes_5.append(node_name)

    print(f"실행된 노드: {' → '.join(nodes_5)}")

    # 결과 분석
    final_state = list(result_5.values())[0]
    print(f"\n최종 상태:")
    print(f"  status: {final_state.get('status')}")
    print(f"  intent: {final_state.get('intent')}")
    print(f"  ticket_confirmed: {final_state.get('ticket_confirmed')}")

    # 마지막 AI 응답
    for msg in reversed(final_state["messages"]):
        if msg.type == "ai":
            print(f"\nAI 응답 (첫 200자):\n{msg.content[:200]}...")
            break

    # 문제 확인
    if "evaluate_ticket_confirmation" in nodes_5:
        print("\n✅ 올바른 경로: evaluate_ticket_confirmation 실행됨")
    elif "classify_intent" in nodes_5 or "search_knowledge" in nodes_5:
        print("\n❌ 잘못된 경로: 의도 분류 또는 검색이 실행됨!")
    else:
        print(f"\n⚠️  예상치 못한 경로: {nodes_5}")


if __name__ == "__main__":
    test_ticket_confirmation_flow()
