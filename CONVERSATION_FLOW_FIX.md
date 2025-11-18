# 대화 흐름 개선 (Conversation Flow Fix)

## 🎯 문제점

기존 시스템은 **모든 사용자 입력에 대해 새로운 FAQ 검색**을 수행했습니다:

```
사용자: 메시지가 안 보내져
  → FAQ 검색 → 단계 1 제안

사용자: 확인했어요
  → FAQ 검색 (새로 검색!) → 엉뚱한 결과

사용자: 안녕
  → FAQ 검색 (스몰톡에도!) → 엉뚱한 결과
```

## ✅ 해결 방법

### 1. 대화 상태 추적

이제 시스템은 대화가 계속되는지 새로운 문의인지 구분합니다:

- **새 문의**: FAQ 검색 시작
- **대화 계속**: 이전 단계의 다음 단계로 진행

### 2. 구현 세부사항

#### A. Initialize 노드 개선 ([src/nodes/initialize.py:57-81](src/nodes/initialize.py#L57-L81))

```python
# 대화 계속 여부 판단
has_steps = state.get("solution_steps") and len(state.get("solution_steps", [])) > 0
was_waiting = state.get("status") == "waiting_user"
is_continuing = has_steps and was_waiting

if is_continuing:
    # 대화 계속: 검색 건너뛰고 evaluate로
    state["status"] = "evaluating"
else:
    # 새 대화: 검색 시작
    state["status"] = "searching"
```

**판단 기준**:
- `solution_steps`가 있음 → 이전에 문제를 분석한 적 있음
- `status == "waiting_user"` → 사용자 응답 대기 중이었음
- 둘 다 참이면 → 대화 계속

#### B. 조건부 라우팅 추가 ([src/graph/routing.py:14-32](src/graph/routing.py#L14-L32))

```python
def route_after_initialize(state: SupportState) -> str:
    # initialize 노드가 설정한 status를 사용
    status = state.get("status")
    route = "evaluate" if status == "evaluating" else "search"
    return route
```

**중요**: `is_continuing` 플래그 대신 `status`를 사용하는 이유:
- LangGraph는 노드 실행 후 상태를 업데이트하지만
- 같은 단계의 라우팅 함수는 **업데이트 이전 상태**를 받음
- 따라서 노드 내부에서 설정한 `status` 필드를 라우팅에 사용

#### C. 워크플로우 경로 분기 ([src/graph/workflow.py:51-59](src/graph/workflow.py#L51-L59))

```python
# initialize 후 조건부 라우팅 (새 대화 vs 계속)
workflow.add_conditional_edges(
    "initialize",
    route_after_initialize,
    {
        "search": "search_knowledge",      # 새 대화 - 검색
        "evaluate": "evaluate_status"      # 기존 대화 - 평가
    }
)
```

#### D. UI 상태 유지 ([src/ui/app.py:130-138](src/ui/app.py#L130-L138))

```python
# 상태 준비 - 기존 워크플로우 상태와 병합
input_state = {
    **st.session_state.workflow_state,  # 기존 상태 유지
    "messages": [
        HumanMessage(content=msg["content"]) if msg["role"] == "user"
        else AIMessage(content=msg["content"])
        for msg in st.session_state.messages
    ],
    "user_id": "user_001"
}
```

**핵심**: `workflow_state`를 세션에 저장하여 다음 턴에 전달

## 📊 대화 흐름 비교

### Before (문제)
```
턴 1: "메시지가 안 보내져"
  → initialize → search → plan → respond
  → "단계 1: 인터넷 연결 확인"

턴 2: "확인했어요"
  → initialize → search (다시!) → plan → respond
  → "단계 1: 비밀번호 재설정" (엉뚱한 결과!)
```

### After (개선)
```
턴 1: "메시지가 안 보내져"
  → initialize → search → plan → respond
  → "단계 1: 인터넷 연결 확인"

턴 2: "확인했어요"
  → initialize → evaluate → respond
  → "단계 2: 앱 재시작" (같은 문제의 다음 단계!)
```

## 🧪 테스트

### 실행 방법
```bash
. venv/Scripts/activate
python test_conversation_flow.py
```

### 테스트 시나리오
```python
턴 1: "메시지가 안 보내져요"
  → 검색: "메시지가 전송되지 않음" (FAQ-008)
  → 단계 1/3: 인터넷 연결 확인

턴 2: "확인했는데 안돼요"
  → 평가: continue
  → 단계 2/3: 메신저 앱 재시작

턴 3: "그것도 안돼요"
  → 평가: continue
  → 단계 3/3: 앱 캐시 삭제
```

### 예상 출력
```
[턴 1] 사용자: 메시지가 안 보내져요
노드: respond_step
검색 결과: 3개
  - 메시지가 전송되지 않음
해결 단계: 3개
AI 응답: [단계 1/3] 인터넷 연결 상태 확인

[턴 2] 사용자: 확인했는데 안돼요
  → initialize 실행
  → evaluate_status 실행  ✅
  → respond_step 실행
AI 응답: [단계 2/3] 메신저 앱 재시작

[턴 3] 사용자: 그것도 안돼요
  → initialize 실행
  → evaluate_status 실행  ✅
  → respond_step 실행
AI 응답: [단계 3/3] 메신저 앱 캐시 삭제
```

## 🎨 사용자 시나리오

### 시나리오 1: 정상적인 문제 해결
```
사용자: 파일 업로드가 안돼요
AI: [검색] 파일 업로드 실패 FAQ
    [단계 1/3] 파일 크기 확인 (100MB 이하)

사용자: 확인했어요, 50MB예요
AI: [평가] continue
    [단계 2/3] 파일 형식 확인

사용자: JPG 파일인데요
AI: [평가] continue
    [단계 3/3] 브라우저 캐시 삭제

사용자: 됐어요!
AI: [평가] resolved
    🎉 문제가 해결되어 다행입니다!
```

### 시나리오 2: 티켓 에스컬레이션
```
사용자: 로그인이 안돼요
AI: [단계 1/3] 비밀번호 재설정

사용자: 해봤는데 안돼요
AI: [단계 2/3] 캐시 삭제

사용자: 그것도 안돼요
AI: [단계 3/3] 다른 브라우저 시도

사용자: 다 해봤는데 안돼요, 등록해주세요
AI: [평가] escalate
    [티켓 생성] TICKET-2025-001
    📧 담당자에게 알림 전송
```

### 시나리오 3: 새로운 문의
```
사용자: 파일 업로드가 안돼요
AI: [단계 1/3] 파일 크기 확인

사용자: 됐어요!
AI: 🎉 해결되었습니다!

사용자: 그런데 비밀번호를 잊어버렸어요
AI: [새 검색] 비밀번호 재설정 FAQ
    [단계 1/3] 비밀번호 재설정 링크
```

## 🔍 디버깅 방법

코드에 디버그 로그가 주석 처리되어 있습니다. 필요시 활성화:

### Initialize 노드
```python
# src/nodes/initialize.py:65-66, 73, 79
print(f"[Initialize] has_steps={has_steps}, was_waiting={was_waiting}")
print(f"[Initialize] → 대화 계속 (evaluating)")
```

### 라우팅
```python
# src/graph/routing.py:30
print(f"[RouteAfterInit] status={status} → {route}")
```

### Evaluate 노드
```python
# src/nodes/evaluate_status.py:39, 56, 131
print(f"[Evaluate] 시작 - current_step={state.get('current_step')}")
print(f"[Evaluate] 사용자 응답: {last_user_message}")
print(f"[Evaluate] LLM 판단 → continue")
```

## 📝 핵심 변경 파일

| 파일 | 변경 내용 |
|------|----------|
| [src/nodes/initialize.py](src/nodes/initialize.py) | 대화 계속 여부 판단 로직 추가 |
| [src/graph/routing.py](src/graph/routing.py) | `route_after_initialize` 함수 추가 |
| [src/graph/workflow.py](src/graph/workflow.py) | 조건부 라우팅 엣지 추가 |
| [src/ui/app.py](src/ui/app.py) | `workflow_state` 세션 관리 |

## 🚀 다음 단계

### 가능한 추가 개선사항

1. **새 문의 감지 개선**
   ```python
   # "그런데", "새로운 문제인데" 등의 키워드로 새 문의 감지
   if any(keyword in lower_msg for keyword in ["그런데", "새로운", "다른 문제"]):
       # 현재 대화 종료하고 새 검색 시작
   ```

2. **대화 컨텍스트 타임아웃**
   ```python
   # 5분 이상 응답 없으면 새 대화로 간주
   if (datetime.now() - last_message_time).seconds > 300:
       is_continuing = False
   ```

3. **의도 분류 LLM 사용**
   ```python
   # LLM으로 사용자 의도 분류 (새 문의 vs 대화 계속)
   intent = classify_intent(user_message, conversation_history)
   ```

## ✅ 완료된 개선사항

- [x] 대화 상태 추적
- [x] 조건부 라우팅 (새 문의 vs 계속)
- [x] UI 상태 유지
- [x] 멀티턴 대화 테스트
- [x] 디버그 로그 추가 (주석 처리)
- [x] 문서화

---

**작성일**: 2025-01-18
**작성자**: Claude (with User)
**테스트 완료**: ✅ Yes
