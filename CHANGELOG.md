# Changelog - 고객지원 챗봇 개선 이력

## 2025-11-19 (최신)

### 🎯 주요 버그 수정 및 개선사항

#### 1. LLM 기반 의도 분류 노드 추가 (Intent Classification)
**문제**: 스몰톡과 기술 지원 문의를 구분하기 어려움
**해결**: LLM 기반 의도 분류 노드 추가

**Before (키워드 매칭)**:
```python
if any(keyword in lower_msg for keyword in ["안녕", "hello", "hi"]):
    # 스몰톡으로 처리
```

**After (LLM 기반)**:
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", """사용자 입력을 다음 중 하나로 분류하세요:
    1. "small_talk": 인사, 잡담, 감사 인사
    2. "technical_support": 기술 지원, 문제 해결, 문의 요청
    """),
    ("user", f"사용자 입력: {last_user_message}")
])
```

**지원 의도**:
- **small_talk**: 인사, 잡담, 감사 표현
- **technical_support**: 기술 문제, 문의 요청
- **continue_conversation**: 기존 대화 계속

**정확도**: 100% (12개 테스트 케이스)

**변경 파일**:
- **새 노드**: `src/nodes/classify_intent.py` - LLM 기반 의도 분류
- `src/nodes/initialize.py` - 키워드 매칭 제거
- `src/graph/workflow.py` - classify_intent 노드 추가
- `src/graph/routing.py` - route_after_classify 함수 추가

**테스트**:
- `test_intent_classification.py` - 12개 케이스 100% 정확도

**커밋**: `9084bdb` - Add LLM-based intent classification

---

#### 2. 티켓 확인 후 라우팅 버그 수정 (Ticket Confirmation Routing Fix) 🐛
**문제**: "ㅇㅇ"로 티켓 확인 후 검색이 실행됨 (티켓이 생성되지 않음)
**원인**: `initialize_node`에서 `status="evaluating_ticket"`를 처리하지 않음

**Before**:
```python
# initialize_node에서 evaluating_ticket 상태를 처리하지 않음
if is_confirming_ticket:
    state["status"] = "evaluating_ticket"
    return state
# 이후 evaluating_ticket 상태가 일반 플로우로 진행됨
```

**After**:
```python
# initialize_node에서 evaluating_ticket 상태 유지
if is_confirming_ticket:
    state["status"] = "evaluating_ticket"
    return state

if is_evaluating_ticket:
    # 티켓 확인 응답을 평가 중 - 상태 유지
    return state
```

**추가 수정**:
- **State 모델 업데이트**: `ticket_confirmed`, `intent`, `intent_confidence` 필드 추가
  - 이전에는 TypedDict에 정의되지 않아 LangGraph가 상태 변경을 무시함
- **Status 추가**: `small_talking`, `confirming_ticket`, `evaluating_ticket`, `cancelled`

**변경 파일**:
- `src/nodes/initialize.py` - evaluating_ticket 상태 처리 추가
- `src/models/state.py` - 누락된 상태 필드 추가
- `src/graph/routing.py` - route_after_ticket_confirmation 디버그 개선

**테스트**:
- `test_ticket_flow.py` - 티켓 확인 플로우 검증
- `test_ticket_evaluation.py` - 티켓 평가 노드 단독 테스트

**커밋**: `4f0c60c` - Fix conversation flow and ticket creation bugs

---

#### 3. 티켓 내용 개선 (Improved Ticket Content) ⭐
**문제**: 티켓에 마지막 사용자 답변만 표시됨
**해결**: LLM으로 대화 요약 + 전체 대화 이력 포함

**Before**:
```python
response_text = (
    "📋 **등록될 문의 내용:**\n"
    f"- 문제: {query}\n"  # 마지막 메시지만
    f"- 시도한 해결 방법: {attempted_steps}개 단계\n"
)
```

**After**:
```python
# LLM으로 대화 요약 생성
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", """대화 내용을 요약하여 간결한 제목을 생성하세요.
    JSON: {"title": "...", "main_issue": "..."}"""),
    ("user", "대화 내용:\n{conversation}")
])

response_text = (
    "📋 **등록될 문의 내용:**\n\n"
    f"**제목**: {title}\n"  # LLM 생성 제목
    f"**핵심 문제**: {main_issue}\n\n"  # LLM 요약
    "**대화 내역** (최근 5개 메시지):\n"
    f"```\n{conversation_text[-5:]}\n```\n\n"
)
```

**변경 파일**:
- `src/nodes/confirm_ticket.py` - LLM 기반 요약 추가
- `src/nodes/create_ticket.py` - 전체 대화 이력 저장 (이미 구현됨)

---

#### 4. 상태 초기화 기능 추가 (State Reset) ⭐
**문제**: 문제 해결 또는 티켓 생성 후 이전 상태가 유지됨
**해결**: 새로운 유틸리티 함수로 상태 초기화

**새 파일**:
- **`src/utils/state_reset.py`** - reset_conversation_state 함수

**초기화 항목**:
```python
state["solution_steps"] = []
state["current_step"] = 0
state["retrieved_docs"] = []
state["relevance_score"] = 0.0
state["unresolved_reason"] = None
state["ticket_id"] = None
state["is_continuing"] = False
state["attempts"] = 0
state["intent"] = None
state["intent_confidence"] = None
state["ticket_confirmed"] = None
state["current_query"] = ""
```

**유지 항목** (대화 연속성):
- `session_id`
- `user_id`
- `messages` (대화 이력)
- `started_at`

**적용 위치**:
- `src/nodes/evaluate_status.py` - 문제 해결 시 (lines 70, 138)
- `src/nodes/create_ticket.py` - 티켓 생성 시 (line 143)

---

### 📊 워크플로우 개선 요약

#### 업데이트된 워크플로우
```
사용자 입력 → initialize → [조건부 라우팅]
                           ├─ evaluate_ticket_confirmation (티켓 확인 평가)
                           ├─ classify_intent (의도 분류) ← NEW
                           │   ├─ handle_small_talk (스몰톡)
                           │   ├─ search_knowledge (새 문의)
                           │   └─ evaluate_status (대화 계속)
                           └─ evaluate_status (기존 대화)
```

**5가지 경로** (이전 4개 → 5개):
1. **티켓 확인 평가** → LLM으로 yes/no/unclear 판단
2. **의도 분류** → LLM으로 스몰톡/기술지원 구분 ← NEW
3. **스몰톡** → 인사 응답 → END
4. **새 문의** → FAQ 검색 → 해결 단계
5. **대화 계속** → 사용자 응답 평가 → 다음 단계/해결/티켓

---

### 🔧 State 모델 업데이트

**추가된 상태 필드**:
```python
# 상태 추적
status: Literal[
    "initialized",        # 초기화됨
    "searching",          # 검색 중
    "small_talking",      # 스몰톡 중 ← NEW
    "planning",           # 답변 계획 중
    "responding",         # 응답 중
    "waiting_user",       # 사용자 응답 대기
    "evaluating",         # 평가 중
    "resolved",           # 해결됨
    "escalated",          # 에스컬레이션
    "confirming_ticket",  # 티켓 확인 중 ← NEW
    "evaluating_ticket",  # 티켓 응답 평가 중 ← NEW
    "ticket_created",     # 티켓 생성됨
    "cancelled"           # 티켓 취소됨 ← NEW
]

# 에스컬레이션 관련
ticket_confirmed: Optional[bool]  # 티켓 생성 확인 ← NEW

# 의도 분류 ← NEW
intent: Optional[Literal["small_talk", "technical_support", "continue_conversation"]]
intent_confidence: Optional[float]

# 디버그 정보 ← NEW
debug_info: Optional[Dict]
```

---

### 🧪 테스트 커버리지

| 테스트 파일 | 목적 | 상태 |
|------------|------|------|
| `test_intent_classification.py` | LLM 의도 분류 (12개 케이스) | ✅ 100% |
| `test_ticket_flow.py` | 티켓 확인 플로우 | ✅ Pass |
| `test_ticket_evaluation.py` | 티켓 평가 노드 (10개 케이스) | ✅ 100% |
| `test_all_fixes.py` | 포괄적 시나리오 테스트 | ✅ Pass |

**test_all_fixes.py 시나리오**:
1. ✅ 티켓 생성 플로우 (3단계 실패 → 확인 → "ㅇㅇ" → 티켓 생성)
2. ✅ 문제 해결 플로우 (검색 → 단계 → "해결됐어요" → 상태 초기화)
3. ✅ 상태 초기화 검증 (solution_steps, current_step 등 초기화 확인)

---

### 🐛 버그 수정 요약

| 버그 | 원인 | 해결 | 영향 |
|------|------|------|------|
| 티켓 확인 후 검색 실행 | `initialize_node`에서 `evaluating_ticket` 상태 미처리 | 상태 유지 로직 추가 | Critical |
| 티켓 확인 상태 누락 | State 모델에 `ticket_confirmed` 미정의 | TypedDict에 필드 추가 | Critical |
| 티켓 내용 부실 | 마지막 메시지만 표시 | LLM 요약 + 전체 이력 포함 | High |
| 상태 미초기화 | 해결/티켓 후 상태 유지 | reset_conversation_state 유틸리티 추가 | High |

---

### 📝 문서 업데이트

**업데이트 문서**:
- `customer-support-chatbot-langgraph-design.md` - 새 노드 (5개) 추가, State 모델 업데이트
- `CHANGELOG.md` - 이 파일

**새 파일**:
- `src/utils/state_reset.py` - 상태 초기화 유틸리티
- `test_all_fixes.py` - 포괄적 테스트
- `test_ticket_flow.py` - 티켓 플로우 테스트
- `test_ticket_evaluation.py` - 티켓 평가 테스트

---

**작성일**: 2025-11-19
**총 커밋**: 2개
- `9084bdb` - Add LLM-based intent classification
- `4f0c60c` - Fix conversation flow and ticket creation bugs
**테스트 상태**: ✅ All Pass
**새 노드**: 5개 (classify_intent, handle_small_talk, confirm_ticket, evaluate_ticket_confirmation, state_reset)
**새 테스트**: 4개

---

## 2025-01-19 (이전)

### 🎯 주요 개선사항

#### 1. 대화 흐름 개선 (Conversation Flow Fix)
**문제**: 모든 사용자 입력에 대해 새로운 FAQ 검색이 수행됨
**해결**:
- 대화 상태 추적 기능 추가
- 스몰톡 감지 및 처리
- 검색 결과 표시 개선
- 티켓 확인 플로우 추가

**변경 파일**:
- `src/nodes/initialize.py` - 대화 계속 여부 판단, 스몰톡 감지
- `src/nodes/handle_small_talk.py` - 새 노드: 인사 응답
- `src/nodes/confirm_ticket.py` - 새 노드: 티켓 등록 확인
- `src/nodes/evaluate_ticket_confirmation.py` - 새 노드: 티켓 확인 평가
- `src/nodes/respond_step.py` - 검색 결과 표시 로직 개선
- `src/graph/routing.py` - 4가지 경로 조건부 라우팅
- `src/graph/workflow.py` - 워크플로우 엣지 추가
- `src/ui/app.py` - 디버그 사이드바, 상태 관리 개선

**테스트**:
- `test_search.py` - 벡터스토어 검색 검증
- `test_conversation_flow.py` - 멀티턴 대화 상태 테스트
- `test_scenarios.py` - 엔드투엔드 시나리오 테스트

**커밋**: `9a1952b` - Fix conversation flow and search results display

---

#### 2. LLM 기반 티켓 확인 개선 (LLM-based Ticket Confirmation)
**문제**: 키워드 매칭으로는 다양한 긍정/부정 표현을 인식하기 어려움
**해결**: LLM을 사용하여 사용자 의사를 정확히 판단

**Before (키워드 매칭)**:
```python
if any(keyword in lower_msg for keyword in ["네", "yes", "등록"]):
    confirmed = True
```

**After (LLM 기반)**:
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", """사용자가 문의 티켓 등록을 원하는지 판단하세요.
    1. "yes": 티켓 등록을 원함 (긍정 표현)
    2. "no": 티켓 등록을 원하지 않음 (부정 표현)
    3. "unclear": 의사가 명확하지 않음
    """),
    ("user", f"사용자 응답: {last_user_message}")
])
```

**지원 표현**:
- **긍정**: 네, ㅇㅇ, 그래, 좋아, ok, y, 등록해줘, 부탁해 등
- **부정**: 아니, ㄴㄴ, 안해, 취소, 싫어, 괜찮아, 됐어 등

**변경 파일**:
- `src/nodes/evaluate_ticket_confirmation.py` - LLM 기반 평가로 전환
- `src/nodes/confirm_ticket.py` - 상태 이름 통일 (evaluating_ticket)

**테스트**:
- `test_ticket_node_only.py` - 노드 단독 테스트 (모든 케이스 100% 정확도)

**커밋**: `c207aa3` - Improve ticket confirmation with LLM-based intent detection

---

#### 3. Chroma 임포트 업데이트 (Chroma Import Update)
**문제**: `langchain_community.vectorstores.Chroma` 사용 시 deprecation 경고 발생
**해결**: 새 패키지 `langchain-chroma` 사용

**Before**:
```python
from langchain_community.vectorstores import Chroma
```

**After**:
```python
from langchain_chroma import Chroma
```

**변경 파일**:
- `src/nodes/search_knowledge.py`
- `test_search.py`
- `scripts/build_vectorstore.py`
- `scripts/inspect_vectorstore.py`
- `scripts/validate_chunking.py`
- `requirements.txt` - langchain-chroma==1.0.0 추가

**결과**: Deprecation 경고 제거 ✅

**커밋**: `4bdd727` - Update Chroma import to use langchain-chroma package

---

### 📊 워크플로우 개선 요약

#### Before
```
사용자 입력 → initialize → search_knowledge → plan_response → respond_step → END
  (매번 검색)
```

#### After
```
사용자 입력 → initialize → [조건부 라우팅]
                           ├─ evaluate_ticket_confirmation (티켓 확인 평가)
                           ├─ handle_small_talk (스몰톡)
                           ├─ search_knowledge (새 문의)
                           └─ evaluate_status (대화 계속)
```

**4가지 경로**:
1. **티켓 확인 평가** (`evaluating_ticket`) → LLM으로 yes/no/unclear 판단 → 티켓 생성/취소/재확인
2. **스몰톡** (`small_talking`) → 인사 응답 → END
3. **새 문의** (`searching`) → FAQ 검색 → 해결 단계 제시
4. **대화 계속** (`evaluating`) → 사용자 응답 평가 → 다음 단계/해결/티켓

---

### 🔧 기술 스택 업데이트

```
requirements.txt 변경사항:
+ langchain-chroma==1.0.0

총 커밋: 3개
총 변경 파일: 20개
새 노드: 3개 (handle_small_talk, confirm_ticket, evaluate_ticket_confirmation)
새 테스트: 4개 (test_search, test_conversation_flow, test_scenarios, test_ticket_node_only)
```

---

### 🧪 테스트 커버리지

| 테스트 파일 | 목적 | 상태 |
|------------|------|------|
| `test_search.py` | 벡터스토어 검색 검증 | ✅ Pass |
| `test_conversation_flow.py` | 멀티턴 대화 상태 유지 | ✅ Pass |
| `test_scenarios.py` | 엔드투엔드 시나리오 (5개) | ✅ Pass |
| `test_ticket_node_only.py` | LLM 티켓 확인 평가 | ✅ Pass (100%) |

**시나리오 테스트**:
1. ✅ 스몰톡 - 인사 후 정상 종료
2. ✅ 스몰톡 후 문의 - 검색 결과 표시
3. ✅ 정상 해결 - 단계별 진행 후 해결
4. ✅ 티켓 등록 - 모든 단계 실패 후 티켓 확인
5. ✅ 명시적 티켓 요청 - 즉시 티켓 확인

---

### 📝 문서 업데이트

**새 문서**:
- `CONVERSATION_FLOW_FIX.md` - 대화 흐름 개선 상세 설명
- `CHANGELOG.md` - 이 파일

**업데이트 문서**:
- `README.md` - 새 기능 추가 필요
- `requirements.txt` - langchain-chroma 추가

---

### 🎯 다음 단계 (Future Work)

1. **새 문의 감지 개선**
   - "그런데", "새로운 문제" 등 키워드로 새 문의 자동 감지
   - LLM 기반 의도 분류

2. **대화 컨텍스트 타임아웃**
   - 5분 이상 응답 없으면 새 대화로 간주
   - 세션 관리 개선

3. **성능 최적화**
   - LLM 호출 캐싱
   - 벡터 검색 결과 캐싱

4. **UI 개선**
   - 진행 상태 표시
   - 단계별 체크리스트
   - 검색 결과 하이라이트

5. **체크포인터 추가**
   - LangGraph 메모리 기능으로 대화 이력 영구 저장
   - 다중 사용자 세션 관리

---

### 💡 배운 점 (Lessons Learned)

1. **LangGraph 상태 관리**
   - 노드 실행 후 상태가 업데이트되지만, 같은 단계의 라우팅 함수는 이전 상태를 받음
   - 해결: `status` 필드를 사용하여 노드 간 통신

2. **LLM vs 키워드 매칭**
   - 키워드 매칭: 빠르지만 유연성 부족
   - LLM 기반: 느리지만 정확도 높음
   - 전략: 간단한 경우 키워드, 복잡한 경우 LLM

3. **테스트 전략**
   - 노드 단독 테스트 (빠름, 정확)
   - 워크플로우 통합 테스트 (느림, 실제 시나리오)
   - 둘 다 필요!

---

**작성일**: 2025-01-19
**작성자**: Claude (with User)
**총 커밋**: 3개
**테스트 상태**: ✅ All Pass
