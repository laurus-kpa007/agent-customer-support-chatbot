# Changelog - 고객지원 챗봇 개선 이력

## 2025-01-19 (오늘)

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
