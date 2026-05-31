import os
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from crawler import NewsCrawler
from summarizer import NewsSummarizer
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    # 1. 설정 로드
    FEEDS = {
        'Tech': os.getenv("TECH_FEEDS", "https://techcrunch.com/feed/").split(','),
        'Politics': os.getenv("POLITICS_FEEDS", "https://feeds.bbci.co.uk/news/politics/rss.xml").split(','),
        'International': os.getenv("INTL_FEEDS", "https://feeds.bbci.co.uk/news/world/rss.xml").split(',')
    }
    
    # GitHub Actions 환경인지 확인 (CI 환경이면 더 많은 기사 수집 가능)
    limit = int(os.getenv("NEWS_LIMIT", 5))

    # 2. 뉴스 수집
    logger.info("뉴스 수집 시작...")
    crawler = NewsCrawler(FEEDS)
    raw_news = crawler.fetch_news(limit_per_feed=limit)

    # 3. AI 요약 (Groq 사용)
    logger.info("Groq AI 요약 시작...")
    summarizer = NewsSummarizer()
    
    final_news_data = {}
    for category, articles in raw_news.items():
        if not articles:
            final_news_data[category] = []
            continue

        logger.info(f"{category} 요약 중...")
        summarized_results = summarizer.summarize_batch(articles)
        
        for i, article in enumerate(articles):
            if i < len(summarized_results):
                result = summarized_results[i]
                article['title'] = result['translated_title']
                article['ai_summary'] = result['summary']
            else:
                article['ai_summary'] = "요약 생성 중 오류 발생"
            
        final_news_data[category] = articles

    # 4. HTML 대시보드 생성 및 백업 (index.html로 저장하여 GitHub Pages에서 사용)
    generated_at_dt = datetime.now()
    generated_at = generated_at_dt.strftime("%Y-%m-%d %H:%M:%S")

    if os.path.exists('index.html'):
        import shutil
        backup_dir = 'history'
        os.makedirs(backup_dir, exist_ok=True)
        # 기존 index.html의 실제 생성 시각을 파일명으로 활용 (더 정확한 이력 관리)
        backup_filename = f"index_{generated_at_dt.strftime('%Y%m%d_%H%M%S')}.html"
        backup_path = os.path.join(backup_dir, backup_filename)
        shutil.copy2('index.html', backup_path)
        logger.info(f"기존 index.html을 {backup_path}로 백업했습니다.")

    logger.info("index.html 생성 중...")
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('dashboard.html')
    
    output_html = template.render(
        news_data=final_news_data,
        generated_at=generated_at
    )

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(output_html)

    logger.info("작업 완료! index.html이 업데이트되었습니다.")

if __name__ == "__main__":
    main()
