import requests
import feedparser
from datetime import datetime, timedelta
from typing import List
import time
import sys
import os

# パスの設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import BaseCollector, Article
from utils.constants import (
    NITTER_INSTANCES, USER_AGENT, RSS_MAX_ENTRIES, 
    MAX_TITLE_LENGTH, MAX_SUMMARY_LENGTH, AI_RELATED_KEYWORDS,
    HIGH_IMPORTANCE_KEYWORDS, MEDIUM_IMPORTANCE_KEYWORDS,
    BASE_SCORE, HIGH_IMPORTANCE_BONUS, MEDIUM_IMPORTANCE_BONUS, MAX_SCORE
)
from utils.logger import get_logger

class TwitterCollector(BaseCollector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger("twitter_collector")
        self.accounts = config.sources.get('twitter_accounts', [])
        self.search_hours_back = config.sources.get('search_time_range', {}).get('hours_back', 20)
        self.nitter_instances = NITTER_INSTANCES
    
    def collect(self) -> List[Article]:
        """Twitter情報を収集"""
        all_articles = []
        
        for account in self.accounts:
            if not account.get('enabled', True):
                continue
            
            try:
                articles = self._search_account_posts(account)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Twitter収集エラー [{account['account']}]: {e}")
                continue
        
        # キーワードフィルタリング
        filtered_articles = self.filter_by_keywords(all_articles)
        
        return filtered_articles
    
    def _search_account_posts(self, account) -> List[Article]:
        """nitter RSS経由でTwitter投稿を取得"""
        account_name = account['account']
        display_name = account.get('display_name', account_name)
        
        # 複数のnitterインスタンスを試行
        for nitter_base in self.nitter_instances:
            try:
                rss_url = f"{nitter_base}/{account_name}/rss"
                
                # User-Agentを設定してリクエスト
                headers = {'User-Agent': USER_AGENT}
                
                response = requests.get(rss_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # RSS解析
                feed = feedparser.parse(response.content)
                articles = self._parse_rss_feed(feed, account_name, display_name)
                
                if articles:  # 記事が取得できた場合
                    print(f"  ✅ {nitter_base} から {len(articles)}件取得")
                    return articles
                
            except Exception as e:
                print(f"  ⚠️  {nitter_base} エラー: {e}")
                continue
        
        print(f"  ❌ すべてのnitterインスタンスで失敗: {account_name}")
        return []
    
    def _parse_rss_feed(self, feed, account_name, display_name) -> List[Article]:
        """RSSフィードを解析してArticleオブジェクトに変換"""
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=self.search_hours_back)
        
        for entry in feed.entries[:10]:  # 最新10件まで
            try:
                # 公開日時の解析
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_date = datetime(*entry.updated_parsed[:6])
                else:
                    published_date = datetime.now()
                
                # 指定期間内の投稿のみ
                if published_date < cutoff_time:
                    continue
                
                # 要約の取得（HTMLタグ除去）
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = entry.summary
                elif hasattr(entry, 'description'):
                    summary = entry.description
                
                # HTMLタグを除去
                summary = self._clean_html_tags(summary)
                
                # AI関連キーワードを含む投稿のみ
                if not self._contains_ai_keywords(entry.title + " " + summary):
                    continue
                
                # スコアを計算（簡易版）
                score = self._calculate_tweet_score(entry.title, summary)
                
                article = Article(
                    title=entry.title[:100],  # タイトルを100文字に制限
                    url=entry.link,
                    summary=summary[:200],    # 要約を200文字に制限
                    published_date=published_date,
                    source=f"Twitter - {display_name}",
                    score=score
                )
                
                articles.append(article)
                
            except Exception as e:
                print(f"  ⚠️  投稿解析エラー: {e}")
                continue
        
        return articles
    
    def _clean_html_tags(self, text):
        """HTMLタグを除去"""
        if not text:
            return ""
        
        import re
        # HTMLタグを除去
        clean = re.sub(r'<[^>]+>', '', text)
        # 複数の空白を一つにまとめる
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def _contains_ai_keywords(self, text):
        """AI関連キーワードが含まれているかチェック"""
        ai_keywords = [
            'ai', 'chatgpt', 'claude', 'gemini', 'openai', 'anthropic',
            '機械学習', '人工知能', 'llm', 'gpt', 'エージェント'
        ]
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in ai_keywords)
    
    def _calculate_tweet_score(self, title, summary):
        """ツイートのスコアを計算"""
        score = 5.0  # ベーススコア
        
        text = f"{title} {summary}".lower()
        
        # 高重要度キーワード
        high_keywords = ['発表', 'リリース', '新機能', '発売', 'ベータ', '更新']
        for keyword in high_keywords:
            if keyword in text:
                score += 2.0
        
        # 中重要度キーワード
        medium_keywords = ['改善', 'アップデート', '機能', '追加']
        for keyword in medium_keywords:
            if keyword in text:
                score += 1.0
        
        return min(score, 10.0)  # 最大10.0に制限