"""Send Notification Node - 알림 발송

티켓 생성 알림을 발송합니다 (PoC: 콘솔 출력).
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from typing import Dict, Any

from src.models.state import SupportState


def send_notification_node(state: SupportState) -> Dict[str, Any]:
    """
    알림 발송 노드
    - 이메일 알림 (PoC: 콘솔 출력)
    - 푸시 알림 시뮬레이션

    Args:
        state: 현재 상태

    Returns:
        업데이트된 상태
    """

    ticket_id = state.get("ticket_id", "N/A")
    user_id = state.get("user_id", "anonymous")

    # 이메일 내용 생성
    email_content = f"""
안녕하세요,

문의가 정상적으로 등록되었습니다.

문의번호: {ticket_id}
등록시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

담당자가 확인 후 답변을 드리겠습니다.
답변이 등록되면 다시 알림을 보내드립니다.

감사합니다.
    """

    # PoC: 콘솔 출력
    print("\n" + "="*60)
    print("📧 이메일 발송 시뮬레이션")
    print("="*60)
    print(f"To: user_{user_id}@example.com")
    print(f"Subject: [고객지원] 문의가 등록되었습니다 (#{ticket_id})")
    print(email_content)
    print("="*60 + "\n")

    # 실제 프로덕션에서는:
    # send_email(
    #     to=user_email,
    #     subject=f"[고객지원] 문의가 등록되었습니다 (#{ticket_id})",
    #     body=email_content
    # )

    print("📱 푸시 알림 발송 시뮬레이션")
    print(f"   사용자: {user_id}")
    print(f"   메시지: 문의가 등록되었습니다 (#{ticket_id})")
    print()

    # 대화 상태 초기화
    from src.utils.state_reset import reset_conversation_state
    state = reset_conversation_state(state)

    return state
