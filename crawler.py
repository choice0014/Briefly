import feedparser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCrawler:
    def __init__(self, feed_urls):
        """
        feed_urls: dict with categories as keys and list of RSS URLs as values
        e.g., {'Tech': ['url1', 'url2'], 'Politics': ['url3']}
        """
        self.feed_urls = feed_urls

    def fetch_news(self, limit_per_feed=5):
        all_news = {}
        
        for category, urls in self.feed_urls.items():
            logger.info(f"Fetching news for category: {category}")
            category_articles = []
            
            for url in urls:
                try:
                    feed = feedparser.parse(url)
                    articles = feed.entries[:limit_per_feed]
                    
                    for entry in articles:
                        article = {
                            'title': entry.get('title', 'No Title'),
                            'link': entry.get('link', ''),
                            'summary': entry.get('summary', entry.get('description', '')),
                            'published': entry.get('published', ''),
                            'source': feed.feed.get('title', url)
                        }
                        category_articles.append(article)
                except Exception as e:
                    logger.error(f"Error fetching from {url}: {e}")
            
            all_news[category] = category_articles
            
        return all_news

if __name__ == "__main__":
    # Test
    feeds = {
        'Tech': ['https://techcrunch.com/feed/'],
        'Politics': ['https://feeds.bbci.co.uk/news/politics/rss.xml']
    }
    crawler = NewsCrawler(feeds)
    news = crawler.fetch_news(limit_per_feed=2)
    for cat, articles in news.items():
        print(f"\n--- {cat} ---")
        for a in articles:
            print(f"- {a['title']} ({a['source']})")
