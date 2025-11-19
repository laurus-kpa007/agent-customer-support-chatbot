"""자연스러운 대화 흐름 테스트

실제 인간-상담원 대화처럼 자연스러운 시나리오 테스트:
1. 스몰톡으로 시작
2. 기술 문제로 전환
3. 단계별 해결 시도
4. 중간에 예외 상황 (오해, 잘못된 응답 등)
5. 최종 해결 또는 티켓 생성
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langchain_core.messages import HumanMessage, AIMessage
from src.graph.workflow import create_workflow


def print_divider(title=""):
    """구분선 출력"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"\n{'-'*60}\n")


def print_state_info(state, step_name):
    """상태 정보 출력"""
    print(f"\n[{step_name}]")
    print(f"  Status: {state.get('status')}")
    print(f"  Current Step: {state.get('current_step', 0)}/{len(state.get('solution_steps', []))}")
    print(f"  Intent: {state.get('intent')}")
    print(f"  Retrieved Docs: {len(state.get('retrieved_docs', []))}개")

    # 마지막 AI 응답
    messages = state.get('messages', [])
    if messages:
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                print(f"\n  AI 응답:\n    {msg.content[:200]}{'...' if len(msg.content) > 200 else ''}")
                break


def test_scenario_1_natural_flow():
    """
    시나리오 1: 자연스러운 전체 흐름
    - 인사로 시작 (스몰톡)
    - 문제 상담 시작
    - 단계별 해결 시도
    - 중간에 모호한 답변 (예외 상황)
    - 최종 해결
    """
    print_divider("시나리오 1: 자연스러운 전체 대화 흐름")

    app = create_workflow()
    state = {"messages": [], "user_id": "test_user_001"}

    # 1. 인사 (스몰톡)
    print("\n👤 사용자: 안녕하세요!")
    state["messages"].append(HumanMessage(content="안녕하세요!"))

    result = app.invoke(state)
    print_state_info(result, "Step 1: 인사")
    state = result

    print_divider()

    # 2. 문제 상담 시작
    print("\n👤 사용자: 앱이 자꾸 느려지는데 어떻게 해야 하나요?")
    state["messages"].append(HumanMessage(content="앱이 자꾸 느려지는데 어떻게 해야 하나요?"))

    result = app.invoke(state)
    print_state_info(result, "Step 2: 문제 상담")
    state = result

    print_divider()

    # 3. 첫 번째 단계 수행 (모호한 답변 - 했는지 안 했는지 불명확)
    print("\n👤 사용자: 음... 캐시는 뭔가요? 그냥 앱을 껐다 켰는데")
    state["messages"].append(HumanMessage(content="음... 캐시는 뭔가요? 그냥 앱을 껐다 켰는데"))

    result = app.invoke(state)
    print_state_info(result, "Step 3: 모호한 응답")
    state = result

    print_divider()

    # 4. 단계 수행했지만 미해결
    print("\n👤 사용자: 아, 캐시 삭제 했는데 여전히 느려요")
    state["messages"].append(HumanMessage(content="아, 캐시 삭제 했는데 여전히 느려요"))

    result = app.invoke(state)
    print_state_info(result, "Step 4: 단계 수행, 미해결")
    state = result

    print_divider()

    # 5. 다음 단계 수행 후 해결
    print("\n👤 사용자: 앱을 재설치했더니 이제 잘 되네요! 감사합니다")
    state["messages"].append(HumanMessage(content="앱을 재설치했더니 이제 잘 되네요! 감사합니다"))

    result = app.invoke(state)
    print_state_info(result, "Step 5: 해결 완료")
    state = result

    print("\n✅ 시나리오 1 완료")
    return state


def test_scenario_2_escalation_with_misunderstanding():
    """
    시나리오 2: 오해와 에스컬레이션
    - 문제 상담
    - 단계 수행했다는 모호한 답변 (했는데, 했지만 등)
    - AI가 잘못 이해하는지 확인
    - 결국 티켓 생성
    """
    print_divider("시나리오 2: 오해 상황과 티켓 생성")

    app = create_workflow()
    state = {"messages": [], "user_id": "test_user_002"}

    # 1. 문제 상담
    print("\n👤 사용자: 로그인이 안 돼요")
    state["messages"].append(HumanMessage(content="로그인이 안 돼요"))

    result = app.invoke(state)
    print_state_info(result, "Step 1: 문제 상담")
    state = result

    print_divider()

    # 2. 모호한 답변 1 - "했어요" (수행했지만 결과 불명)
    print("\n👤 사용자: 비밀번호 재설정 했어요")
    state["messages"].append(HumanMessage(content="비밀번호 재설정 했어요"))

    result = app.invoke(state)
    print_state_info(result, "Step 2: 모호한 답변 (했어요)")
    state = result

    print_divider()

    # 3. 모호한 답변 2 - "했는데" (했지만 안 됨)
    print("\n👤 사용자: 다 했는데 그래도 로그인이 안 돼요")
    state["messages"].append(HumanMessage(content="다 했는데 그래도 로그인이 안 돼요"))

    result = app.invoke(state)
    print_state_info(result, "Step 3: 미해결 표현")
    state = result

    print_divider()

    # 4. 모든 단계 시도 후 여전히 안됨
    print("\n👤 사용자: 세 번째 방법도 해봤는데 안 되네요. 답답해요")
    state["messages"].append(HumanMessage(content="세 번째 방법도 해봤는데 안 되네요. 답답해요"))

    result = app.invoke(state)
    print_state_info(result, "Step 4: 모든 단계 실패")
    state = result

    print_divider()

    # 5. 티켓 생성 확인
    print("\n👤 사용자: 네, 등록해주세요")
    state["messages"].append(HumanMessage(content="네, 등록해주세요"))

    result = app.invoke(state)
    print_state_info(result, "Step 5: 티켓 생성")
    state = result

    print("\n✅ 시나리오 2 완료")
    return state


def test_scenario_3_small_talk_then_problem():
    """
    시나리오 3: 잡담 후 문제 상담으로 자연스러운 전환
    """
    print_divider("시나리오 3: 스몰톡에서 기술 상담으로 전환")

    app = create_workflow()
    state = {"messages": [], "user_id": "test_user_003"}

    # 1. 인사
    print("\n👤 사용자: 안녕하세요~")
    state["messages"].append(HumanMessage(content="안녕하세요~"))

    result = app.invoke(state)
    print_state_info(result, "Step 1: 인사")
    state = result

    print_divider()

    # 2. 잡담
    print("\n👤 사용자: 오늘 날씨 좋네요!")
    state["messages"].append(HumanMessage(content="오늘 날씨 좋네요!"))

    result = app.invoke(state)
    print_state_info(result, "Step 2: 잡담")
    state = result

    print_divider()

    # 3. 문제 상담으로 전환
    print("\n👤 사용자: 그런데 앱에서 결제가 안 되는데 확인 좀 해주실래요?")
    state["messages"].append(HumanMessage(content="그런데 앱에서 결제가 안 되는데 확인 좀 해주실래요?"))

    result = app.invoke(state)
    print_state_info(result, "Step 3: 기술 문제로 전환")
    state = result

    print_divider()

    # 4. 단계 수행 - 해결됨
    print("\n👤 사용자: 네, 카드 정보 다시 입력했더니 됐어요! 고마워요")
    state["messages"].append(HumanMessage(content="네, 카드 정보 다시 입력했더니 됐어요! 고마워요"))

    result = app.invoke(state)
    print_state_info(result, "Step 4: 해결")
    state = result

    print("\n✅ 시나리오 3 완료")
    return state


def test_scenario_4_ambiguous_responses():
    """
    시나리오 4: 다양한 모호한 표현들 테스트
    - "했어요", "했습니다" vs "됐어요", "됐습니다"
    - "했는데", "했지만"
    - "잠시만요", "확인해볼게요" (대기 표현)
    - 시스템이 제대로 구분하는지 확인
    """
    print_divider("시나리오 4: 모호한 표현 구분 테스트")

    app = create_workflow()
    state = {"messages": [], "user_id": "test_user_004"}

    # 1. 문제 상담
    print("\n👤 사용자: 알림이 안 와요")
    state["messages"].append(HumanMessage(content="알림이 안 와요"))

    result = app.invoke(state)
    print_state_info(result, "Step 1: 문제")
    state = result

    print_divider()

    # 2. 대기 표현 - "잠시만요, 확인해볼게요"
    print("\n👤 사용자: 잠시만요, 설정 확인해볼게요")
    state["messages"].append(HumanMessage(content="잠시만요, 설정 확인해볼게요"))

    result = app.invoke(state)
    print_state_info(result, "Step 2: '잠시만요 확인해볼게요' (대기)")
    expected_status = "waiting_user"  # 대기 상태여야 함
    actual_status = result.get("status")
    print(f"  ⚠️ 기대: {expected_status}, 실제: {actual_status}")
    state = result

    print_divider()

    # 3. "했어요" - 수행만 함 (해결 X)
    print("\n👤 사용자: 설정 확인 했어요")
    state["messages"].append(HumanMessage(content="설정 확인 했어요"))

    result = app.invoke(state)
    print_state_info(result, "Step 3: '했어요' (수행만 함)")
    expected_status = "responding"  # 다음 단계로 가야 함
    actual_status = result.get("status")
    print(f"  ⚠️ 기대: {expected_status}, 실제: {actual_status}")
    state = result

    print_divider()

    # 4. "했는데 안돼요" - 명확한 미해결
    print("\n👤 사용자: 앱 재시작 했는데 안돼요")
    state["messages"].append(HumanMessage(content="앱 재시작 했는데 안돼요"))

    result = app.invoke(state)
    print_state_info(result, "Step 4: '했는데 안돼요'")
    state = result

    print_divider()

    # 5. "됐어요!" - 명확한 해결
    print("\n👤 사용자: 아 이제 알림 됐어요!")
    state["messages"].append(HumanMessage(content="아 이제 알림 됐어요!"))

    result = app.invoke(state)
    print_state_info(result, "Step 5: '됐어요!' (해결)")
    expected_status = "resolved"
    actual_status = result.get("status")
    print(f"  ⚠️ 기대: {expected_status}, 실제: {actual_status}")
    state = result

    print("\n✅ 시나리오 4 완료")
    return state


def test_scenario_5_ticket_cancellation():
    """
    시나리오 5: 티켓 생성 취소
    - 모든 단계 실패
    - 티켓 확인 받을 때 취소
    """
    print_divider("시나리오 5: 티켓 생성 취소")

    app = create_workflow()
    state = {"messages": [], "user_id": "test_user_005"}

    # 1. 문제 상담
    print("\n👤 사용자: 계정이 잠겼어요")
    state["messages"].append(HumanMessage(content="계정이 잠겼어요"))

    result = app.invoke(state)
    print_state_info(result, "Step 1: 문제")
    state = result

    # 2-4. 모든 단계 실패
    for i in range(3):
        print_divider()
        print(f"\n👤 사용자: 시도했지만 안 됩니다 (단계 {i+1})")
        state["messages"].append(HumanMessage(content=f"시도했지만 안 됩니다"))

        result = app.invoke(state)
        print_state_info(result, f"Step {i+2}: 실패 {i+1}")
        state = result

    print_divider()

    # 5. 티켓 생성 거부
    print("\n👤 사용자: 아니요, 나중에 다시 연락할게요")
    state["messages"].append(HumanMessage(content="아니요, 나중에 다시 연락할게요"))

    result = app.invoke(state)
    print_state_info(result, "Step 5: 티켓 취소")
    state = result

    print("\n✅ 시나리오 5 완료")
    return state


def main():
    """모든 시나리오 실행"""
    print("\n" + "="*80)
    print(" 자연스러운 대화 흐름 테스트 시작")
    print("="*80)

    try:
        # 시나리오 1: 전체 자연스러운 흐름
        test_scenario_1_natural_flow()

        # 시나리오 2: 오해와 에스컬레이션
        test_scenario_2_escalation_with_misunderstanding()

        # 시나리오 3: 스몰톡에서 기술 상담으로 전환
        test_scenario_3_small_talk_then_problem()

        # 시나리오 4: 모호한 표현 구분
        test_scenario_4_ambiguous_responses()

        # 시나리오 5: 티켓 취소
        test_scenario_5_ticket_cancellation()

        print("\n" + "="*80)
        print(" 🎉 모든 테스트 완료!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
