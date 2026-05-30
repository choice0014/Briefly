import os
import logging
import time
import re
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
            logger.warning("GROQ_API_KEY가 설정되어 있지 않습니다.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            
        self.model_name = model_name
        logger.info(f"Groq 모델 초기화 완료: {model_name}")

    def summarize(self, title, content, retries=2):
        """
        Groq API를 사용하여 제목 번역 및 3줄 요약을 수행합니다.
        """
        if not self.client:
            return title, "API 키가 없어 요약을 생성할 수 없습니다."

        if not content or len(content.strip()) < 10:
            content = f"기사 제목 '{title}'"

        system_prompt = """[Task] 뉴스 요약 및 번역 전문가
[Constraint]
1. 입력된 제목을 자연스러운 한국어로 번역할 것.
2. 본문 내용을 바탕으로 반드시 3개 이내의 불렛 포인트(•) 요약을 작성할 것.
3. '...함', '...임' 등의 명사형 종결 어미만 사용할 것.
4. 한자(漢字) 사용을 엄격히 금지하며, 순수 현대 한국어로만 작성할 것.
5. "요약 결과", "참고" 등 모든 사족을 금지함.
[Format]
Title: [번역된 제목]
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
                    temperature=0.1,
                    max_tokens=800
                )
                response = completion.choices[0].message.content
                if response:
                    # 제목과 요약 분리
                    translated_title = title
                    title_match = re.search(r'Title:\s*(.*)', response)
                    if title_match:
                        translated_title = title_match.group(1).strip()
                    
                    summaries = [line.strip() for line in response.strip().split('\n') if line.strip().startswith('•')]
                    summary_text = '\n'.join(summaries) if summaries else response.strip()
                    
                    return translated_title, summary_text
            except Exception as e:
                logger.error(f"Groq 요약 시도 {attempt+1} 실패: {e}")
                time.sleep(1)
        
        return title, "요약 생성 불가"

    def summarize_batch(self, articles):
        results = []
        for art in articles:
            translated_title, summary = self.summarize(art['title'], art['summary'])
            results.append({
                'translated_title': translated_title,
                'summary': summary
            })
        return results

if __name__ == "__main__":
    # 테스트 실행
    summarizer = NewsSummarizer()
    t, s = summarizer.summarize("Test News", "This is a test news article about AI translation.")
    print(f"Title: {t}\nSummary:\n{s}")
