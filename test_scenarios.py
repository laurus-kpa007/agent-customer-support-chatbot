#!/usr/bin/env python3
"""다양한 시나리오 테스트 - 스몰톡, 티켓 등록 등"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage, AIMessage
from src.graph.workflow import create_workflow

def test_scenario(name, turns):
    """시나리오 테스트"""
    print("\n" + "=" * 80)
    print(f"  시나리오: {name}")
    print("=" * 80)

    app = create_workflow()
    conversation = []
    workflow_state = {}

    for turn_num, user_input in enumerate(turns, 1):
        print(f"\n[턴 {turn_num}] 사용자: {user_input}")
        print("-" * 80)

        # 사용자 메시지 추가
        user_msg = HumanMessage(content=user_input)
        conversation.append(user_msg)

        # 상태 준비
        input_state = {
            **workflow_state,
            "messages": conversation,
            "user_id": "test_user"
        }

        # 워크플로우 실행
        result = None
        nodes_executed = []

        for event in app.stream(input_state):
            result = event
            for node_name, _ in event.items():
                nodes_executed.append(node_name)

        print(f"실행된 노드: {' → '.join(nodes_executed)}")

        # 결과 확인
        if result:
            for node_name, output in result.items():
                # 상태 저장
                workflow_state = {k: v for k, v in output.items() if k not in ["messages"]}

                # AI 응답 출력
                if output.get("messages"):
                    ai_msgs = [m for m in output["messages"] if isinstance(m, AIMessage)]
                    if ai_msgs:
                        last_ai = ai_msgs[-1]
                        conversation.append(last_ai)
                        print(f"\nAI 응답:")
                        print(last_ai.content[:300] + ("..." if len(last_ai.content) > 300 else ""))

                # 상태 정보
                print(f"\n상태: {output.get('status', 'N/A')}")
                if output.get("current_step") is not None:
                    print(f"현재 단계: {output.get('current_step')}/{len(output.get('solution_steps', []))}")
                if output.get("ticket_id"):
                    print(f"티켓 ID: {output.get('ticket_id')}")

    print("\n" + "=" * 80)
    print(f"시나리오 '{name}' 완료")
    print("=" * 80)


def main():
    """모든 시나리오 테스트"""

    # 시나리오 1: 스몰톡
    test_scenario("스몰톡", [
        "안녕하세요"
    ])

    # 시나리오 2: 스몰톡 후 문의
    test_scenario("스몰톡 후 문의", [
        "안녕",
        "메시지가 안 보내져요"
    ])

    # 시나리오 3: 정상 해결
    test_scenario("정상 해결", [
        "파일 업로드가 안돼요",
        "확인했어요, 됐어요!"
    ])

    # 시나리오 4: 모든 단계 실패 후 티켓
    test_scenario("티켓 등록", [
        "로그인이 안돼요",
        "안돼요",
        "그것도 안돼요",
        "다 안돼요"
    ])

    # 시나리오 5: 명시적 티켓 요청
    test_scenario("명시적 티켓 요청", [
        "비밀번호를 모르겠어요",
        "등록해주세요"
    ])


if __name__ == "__main__":
    main()
