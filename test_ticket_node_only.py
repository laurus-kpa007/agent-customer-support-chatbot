"""티켓 확인 노드만 직접 테스트

evaluate_ticket_confirmation_node만 직접 호출하여 LLM 판단 테스트
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage, AIMessage
from src.nodes.evaluate_ticket_confirmation import evaluate_ticket_confirmation_node


def test_node_directly():
    """노드만 직접 테스트"""

    # 테스트 케이스
    test_cases = [
        ("네", "긍정"),
        ("ㅇㅇ", "긍정"),
        ("그래", "긍정"),
        ("아니요", "부정"),
        ("ㄴㄴ", "부정"),
    ]

    print("=" * 80)
    print("  evaluate_ticket_confirmation_node 직접 테스트")
    print("=" * 80)

    for response, expected in test_cases:
        # 상태 설정
        state = {
            "messages": [
                HumanMessage(content="로그인이 안돼요"),
                AIMessage(content="티켓을 등록하시겠습니까?"),
                HumanMessage(content=response)
            ],
            "user_id": "test_user",
            "status": "evaluating_ticket",
            "current_query": "로그인이 안돼요",
            "current_step": 0,
            "solution_steps": []
        }

        print(f"\n테스트: '{response}' (예상: {expected})")

        # 노드 실행
        result = evaluate_ticket_confirmation_node(state)

        ticket_confirmed = result.get("ticket_confirmed")
        status = result.get("status")

        if expected == "긍정":
            if ticket_confirmed is True and status == "escalated":
                print(f"  ✅ 긍정으로 정확히 인식")
            elif ticket_confirmed is False:
                print(f"  ❌ 부정으로 잘못 인식됨! (status={status})")
            else:
                print(f"  ⚠️  명확하지 않음으로 인식됨 (status={status})")
        else:  # 부정
            if ticket_confirmed is False and status == "cancelled":
                print(f"  ✅ 부정으로 정확히 인식")
            elif ticket_confirmed is True:
                print(f"  ❌ 긍정으로 잘못 인식됨! (status={status})")
            else:
                print(f"  ⚠️  명확하지 않음으로 인식됨 (status={status})")


if __name__ == "__main__":
    test_node_directly()
