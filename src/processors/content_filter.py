from typing import List
from datetime import datetime, timedelta
# 相対importをabsoluteに変更
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collectors.base_collector import Article
from utils.database import ArticleHistoryDB

class ContentFilter:
    def __init__(self, config):
        self.config = config
        self.db = ArticleHistoryDB()
    
    def filter_articles(self, articles: List[Article]) -> List[Article]:
        """記事をフィルタリング"""
        # 1. 重複チェック
        unique_articles = self._remove_duplicates(articles)
        
        # 2. 日付フィルタ（古すぎる記事を除外）
        recent_articles = self._filter_by_date(unique_articles, days=7)
        
        # 3. 品質フィルタ
        quality_articles = self._filter_by_quality(recent_articles)
        
        return quality_articles
    
    def _remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """重複記事を除去"""
        unique_articles = []
        seen_urls = set()
        
        for article in articles:
            # データベースでの重複チェック
            if self.db.is_duplicate(article.url):
                continue
            
            # メモリ上での重複チェック（同一処理内）
            if article.url in seen_urls:
                continue
            
            unique_articles.append(article)
            seen_urls.add(article.url)
        
        return unique_articles
    
    def _filter_by_date(self, articles: List[Article], days: int = 7) -> List[Article]:
        """日付による記事フィルタ"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_articles = []
        for article in articles:
            if article.published_date and article.published_date >= cutoff_date:
                recent_articles.append(article)
            elif not article.published_date:
                # 公開日が不明な場合は含める
                recent_articles.append(article)
        
        return recent_articles
    
    def _filter_by_quality(self, articles: List[Article]) -> List[Article]:
        """品質による記事フィルタ"""
        quality_articles = []
        
        for article in articles:
            # タイトルの最小長チェック
            if len(article.title.strip()) < 10:
                continue
            
            # 要約の最小長チェック
            if len(article.summary.strip()) < 20:
                continue
            
            # URLの有効性チェック
            if not article.url or not article.url.startswith(('http://', 'https://')):
                continue
            
            quality_articles.append(article)
        
        return quality_articles