# 고객지원 챗봇 Agent - LangGraph PoC

FAQ와 Q&A 게시판 데이터를 기반으로 사용자 질의에 단계별(Step-by-Step)로 답변하고, 해결되지 않을 경우 자동으로 게시판에 등록하는 고객지원 챗봇 시스템

## 📋 프로젝트 개요

### 핵심 기능
- ✅ **FAQ/Q&A 데이터 기반 RAG 검색**: 벡터 스토어를 활용한 의미 기반 검색
- ✅ **단계별 문제 해결**: 사용자 문제에 대한 Step-by-Step 가이드 제공
- ✅ **Human-in-the-Loop**: 각 단계마다 사용자 확인 및 피드백 수집
- ✅ **자동 티켓 생성**: 미해결 시 Q&A 게시판 자동 등록
- ✅ **알림 시스템**: 답변 등록 시 이메일/푸시 알림

### 사용 예시

```
사용자: 메신저에서 신착 메시지 알림이 안떠요

Agent: [단계 1/3] 환경설정>알림>"알림창"에 체크가 되어 있는지 확인해 주세요
       📌 기대 결과: 알림창에 체크가 되어있어야 합니다.
       이 단계를 확인하셨나요? 결과를 알려주세요.

사용자: 체크되어 있는데요

Agent: [단계 2/3] 윈도우 시작>설정>알림 및 작업 설정 >
       앱 및 다른 보낸 사람의 알림 받기가 켬 상태여야 합니다.
       📌 기대 결과: 켬 상태
       이 단계를 확인하셨나요?

사용자: 그것도 켬으로 되어 있어요

Agent: 불편을 드려 죄송합니다. 담당 부서의 확인이 필요한 상황인 것 같습니다.
       현재까지의 문의 내용으로 문의를 등록하시겠습니까?

사용자: 네 등록해주세요

Agent: 아래 내용으로 문의를 등록하였습니다.
       문의 번호: a3f2b5c1
       제목: 메신저 신착 알림 미작동
       답변이 등록되면 이메일로 알려드리겠습니다.
```

## 🏗️ 아키텍처

### LangGraph 워크플로우

```
사용자 입력
  → 초기화
  → RAG 검색 (벡터 스토어)
  → 답변 계획 (LLM)
  → 단계별 응답
  → [Human-in-the-Loop] 사용자 응답 대기
  → 상태 평가 (LLM)
  → 분기:
     ├─ 해결됨 → 종료
     ├─ 다음 단계 → 응답 반복
     └─ 에스컬레이션 → 티켓 생성 → 알림 → 종료
```

### 7개 핵심 노드

1. **Initialize**: 세션 초기화, 상태 설정
2. **Search Knowledge**: Chroma 벡터 검색 (BGE-M3-Korean 임베딩)
3. **Plan Response**: LLM 기반 단계별 해결방법 생성
4. **Respond Step**: 현재 단계 안내
5. **Evaluate Status**: 해결 여부 판단 및 라우팅
6. **Create Ticket**: 대화 요약 및 티켓 생성
7. **Send Notification**: 이메일/푸시 알림 발송

## 🛠️ 기술 스택

### PoC 버전 (현재)
- **프레임워크**: LangGraph (LangChain)
- **LLM**: 🚀 **Ollama Gemma2 27b** (로컬 LLM)
- **벡터 DB**: Chroma
- **임베딩**: 🇰🇷 **Ollama BGE-M3-Korean** (한글 최적화)
- **상태 관리**: SQLite Checkpointer
- **인터페이스**: 🌐 **Streamlit WebUI** (실시간 채팅)
- **FAQ 데이터**: 1000개 구조화된 데이터 (증상/원인/임시조치)
- **진행 상태**: 실시간 Progress Bar

### 프로덕션 고려 사항
- **프레임워크**: Microsoft Agent Framework
- **벡터 DB**: Azure AI Search (하이브리드 검색)
- **임베딩**: Azure OpenAI Embeddings (다국어 지원)
- **데이터베이스**: PostgreSQL/CosmosDB
- **배포**: Azure AI Foundry
- **모니터링**: OpenTelemetry + Azure Application Insights
- **검색 고도화**: Re-ranking, Query Expansion, 메타데이터 필터링

## 📚 문서

### 설계 문서
- [LangGraph PoC 상세 설계](./customer-support-chatbot-langgraph-design.md)
  - 전체 아키텍처 설계 (Ollama + Streamlit)
  - 데이터 모델 정의 (증상/원인/임시조치 구조)
  - 노드별 상세 구현 가이드
  - Human-in-the-Loop 구현 방법
  - 실시간 진행 상태 표시
  - 구현 로드맵 (7-9일)

- [사용자 시나리오 및 워크플로우](./user-scenario-workflow.md) ⭐ **NEW**
  - 상세 사용 시나리오 (문제 해결 / 티켓 생성)
  - 전체 프로세스 다이어그램
  - FAQ 데이터 구조 예시 (1000개 게시글 기준)
  - WebUI 상태 표시 구현 예시

### 참고 문서
- [Microsoft Agent Framework 상세 가이드](./microsoft-agent-framework-detailed.md)
  - MS Agent Framework 개요
  - AutoGen과의 비교
  - 프로덕션 전환 가이드

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.8+
- **Ollama 설치** (https://ollama.ai)
- 8GB+ RAM (Gemma2 27b 실행용)

### 1. Ollama 설치 및 모델 다운로드

```bash
# Ollama 설치 (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: https://ollama.ai/download 에서 다운로드

# 필요한 모델 다운로드 (~15GB)
ollama pull gemma2:27b          # LLM 모델 (~13GB)
ollama pull bge-m3-korean       # 한글 임베딩 모델 (~1.2GB)

# 모델 확인
ollama list
```

### 2. 프로젝트 설치

```bash
# 레포지토리 클론
git clone https://github.com/laurus-kpa007/agent-customer-support-chatbot.git
cd agent-customer-support-chatbot

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 확인 (.env 파일이 이미 포함되어 있습니다)
# 필요시 Ollama URL 수정: OLLAMA_BASE_URL=http://localhost:11434
```

### 3. 데이터 준비 및 벡터 스토어 구축

```bash
# Chroma 벡터 스토어 구축 (샘플 FAQ 20개 포함)
python scripts/build_vectorstore.py

# 청킹 품질 검증
python scripts/validate_chunking.py

# ✅ 벡터 스토어가 data/vectorstore에 생성됩니다
```

### 4. Streamlit WebUI 실행

```bash
# WebUI 실행
streamlit run src/ui/app.py

# 브라우저에서 자동으로 열립니다
# http://localhost:8501
```

### 5. 사용 방법

1. WebUI가 열리면 채팅 입력창에 질문 입력
2. 실시간 진행 상태 확인 (검색 중, 답변 준비 중 등)
3. 단계별 해결 방법 확인 및 응답
4. 미해결 시 티켓 자동 생성

**예시 질문**:
- "메신저에서 알림이 안와요"
- "로그인이 안돼요"
- "파일 업로드가 안됩니다"

## 📂 프로젝트 구조 (예정)

```
customer-support-chatbot-poc/
├── README.md                       # 이 파일
├── requirements.txt                # Python 의존성
├── .env.example                    # 환경 변수 템플릿
│
├── docs/                           # 문서
│   ├── customer-support-chatbot-langgraph-design.md
│   └── microsoft-agent-framework-detailed.md
│
├── data/                           # 데이터
│   ├── sample_faq.json            # 샘플 FAQ
│   ├── vectorstore/               # Chroma 벡터 스토어
│   └── tickets/                   # 생성된 티켓들
│
├── src/                           # 소스 코드
│   ├── models/                    # 데이터 모델
│   ├── nodes/                     # LangGraph 노드
│   ├── graph/                     # 워크플로우 정의
│   ├── services/                  # 서비스 레이어
│   └── utils/                     # 유틸리티
│
├── scripts/                       # 스크립트
│   ├── prepare_data.py           # 데이터 준비
│   └── build_vectorstore.py      # 벡터 스토어 구축
│
└── main.py                        # CLI 실행 파일
```

## 🗓️ 개발 로드맵

### Phase 1: 기반 구축 (1일)
- [x] 프로젝트 설계 완료
- [ ] 샘플 FAQ 데이터 생성 (20-30개)
- [ ] 벡터 스토어 구축

### Phase 2: 노드 구현 (2-3일)
- [ ] 7개 핵심 노드 구현
- [ ] 단위 테스트 작성

### Phase 3: 워크플로우 통합 (2일)
- [ ] LangGraph StateGraph 구성
- [ ] Human-in-the-Loop 인터럽트 설정
- [ ] 조건부 라우팅 구현

### Phase 4: 인터페이스 (1일)
- [ ] CLI 챗봇 구현
- [ ] 대화 히스토리 표시

### Phase 5: 테스트 및 검증 (1-2일)
- [ ] 통합 테스트
- [ ] 성능 측정
- [ ] 문서화

**총 예상 기간**: 7-9일

## 🎯 PoC 성공 기준

1. ✅ 사용자 질의에 대한 FAQ 검색 성공률 > 70%
2. ✅ 3단계 이내 단계별 답변 제공
3. ✅ 대화 컨텍스트 유지 및 이해
4. ✅ 미해결 시 티켓 자동 생성
5. ✅ 전체 워크플로우 정상 동작

## 📊 프로덕션 전환 계획

PoC 검증 후 다음 단계로 전환:

1. **Microsoft Agent Framework 마이그레이션**
   - LangGraph → MS Agent Framework
   - 엔터프라이즈 기능 추가 (모니터링, 보안 등)

2. **검색 고도화**
   - 하이브리드 검색 (벡터 + 키워드)
   - Re-ranking 모델 적용
   - Query Expansion (쿼리 확장)
   - 메타데이터 필터링 강화

3. **웹 크롤링 자동화**
   - 실제 FAQ/Q&A 게시판 크롤링
   - 주기적 업데이트 스케줄링
   - 증분 인덱싱 (변경된 문서만 업데이트)

4. **프로덕션 인프라**
   - Azure AI Foundry 배포
   - 웹 UI 개발 (React + WebSocket)
   - 실제 게시판 API 연동
   - 이메일 발송 시스템 구축

## 🤝 기여

이 프로젝트는 고객지원 자동화를 위한 PoC입니다. 개선 제안이나 버그 리포트는 이슈로 등록해주세요.

## 📄 라이선스

MIT License

## 📧 문의

프로젝트 관련 문의: [GitHub Issues](https://github.com/laurus-kpa007/-customer-support-chatbot/issues)

---

**현재 상태**: 설계 완료, 구현 준비 중
**최종 업데이트**: 2025-11-18
