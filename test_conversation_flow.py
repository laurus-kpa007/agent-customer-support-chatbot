#!/usr/bin/env python3
"""대화 흐름 테스트 - 멀티턴 대화"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage, AIMessage
from src.graph.workflow import create_workflow

def test_multi_turn_conversation():
    """멀티턴 대화 테스트"""

    print("=" * 70)
    print("  멀티턴 대화 흐름 테스트")
    print("=" * 70)

    # 워크플로우 생성
    print("\n워크플로우 생성 중...")
    app = create_workflow()
    print("✅ 완료\n")

    # 시나리오: 메시지가 안 보내져 → 확인했음 → 안됨 → 티켓 등록
    print("=" * 70)
    print("시나리오: 문제 해결 시도 → 실패 → 티켓 등록")
    print("=" * 70)

    # 대화 시작
    conversation = []
    workflow_state = {}

    # 턴 1: 사용자가 문제 제기
    print("\n[턴 1] 사용자: 메시지가 안 보내져요")
    print("-" * 70)

    user_message_1 = HumanMessage(content="메시지가 안 보내져요")
    conversation.append(user_message_1)

    input_state_1 = {
        **workflow_state,
        "messages": conversation,
        "user_id": "test_user"
    }

    result_1 = None
    for event in app.stream(input_state_1):
        result_1 = event

    # 결과 확인
    for node_name, output in result_1.items():
        print(f"노드: {node_name}")
        print(f"상태: {output.get('status', 'N/A')}")

        if output.get("is_continuing"):
            print("⚠️  대화 계속 모드")
        else:
            print("✅ 새 대화 모드")

        if output.get("retrieved_docs"):
            print(f"검색 결과: {len(output['retrieved_docs'])}개")
            print(f"  - {output['retrieved_docs'][0]['title']}")

        if output.get("solution_steps"):
            print(f"해결 단계: {len(output['solution_steps'])}개")

        if output.get("messages"):
            ai_msg = [m for m in output["messages"] if isinstance(m, AIMessage)][-1]
            conversation.append(ai_msg)
            print(f"\nAI 응답:")
            print(ai_msg.content[:200] + "...")

        # 상태 저장
        workflow_state = {k: v for k, v in output.items() if k not in ["messages"]}

    # 턴 2: 사용자가 "확인했음" 응답
    print("\n\n[턴 2] 사용자: 확인했는데 안돼요")
    print("-" * 70)

    user_message_2 = HumanMessage(content="확인했는데 안돼요")
    conversation.append(user_message_2)

    input_state_2 = {
        **workflow_state,
        "messages": conversation,
        "user_id": "test_user"
    }

    result_2 = None
    for event in app.stream(input_state_2):
        result_2 = event
        # 모든 이벤트 출력
        for node_name, _ in event.items():
            print(f"  → {node_name} 실행")

    # 결과 확인
    print("\n최종 결과:")
    for node_name, output in result_2.items():
        print(f"노드: {node_name}")
        print(f"상태: {output.get('status', 'N/A')}")

        if output.get("is_continuing"):
            print("✅ 대화 계속 모드 (검색 건너뜀)")
        else:
            print("⚠️  새 대화로 인식 (잘못됨!)")

        if output.get("current_step") is not None:
            print(f"현재 단계: {output['current_step']}")

        if output.get("messages"):
            ai_msg = [m for m in output["messages"] if isinstance(m, AIMessage)][-1]
            conversation.append(ai_msg)
            print(f"\nAI 응답:")
            print(ai_msg.content[:200] + "...")

        # 상태 저장
        workflow_state = {k: v for k, v in output.items() if k not in ["messages"]}

    # 턴 3: 사용자가 "그것도 안돼요"
    print("\n\n[턴 3] 사용자: 그것도 안돼요")
    print("-" * 70)

    user_message_3 = HumanMessage(content="그것도 안돼요")
    conversation.append(user_message_3)

    input_state_3 = {
        **workflow_state,
        "messages": conversation,
        "user_id": "test_user"
    }

    result_3 = None
    for event in app.stream(input_state_3):
        result_3 = event

    # 결과 확인
    for node_name, output in result_3.items():
        print(f"노드: {node_name}")
        print(f"상태: {output.get('status', 'N/A')}")

        if output.get("is_continuing"):
            print("✅ 대화 계속 모드")

        if output.get("current_step") is not None:
            print(f"현재 단계: {output['current_step']}")

        if output.get("messages"):
            ai_msg = [m for m in output["messages"] if isinstance(m, AIMessage)][-1]
            conversation.append(ai_msg)
            print(f"\nAI 응답:")
            print(ai_msg.content[:300] + "...")

        # 상태 저장
        workflow_state = {k: v for k, v in output.items() if k not in ["messages"]}

    print("\n" + "=" * 70)
    print("테스트 완료")
    print(f"총 대화 턴: {len([m for m in conversation if isinstance(m, HumanMessage)])}개")
    print("=" * 70)

if __name__ == "__main__":
    test_multi_turn_conversation()
