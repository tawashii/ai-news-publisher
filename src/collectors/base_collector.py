from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Article:
    title: str
    url: str
    summary: str
    published_date: Optional[datetime] = None
    source: str = ""
    score: float = 0.0
    
    def __post_init__(self):
        if self.published_date is None:
            self.published_date = datetime.now()

class BaseCollector(ABC):
    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def collect(self) -> List[Article]:
        """記事を収集する抽象メソッド"""
        pass
    
    def filter_by_keywords(self, articles: List[Article]) -> List[Article]:
        """キーワードフィルタリング"""
        keywords_config = self.config.keywords
        include_keywords = keywords_config.get('include_keywords', [])
        exclude_keywords = keywords_config.get('exclude_keywords', [])
        
        filtered_articles = []
        
        for article in articles:
            text = f"{article.title} {article.summary}".lower()
            
            # 除外キーワードチェック
            if any(exclude_kw.lower() in text for exclude_kw in exclude_keywords):
                continue
            
            # 含有キーワードチェック
            if any(include_kw.lower() in text for include_kw in include_keywords):
                filtered_articles.append(article)
        
        return filtered_articles