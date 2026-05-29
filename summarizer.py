import os
import logging
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class NewsSummarizer:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        """
        Groq API를 사용하여 무료로 고성능 요약을 수행합니다.
        GitHub Actions에서도 동작할 수 있도록 설계되었습니다.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            # 로컬 실행 시에는 에러를 내지만, GitHub Actions에서는 Secrets로 전달될 예정입니다.
            logger.warning("GROQ_API_KEY가 설정되어 있지 않습니다.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            
        self.model_name = model_name
        logger.info(f"Groq 모델 초기화 완료: {model_name}")

    def summarize(self, title, content, retries=2):
        """
        Groq API를 사용하여 사족 없는 순수 불렛 포인트 요약을 수행합니다.
        """
        if not self.client:
            return "API 키가 없어 요약을 생성할 수 없습니다."

        if not content or len(content.strip()) < 10:
            content = f"기사 제목 '{title}'"

        system_prompt = """[Task] 뉴스 요약 전문가
[Constraint]
1. 출력은 반드시 3개 이내의 불렛 포인트(•)로 구성할 것.
2. '...함', '...임' 등의 명사형 종결 어미만 사용할 것.
3. "요약 결과", "참고", "도움이 필요하시면" 등 모든 메타 텍스트 및 사족을 금지함.
4. 오직 요약된 내용(불렛 포인트)만 출력할 것.
5. 고유명사는 표준 한국어로 표기할 것(예: Nintendo -> 닌텐도).
[Format]
• 요약 내용 1
• 요약 내용 2
• 요약 내용 3"""

        user_input = f"제목: {title}\n본문: {content}"
        
        for attempt in range(retries + 1):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.1, # 일관성을 위해 온도를 낮춤
                    max_tokens=500
                )
                response = completion.choices[0].message.content
                if response:
                    # 혹시 모를 사족 제거 필터링
                    lines = [line.strip() for line in response.strip().split('\n') if line.strip().startswith('•')]
                    return '\n'.join(lines) if lines else response.strip()
            except Exception as e:
                logger.error(f"Groq 요약 시도 {attempt+1} 실패: {e}")
                time.sleep(1)
        
        return "요약 생성 불가"

    def summarize_batch(self, articles):
        summaries = []
        for art in articles:
            summaries.append(self.summarize(art['title'], art['summary']))
        return summaries

if __name__ == "__main__":
    # 테스트 실행
    summarizer = NewsSummarizer()
    print(summarizer.summarize("테스트 뉴스", "이것은 Groq API를 이용한 한국어 요약 테스트입니다."))
