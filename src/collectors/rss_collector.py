import feedparser
import requests
from datetime import datetime
from typing import List
import sys
import os

# パスの設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import BaseCollector, Article

class RSSCollector(BaseCollector):
    def __init__(self, config):
        super().__init__(config)
        self.sources = config.sources.get('rss_sources', [])
    
    def collect(self) -> List[Article]:
        """RSS記事を収集"""
        all_articles = []
        
        for source in self.sources:
            if not source.get('enabled', True):
                continue
                
            try:
                articles = self._fetch_rss(source)
                all_articles.extend(articles)
            except Exception as e:
                print(f"RSS収集エラー [{source['name']}]: {e}")
                continue
        
        # キーワードフィルタリング
        filtered_articles = self.filter_by_keywords(all_articles)
        
        return filtered_articles
    
    def _fetch_rss(self, source) -> List[Article]:
        """単一のRSSフィードから記事を取得"""
        try:
            # User-Agentを設定してリクエスト
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(source['url'], headers=headers, timeout=10)
            response.raise_for_status()
            
            # feedparserでパース
            feed = feedparser.parse(response.content)
            
            articles = []
            for entry in feed.entries[:10]:  # 最新10件まで
                try:
                    # 公開日時の解析
                    published_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_date = datetime(*entry.updated_parsed[:6])
                    
                    # 要約の取得
                    summary = ""
                    if hasattr(entry, 'summary'):
                        summary = entry.summary
                    elif hasattr(entry, 'description'):
                        summary = entry.description
                    
                    # HTMLタグの除去
                    summary = self._clean_html(summary)
                    
                    article = Article(
                        title=entry.title,
                        url=entry.link,
                        summary=summary,
                        published_date=published_date,
                        source=source['name']
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"記事解析エラー: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            print(f"RSS取得エラー [{source['name']}]: {e}")
            return []
    
    def _clean_html(self, text):
        """HTMLタグを除去"""
        if not text:
            return ""
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, 'html.parser')
        cleaned = soup.get_text().strip()
        
        # 複数の改行を一つにまとめる
        import re
        cleaned = re.sub(r'\n+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned[:200]  # 200文字まで