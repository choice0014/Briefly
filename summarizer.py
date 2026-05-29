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
        Groq Llama-3 모델을 사용하여 고품질 한국어 요약을 수행합니다.
        """
        if not self.client:
            return "API 키가 없어 요약을 생성할 수 없습니다."

        if not content or len(content.strip()) < 10:
            content = f"기사 제목 '{title}'에 대한 관련 내용을 바탕으로 핵심 뉴스를 설명해 주세요."

        prompt = f"""
        당신은 한국의 베테랑 뉴스 편집자입니다. 아래 정보를 바탕으로 독자가 이해하기 쉽게 현대적인 한국어로 요약하세요.
        
        정보:
        - 기사 제목: {title}
        - 기사 본문: {content}
        
        [엄격한 준수 사항]
        1. **고유명사 정확도**: 'Nintendo'는 '닌텐도', 'Microsoft'는 '마이크로소프트' 등 정확한 한국어 명칭을 사용하세요.
        2. **한자어 제한**: '巨企' 등 일본식/중국식 한자어 대신 '빅테크', '대기업' 등 쉬운 한국어를 사용하세요.
        3. **형식**: 반드시 3개 이내의 불렛 포인트(•)로 요약하세요.
        4. **문체**: '...함', '...임'과 같은 명사형 종결 어미를 사용하세요.
        5. **순수 요약**: 다른 설명 없이 오직 불렛 포인트만 출력하세요. 정보가 부족하다면 제목을 바탕으로 예상되는 핵심 내용을 작성하세요.
        
        요약 결과:
        """
        
        for attempt in range(retries + 1):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=500
                )
                response = completion.choices[0].message.content
                if response:
                    return response.strip()
            except Exception as e:
                logger.error(f"Groq 요약 시도 {attempt+1} 실패: {e}")
                time.sleep(1)
        
        return "뉴스 내용을 분석하여 요약을 생성할 수 없습니다."

    def summarize_batch(self, articles):
        summaries = []
        for art in articles:
            summaries.append(self.summarize(art['title'], art['summary']))
        return summaries

if __name__ == "__main__":
    # 테스트 실행
    summarizer = NewsSummarizer()
    print(summarizer.summarize("테스트 뉴스", "이것은 Groq API를 이용한 한국어 요약 테스트입니다."))
