# 🚀 고객지원 챗봇 로컬 설치 및 실행 가이드

이 가이드는 처음부터 끝까지 로컬 환경에서 고객지원 챗봇을 설치하고 실행하는 모든 단계를 상세히 설명합니다.

## 📋 목차

1. [시스템 요구사항](#시스템-요구사항)
2. [Step 1: Ollama 설치](#step-1-ollama-설치)
3. [Step 2: 모델 다운로드](#step-2-모델-다운로드)
4. [Step 3: 프로젝트 클론](#step-3-프로젝트-클론)
5. [Step 4: Python 환경 설정](#step-4-python-환경-설정)
6. [Step 5: 데이터 임베딩 (벡터 스토어 구축)](#step-5-데이터-임베딩-벡터-스토어-구축)
7. [Step 6: 챗봇 실행](#step-6-챗봇-실행)
8. [Step 7: 사용 방법](#step-7-사용-방법)
9. [문제 해결](#문제-해결)

---

## 시스템 요구사항

### 필수 사항
- **운영체제**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: 3.8 이상
- **RAM**: 최소 8GB (16GB 권장)
- **디스크 공간**: 20GB 이상 (모델 저장용)
- **인터넷 연결**: 모델 다운로드 시 필요 (~15GB)

### 권장 사양
- **CPU**: 4코어 이상
- **RAM**: 16GB 이상
- **GPU**: 선택사항 (GPU 가속 지원)

---

## Step 1: Ollama 설치

Ollama는 로컬에서 LLM을 실행할 수 있게 해주는 도구입니다.

### Windows

1. **Ollama 다운로드**
   - 브라우저에서 https://ollama.ai/download 접속
   - "Download for Windows" 클릭
   - `OllamaSetup.exe` 다운로드

2. **설치 실행**
   - 다운로드한 `OllamaSetup.exe` 더블클릭
   - 설치 마법사 따라 진행
   - "Install" 클릭

3. **설치 확인**
   ```cmd
   # 명령 프롬프트(cmd) 또는 PowerShell 열기
   ollama --version
   ```

   **예상 출력**:
   ```
   ollama version is 0.x.x
   ```

### macOS

1. **Homebrew 방식 (권장)**
   ```bash
   # 터미널 열기 (Cmd + Space, "Terminal" 검색)

   # Homebrew가 없다면 먼저 설치
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

   # Ollama 설치
   brew install ollama
   ```

2. **또는 직접 다운로드**
   ```bash
   # 설치 스크립트 실행
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **설치 확인**
   ```bash
   ollama --version
   ```

### Linux (Ubuntu/Debian)

```bash
# 터미널 열기

# Ollama 설치
curl -fsSL https://ollama.ai/install.sh | sh

# 설치 확인
ollama --version
```

### Ollama 서버 시작

설치 후 Ollama 서버를 시작합니다.

```bash
# Ollama 서버 시작
ollama serve
```

**중요**: 이 명령어는 백그라운드에서 계속 실행되어야 합니다. 새 터미널 창을 열어서 다음 단계를 진행하세요.

**Windows**에서는 설치 시 자동으로 서비스로 등록되므로 `ollama serve` 명령을 실행할 필요가 없습니다.

---

## Step 2: 모델 다운로드

### 1. LLM 모델 다운로드 (Gemma2 27b)

**새 터미널 창**을 열고 실행:

```bash
ollama pull gemma2:27b
```

**진행 상황**:
```
pulling manifest
pulling 8934d96d3f08... 100% ▕████████████████▏ 15.0 GB
pulling 097a36493f71... 100% ▕████████████████▏  8.4 KB
pulling 109037bec39c... 100% ▕████████████████▏  136 B
pulling 22a838ceb7fb... 100% ▕████████████████▏   84 B
pulling 887433b89a90... 100% ▕████████████████▏  483 B
verifying sha256 digest
writing manifest
removing any unused layers
success
```

**소요 시간**: 인터넷 속도에 따라 10~30분 소요 (약 15GB)

### 2. 임베딩 모델 다운로드 (BGE-M3-Korean)

```bash
ollama pull bge-m3-korean
```

**진행 상황**:
```
pulling manifest
pulling 8667b8b7c4d3... 100% ▕████████████████▏ 1.2 GB
...
success
```

**소요 시간**: 약 3~5분 (약 1.2GB)

### 3. 모델 확인

```bash
ollama list
```

**예상 출력**:
```
NAME                ID              SIZE      MODIFIED
gemma2:27b          8934d96d3f08    15 GB     2 minutes ago
bge-m3-korean       8667b8b7c4d3    1.2 GB    1 minute ago
```

### 4. 모델 테스트

LLM 모델이 정상 작동하는지 확인:

```bash
ollama run gemma2:27b "안녕하세요"
```

**예상 출력**:
```
안녕하세요! 무엇을 도와드릴까요?
```

`Ctrl + D` 또는 `/bye`로 종료

---

## Step 3: 프로젝트 클론

### 1. Git이 설치되어 있는지 확인

```bash
git --version
```

Git이 없다면:
- **Windows**: https://git-scm.com/download/win
- **macOS**: `brew install git`
- **Linux**: `sudo apt-get install git`

### 2. 프로젝트 클론

```bash
# 원하는 디렉토리로 이동 (예: 홈 디렉토리)
cd ~

# 또는 Windows에서
# cd C:\Users\YourName\Documents

# 프로젝트 클론
git clone https://github.com/laurus-kpa007/agent-customer-support-chatbot.git

# 프로젝트 디렉토리로 이동
cd agent-customer-support-chatbot
```

### 3. 프로젝트 구조 확인

```bash
# Windows
dir

# macOS/Linux
ls -la
```

**예상 출력**:
```
data/
docs/
scripts/
src/
.env
.gitignore
README.md
requirements.txt
...
```

---

## Step 4: Python 환경 설정

### 1. Python 버전 확인

```bash
python --version
# 또는
python3 --version
```

**필수**: Python 3.8 이상

Python이 없거나 버전이 낮다면:
- **Windows**: https://www.python.org/downloads/
- **macOS**: `brew install python@3.11`
- **Linux**: `sudo apt-get install python3.11`

### 2. 가상환경 생성

```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

**진행 상황**:
```
Creating virtual environment...
Done.
```

### 3. 가상환경 활성화

```bash
# Windows (CMD)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

**성공 시**: 프롬프트 앞에 `(venv)` 표시됨
```
(venv) C:\...\agent-customer-support-chatbot>
```

### 4. pip 업그레이드

```bash
pip install --upgrade pip
```

### 5. 의존성 설치

```bash
pip install -r requirements.txt
```

**진행 상황**:
```
Collecting langchain==0.1.20
  Downloading langchain-0.1.20-py3-none-any.whl (...)
Collecting langgraph==0.0.55
  Downloading langgraph-0.0.55-py3-none-any.whl (...)
...
Installing collected packages: ...
Successfully installed langchain-0.1.20 langgraph-0.0.55 ...
```

**소요 시간**: 5~10분

### 6. 설치 확인

```bash
pip list | grep langchain
```

**예상 출력**:
```
langchain              0.1.20
langchain-community    0.0.38
langchain-core         0.1.52
langchain-ollama       0.1.0
```

---

## Step 5: 데이터 임베딩 (벡터 스토어 구축)

이 단계가 **가장 중요**합니다! FAQ 데이터를 벡터화하여 Chroma DB에 저장합니다.

### 1. Ollama 서버 확인

먼저 Ollama가 실행 중인지 확인:

```bash
# 다른 터미널 창에서 Ollama가 실행 중이어야 함
# 확인 방법:
curl http://localhost:11434
```

**예상 출력**:
```
Ollama is running
```

만약 연결 안 되면:
```bash
# 새 터미널에서
ollama serve
```

### 2. 환경 변수 확인

`.env` 파일이 올바른지 확인:

```bash
# Windows
type .env

# macOS/Linux
cat .env
```

**내용 확인**:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=gemma2:27b
OLLAMA_EMBEDDING_MODEL=bge-m3-korean
DATA_DIR=./data
VECTORSTORE_PATH=./data/vectorstore
TICKETS_PATH=./data/tickets
```

URL이 다르다면 `.env` 파일 수정:
```bash
# Windows
notepad .env

# macOS/Linux
nano .env
```

### 3. 벡터 스토어 구축 실행

```bash
python scripts/build_vectorstore.py
```

**진행 상황 (예상 출력)**:
```
============================================================
  FAQ 벡터 스토어 구축 스크립트
  - 전략: 문서 전체 청킹 (해결 방법 완전 보존)
  - 벡터 DB: Chroma
  - 임베딩: Ollama BGE-M3-Korean
============================================================

📚 FAQ 데이터 로드 중... (data/faq_sample.json)
✅ 20개 FAQ 로드 완료

📄 Document 객체 생성 중...
✅ 20개 Document 생성 완료
   - 평균 길이: 1247자
   - 최대 길이: 2103자
   - 최소 길이: 876자

🔄 Ollama 임베딩 모델 로드 중...
   - 모델: bge-m3-korean
✅ BGE-M3-Korean 임베딩 모델 로드 완료

🗄️  Chroma 벡터 스토어 구축 중...
   - 저장 경로: data/vectorstore
   - 문서 수: 20개
   - 임베딩 진행 중... (수 분 소요될 수 있습니다)
✅ 벡터 스토어 구축 완료

🔍 테스트 검색 수행 중...

📌 쿼리: 메신저에서 알림이 안떠요

   [1] 신착 메시지 알림이 표시되지 않음
       카테고리: 메신저
       ID: FAQ-001
       내용: 제목: 신착 메시지 알림이 표시되지 않음
카테고리: 메신저

증상:
메신저에서 새로운 메시지를 받아도 알림창이...

   [2] 알림음이 들리지 않음
       카테고리: 알림
       ID: FAQ-006
       내용: 제목: 알림음이 들리지 않음
카테고리: 알림
...

============================================================
✅ 벡터 스토어 구축 완료!
============================================================

저장 위치: /path/to/data/vectorstore

이제 챗봇을 실행할 수 있습니다:
  streamlit run src/ui/app.py
```

**소요 시간**:
- 20개 FAQ: 약 2~5분
- 1000개 FAQ: 약 20~30분 (실제 운영 시)

### 4. 벡터 스토어 확인

생성된 파일 확인:

```bash
# Windows
dir data\vectorstore

# macOS/Linux
ls -la data/vectorstore
```

**예상 출력**:
```
chroma.sqlite3
<기타 Chroma 데이터베이스 파일들>
```

### 5. 청킹 품질 검증 (선택사항)

벡터 스토어가 제대로 구축되었는지 검증:

```bash
python scripts/validate_chunking.py
```

**예상 출력**:
```
============================================================
  청킹 품질 검증
  - 각 FAQ의 해결 방법이 완전한지 확인합니다
============================================================

📂 벡터 스토어 로드 중...
✅ 벡터 스토어 로드 완료

🔍 청킹 완전성 검증 중...

쿼리: 메신저 알림 설정
  - 문서 ID: FAQ-001
  - 제목: 신착 메시지 알림이 표시되지 않음
  - 발견된 방법 수: 3
  - 완전한 방법 수: 3
  ✅ 모든 해결 방법이 완전함

쿼리: 로그인 비밀번호 오류
  - 문서 ID: FAQ-002
  - 제목: 비밀번호를 잊어버렸을 때
  - 발견된 방법 수: 2
  - 완전한 방법 수: 2
  ✅ 모든 해결 방법이 완전함

...

============================================================
검증 결과: 5/5 테스트 통과
✅ 모든 FAQ 문서의 해결 방법이 완전합니다!
============================================================
```

---

## Step 6: 챗봇 실행

### 1. Streamlit WebUI 실행

```bash
streamlit run src/ui/app.py
```

**예상 출력**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 2. 브라우저 자동 열림

- 자동으로 브라우저가 열리고 `http://localhost:8501` 접속
- 자동으로 열리지 않으면 직접 브라우저에서 해당 URL 입력

### 3. 챗봇 UI 확인

화면에 다음이 표시되어야 함:
- 🤖 **고객지원 챗봇** 제목
- 좌측 사이드바: 사용 방법 및 세션 정보
- 채팅 입력창: "무엇을 도와드릴까요?"

---

## Step 7: 사용 방법

### 예제 대화 1: 문제 해결 성공

**사용자 입력**:
```
메신저에서 알림이 안떠요
```

**AI 응답**:
```
[단계 1/3] 메신저 알림 설정 확인

📝 환경설정 메뉴를 열고, 알림 탭을 선택한 후,
   '알림창' 옵션에 체크되어 있는지 확인합니다.

✅ 기대 결과: 알림창에 체크가 되어있어야 합니다

---
이 단계를 확인하셨나요? 결과를 알려주세요.
(예: '해결됐어요', '안돼요', '다음 단계', '등록해주세요')
```

**사용자 입력**:
```
해결됐어요!
```

**AI 응답**:
```
🎉 문제가 해결되어 다행입니다!

추가로 도움이 필요하시면 언제든 문의해주세요. 😊
```

### 예제 대화 2: 티켓 생성

**사용자 입력**:
```
파일 업로드가 안돼요
```

**AI 응답**:
```
[단계 1/3] 파일 크기 확인

📝 업로드하려는 파일을 우클릭하고 '속성'을 선택합니다.
   파일 크기가 100MB 이하인지 확인합니다...
```

**사용자 입력**:
```
체크했는데도 안돼요
```

**AI 응답**:
```
[단계 2/3] 파일 형식 확인
...
```

**사용자 입력**:
```
이것도 했는데 안돼요. 등록해주세요
```

**AI 응답**:
```
📋 문의가 등록되었습니다

문의 번호: a3f2b5c1
제목: 파일 업로드 실패
요약: 사용자가 파일을 업로드하려 했으나 실패함

담당자가 확인 후 답변을 드리겠습니다.
답변이 등록되면 알림을 보내드리겠습니다. 📬

감사합니다! 😊
```

**터미널 출력 (알림 시뮬레이션)**:
```
============================================================
📧 이메일 발송 시뮬레이션
============================================================
To: user_user_001@example.com
Subject: [고객지원] 문의가 등록되었습니다 (#a3f2b5c1)

안녕하세요,

문의가 정상적으로 등록되었습니다.

문의번호: a3f2b5c1
등록시간: 2025-11-18 14:30:15

담당자가 확인 후 답변을 드리겠습니다.
...
============================================================

📱 푸시 알림 발송 시뮬레이션
   사용자: user_001
   메시지: 문의가 등록되었습니다 (#a3f2b5c1)
```

### 생성된 티켓 확인

```bash
# Windows
type data\tickets\ticket_a3f2b5c1.json

# macOS/Linux
cat data/tickets/ticket_a3f2b5c1.json
```

---

## 문제 해결

### 1. Ollama 연결 오류

**증상**:
```
❌ 임베딩 모델 로드 실패: Connection refused
```

**해결**:
```bash
# Ollama 서버가 실행 중인지 확인
curl http://localhost:11434

# 실행 안 되면 시작
ollama serve
```

### 2. 모델을 찾을 수 없음

**증상**:
```
Error: model 'gemma2:27b' not found
```

**해결**:
```bash
# 모델 다시 다운로드
ollama pull gemma2:27b
ollama pull bge-m3-korean

# 모델 확인
ollama list
```

### 3. Python 패키지 오류

**증상**:
```
ModuleNotFoundError: No module named 'langchain'
```

**해결**:
```bash
# 가상환경이 활성화되어 있는지 확인
# 프롬프트 앞에 (venv) 표시 확인

# 의존성 재설치
pip install -r requirements.txt
```

### 4. 포트 이미 사용 중

**증상**:
```
Error: Port 8501 is already in use
```

**해결**:
```bash
# 다른 포트 사용
streamlit run src/ui/app.py --server.port 8502
```

### 5. 메모리 부족

**증상**:
```
Killed (메모리 부족으로 프로세스 종료)
```

**해결**:
- 다른 프로그램 종료
- 더 작은 모델 사용:
  ```bash
  # .env 파일 수정
  OLLAMA_LLM_MODEL=gemma2:9b  # 27b 대신 9b
  ```

### 6. 한글 깨짐

**증상**: FAQ 데이터나 응답에서 한글이 깨져 보임

**해결**:
```bash
# Windows CMD에서 UTF-8 인코딩 설정
chcp 65001

# 또는 PowerShell 사용 권장
```

### 7. 벡터 스토어 구축 실패

**증상**:
```
❌ 벡터 스토어 구축 실패: ...
```

**해결**:
```bash
# 기존 벡터 스토어 삭제 후 재구축
rm -rf data/vectorstore  # macOS/Linux
rmdir /s data\vectorstore  # Windows

# 재구축
python scripts/build_vectorstore.py
```

### 8. Streamlit 캐시 문제

**증상**: 코드 수정했는데 변경사항이 반영 안 됨

**해결**:
```bash
# Streamlit 캐시 삭제
streamlit cache clear

# 또는 브라우저에서 'c' 키 누르고 "Clear cache" 선택
```

---

## 추가 팁

### 1. 백그라운드 실행 (Linux/macOS)

Ollama를 백그라운드에서 실행:
```bash
# 백그라운드 실행
nohup ollama serve > ollama.log 2>&1 &

# 확인
tail -f ollama.log
```

### 2. 로그 확인

Streamlit 로그:
```bash
streamlit run src/ui/app.py --logger.level debug
```

### 3. 데이터 업데이트

FAQ 데이터를 수정한 후:
```bash
# 벡터 스토어 재구축 (기존 것 자동 덮어쓰기)
python scripts/build_vectorstore.py
```

### 4. 세션 리셋

채팅 기록 초기화:
- WebUI 사이드바의 "🔄 새 대화 시작" 버튼 클릭
- 또는 브라우저 새로고침

### 5. 성능 최적화

더 빠른 응답을 원한다면:
```env
# .env 파일 수정
OLLAMA_LLM_MODEL=gemma2:9b  # 더 작은 모델 (더 빠름)
```

---

## 다음 단계

### 실제 FAQ 데이터 추가

1. `data/faq_sample.json` 파일을 수정하거나 새 FAQ 추가
2. 벡터 스토어 재구축: `python scripts/build_vectorstore.py`
3. 챗봇 실행

### 프로덕션 배포

- [프로덕션 배포 가이드](./DEPLOYMENT_GUIDE.md) 참조 (추후 작성)
- Azure AI Foundry 또는 AWS 배포
- Microsoft Agent Framework 전환

---

## 도움 받기

- **GitHub Issues**: https://github.com/laurus-kpa007/agent-customer-support-chatbot/issues
- **문서**: [README.md](./README.md), [설계 문서](./customer-support-chatbot-langgraph-design.md)

---

**축하합니다! 🎉**

이제 로컬에서 완전히 작동하는 고객지원 챗봇을 사용할 수 있습니다!
