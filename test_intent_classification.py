"""의도 분류 테스트

LLM 기반 의도 분류가 올바르게 작동하는지 테스트합니다.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage
from src.nodes.classify_intent import classify_intent_node


def test_intent_classification():
    """다양한 입력에 대한 의도 분류 테스트"""

    test_cases = [
        # (입력, 예상 intent, 설명)
        ("안녕하세요", "small_talk", "단순 인사"),
        ("Hello", "small_talk", "영어 인사"),
        ("반갑습니다", "small_talk", "격식있는 인사"),
        ("좋은 아침이에요", "small_talk", "시간 인사"),
        ("감사합니다", "small_talk", "감사 인사"),

        ("로그인이 안돼요", "technical_support", "로그인 문제"),
        ("파일 업로드가 실패합니다", "technical_support", "파일 업로드 문제"),
        ("비밀번호를 잊어버렸어요", "technical_support", "비밀번호 분실"),
        ("메시지가 안 보내져요", "technical_support", "메시지 전송 문제"),
        ("계정을 삭제하고 싶어요", "technical_support", "계정 관리"),

        ("안녕하세요, 로그인이 안되는데 도와주세요", "technical_support", "인사 + 기술 문의"),
        ("Hello, I can't upload files", "technical_support", "영어 인사 + 기술 문의"),
    ]

    print("=" * 80)
    print("  LLM 기반 의도 분류 테스트")
    print("=" * 80)

    correct = 0
    total = len(test_cases)

    for user_input, expected_intent, description in test_cases:
        # 상태 설정
        state = {
            "messages": [HumanMessage(content=user_input)],
            "user_id": "test_user",
            "status": "initialized",
            "solution_steps": [],
            "current_step": 0
        }

        # 노드 실행
        result = classify_intent_node(state)

        intent = result.get("intent", "unknown")
        confidence = result.get("intent_confidence", 0.0)

        is_correct = intent == expected_intent
        if is_correct:
            correct += 1

        status_icon = "✅" if is_correct else "❌"
        print(f"\n{status_icon} {description}")
        print(f"   입력: \"{user_input}\"")
        print(f"   예상: {expected_intent}")
        print(f"   실제: {intent} (신뢰도: {confidence:.2f})")

        if not is_correct:
            debug_info = result.get("debug_info", {}).get("intent_classification", {})
            reason = debug_info.get("reason", "")
            if reason:
                print(f"   이유: {reason}")

    print("\n" + "=" * 80)
    print(f"  정확도: {correct}/{total} = {100*correct/total:.1f}%")
    print("=" * 80)

    return correct == total


if __name__ == "__main__":
    all_pass = test_intent_classification()
    if all_pass:
        print("\n✅ 모든 테스트 통과!")
    else:
        print("\n⚠️  일부 테스트 실패")
