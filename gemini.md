# Briefly Gemini API Integration Guide

본 문서는 Briefly 뉴스 요약 대시보드 프로젝트에서 주력 AI 엔진(Groq) 외에, 대안 엔진(Alternative Engine)으로 Google Gemini API를 통합하여 다중 모델 요약 환경을 구축하기 위한 아키텍처 설계 및 연동 가이드라인입니다.

---

## 1. 대상 모델 및 강점
향후 엔진 교체 또는 병용 시 다음 모델의 적용을 권장합니다.
* **`gemini-2.5-flash` (추천)**
  * 뛰어난 가성비와 초고속 응답 스펙을 보유하여 다량의 실시간 뉴스 RSS 요약 처리에 최적화되어 있습니다.
  * 대용량 컨텍스트 윈도우(Context Window)를 활용해 카테고리 전체 뉴스를 단 한 번의 프롬프트 호출로 묶음 요약(Batch Summary)하는 고도화가 가능합니다.
* **`gemini-2.5-pro`**
  * 고성능 추론 모델로, 복잡한 국제정세나 IT 전문 기술 기사의 심층 오피니언 분석 요약이 필요할 때 선택적으로 사용합니다.

---

## 2. Gemini API 연동 코드 아키텍처
최신 `google-genai` SDK 패키지를 기준으로 연동 인터페이스를 설계합니다.

### A. 의존성 추가 (`requirements.txt`)
Gemini API 연동을 위해 다음 패키지를 설치해야 합니다.
```text
google-genai
```

### B. 요약 함수 구현 구조 (Python 예시)
`summarizer.py` 구조를 계승하여 Gemini 클라이언트로 전환 시 사용 가능한 표준 연동 컴포넌트 구조입니다.
```python
import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiSummarizer:
    def __init__(self, model_name="gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY가 설정되어 있지 않습니다.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def summarize(self, title, content):
        if not self.client:
            return "API 키가 없어 요약을 생성할 수 없습니다."

        system_instruction = """[Task] 뉴스 요약 전문가
[Constraint]
1. 출력은 반드시 3개 이내의 불렛 포인트(•)로 구성할 것.
2. '...함', '...임' 등의 명사형 종결 어미만 사용할 것.
3. 메타 텍스트 및 사족을 일절 금지함.
4. 고유명사는 표준 한국어로 표기할 것.
[Format]
• 요약 내용 1
• 요약 내용 2
• 요약 내용 3"""

        user_content = f"제목: {title}\n본문: {content}"

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                    max_output_tokens=500
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API 호출 실패: {e}")
            return "요약 생성 불가"
```

---

## 3. 다중 AI 엔진 예외 처리 설계 (Failover)
Groq API 호출 제한(Rate Limit)이나 네트워크 타임아웃 장애가 발생할 경우를 대비하여, 주력 엔진 실패 시 Gemini API를 예비 엔진으로 활용하는 이중화 전략(Failover)을 적용할 수 있습니다.
* **기본 흐름**: Groq API 호출 시도
* **예외 처리**: Groq API 호출 3회 연속 실패 시, 예비 모델(`gemini-2.5-flash`)로 요약 스위칭 가동 및 경고 로그 전송.
