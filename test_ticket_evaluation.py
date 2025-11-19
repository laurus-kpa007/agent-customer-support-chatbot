"""티켓 확인 평가 테스트 - LLM이 "ㅇㅇ"을 인식하는지 확인"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage
from src.nodes.evaluate_ticket_confirmation import evaluate_ticket_confirmation_node


def test_ticket_evaluation():
    """LLM이 다양한 긍정/부정 표현을 인식하는지 테스트"""

    test_cases = [
        ("ㅇㅇ", True),
        ("네", True),
        ("yes", True),
        ("등록해주세요", True),
        ("응", True),
        ("그래", True),
        ("아니", False),
        ("ㄴㄴ", False),
        ("no", False),
        ("취소", False),
    ]

    print("=" * 80)
    print("  티켓 확인 평가 테스트")
    print("=" * 80)

    for user_input, expected in test_cases:
        state = {
            "messages": [HumanMessage(content=user_input)],
            "user_id": "test_user",
            "status": "evaluating_ticket"
        }

        result = evaluate_ticket_confirmation_node(state)
        ticket_confirmed = result.get("ticket_confirmed")

        if ticket_confirmed == expected:
            print(f"✅ '{user_input}' → {ticket_confirmed} (예상: {expected})")
        else:
            print(f"❌ '{user_input}' → {ticket_confirmed} (예상: {expected})")


if __name__ == "__main__":
    test_ticket_evaluation()
