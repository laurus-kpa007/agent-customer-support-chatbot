# 에이전트의 "인간적인" 행동 개선

이 작업의 목표는 로봇 같은 하드코딩된 응답을 동적이고 문맥을 고려한 LLM 생성 응답으로 대체하여, 고객 지원 에이전트를 더 인간 상담원처럼 만드는 것입니다. 이는 "Human in the Loop" 측면을 강화하여 상호작용을 더 부드럽고 매끄럽게 만드는 데 중점을 둡니다.

## 사용자 검토 필요 사항

> [!NOTE]
> 응답 생성에는 설정된 Ollama 모델(기본값: `gemma2:27b`)을 사용할 것입니다. 이는 정적 문자열을 사용하는 것보다 지연 시간이 약간 증가할 수 있지만, 사용자 경험을 크게 향상시킬 것입니다.

## 변경 제안

### `src/nodes`

#### [MODIFY] [handle_small_talk.py](file:///d:/Python/agent-customer-support-chatbot/src/nodes/handle_small_talk.py)
- 하드코딩된 `response_text`를 LLM 호출로 대체합니다.
- LLM에게 도움이 되고 친절하며 전문적인 고객 지원 상담원처럼 행동하도록 지시하는 프롬프트를 사용합니다.
- 응답은 사용자의 입력을 인정하고 적절한 경우 기술 지원 주제로 부드럽게 안내해야 합니다.

#### [MODIFY] [respond_step.py](file:///d:/Python/agent-customer-support-chatbot/src/nodes/respond_step.py)
- 템플릿 기반의 `response_text`를 LLM 호출로 대체합니다.
- 현재 단계의 `action`(조치), `description`(설명), `expected_result`(기대 결과)를 가져와 대화체로 제시하는 프롬프트를 사용합니다.
- 에이전트는 격려하는 어조를 사용해야 하며, 진행하기 위해 사용자의 피드백(Human-in-the-Loop)을 명시적으로 요청해야 합니다.

## 검증 계획

기존 테스트 스크립트를 사용하여 변경 사항을 검증할 것입니다.

### 자동화 테스트
- `python test_scenarios.py` 실행: 스몰톡 시나리오를 테스트합니다. 출력을 수동으로 검사하여 응답이 다양하고 인간적인지 확인할 것입니다.
- `python test_conversation_flow.py` 실행: 멀티턴 대화와 단계별 문제 해결 과정을 테스트합니다. 단계가 명확하고 대화체로 제시되는지 확인할 것입니다.

### 수동 검증
- 테스트 스크립트에서 생성된 로그를 검토하여 에이전트가 페르소나를 유지하고 대화 흐름을 올바르게 처리하는지 확인할 것입니다.
