from typing import List
import sys
import os

# パスの設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import Article

class PopularityScorer:
    def __init__(self, config):
        self.config = config
    
    def score_articles(self, articles: List[Article]) -> List[Article]:
        """記事に人気度スコアを付与"""
        for article in articles:
            score = self._calculate_score(article)
            article.score = score
        
        # スコア順にソート（降順）
        articles.sort(key=lambda x: x.score, reverse=True)
        
        return articles
    
    def _calculate_score(self, article: Article) -> float:
        """記事の人気度スコアを計算"""
        score = 0.0
        
        # 1. ソース別の基本スコア
        source_scores = {
            'ITmedia AI+': 7.0,
            'はてなブックマーク テクノロジー': 6.0,
            'Zenn AI': 5.0,
            'Twitter - ChatGPT研究所': 8.0,
            'Twitter - ぬこぬこ': 7.0,
            'Twitter - usutaku': 7.0,
            'Twitter - みのるん': 7.5
        }
        
        score += source_scores.get(article.source, 5.0)
        
        # 2. キーワードによる重み付け
        title_lower = article.title.lower()
        summary_lower = article.summary.lower()
        text = f"{title_lower} {summary_lower}"
        
        # 高重要度キーワード
        high_importance_keywords = [
            'openai', 'chatgpt', 'gpt-4', 'claude', 'gemini',
            '新機能', '発表', 'リリース', '発売', 'beta'
        ]
        
        # 中重要度キーワード
        medium_importance_keywords = [
            'ai', '人工知能', '機械学習', 'llm', 'aiエージェント',
            '改善', '更新', 'アップデート'
        ]
        
        for keyword in high_importance_keywords:
            if keyword in text:
                score += 2.0
        
        for keyword in medium_importance_keywords:
            if keyword in text:
                score += 1.0
        
        # 3. タイトルの長さによる調整（適度な長さが好ましい）
        title_length = len(article.title)
        if 20 <= title_length <= 80:
            score += 1.0
        elif title_length > 100:
            score -= 0.5
        
        # 4. 要約の長さによる調整
        summary_length = len(article.summary)
        if 50 <= summary_length <= 200:
            score += 0.5
        elif summary_length < 20:
            score -= 1.0
        
        # 5. Twitter記事の場合は既存スコアを使用
        if article.source.startswith('Twitter -') and hasattr(article, 'score') and article.score > 0:
            score += article.score * 0.5  # Geminiから取得したスコアを0.5倍して加算
        
        return max(score, 0.0)  # 負の値は0にクリップ