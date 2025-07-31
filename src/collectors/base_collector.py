from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Protocol, TypedDict, Any, Dict

class ConfigProtocol(Protocol):
    """設定オブジェクトのプロトコル定義"""
    keywords: Dict[str, List[str]]

class KeywordsConfig(TypedDict):
    """キーワード設定の型定義"""
    include_keywords: List[str]
    exclude_keywords: List[str]

@dataclass
class Article:
    """記事データクラス"""
    title: str
    url: str
    summary: str
    published_date: Optional[datetime] = None
    source: str = ""
    score: float = 0.0
    
    def __post_init__(self) -> None:
        """初期化後処理"""
        if self.published_date is None:
            self.published_date = datetime.now()
        
        # 型安全性のための検証
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string")
        if not isinstance(self.url, str) or not self.url.strip():
            raise ValueError("url must be a non-empty string")
        if not isinstance(self.score, (int, float)) or self.score < 0:
            raise ValueError("score must be a non-negative number")

class BaseCollector(ABC):
    """記事収集の基底クラス"""
    
    def __init__(self, config: ConfigProtocol) -> None:
        self.config = config
    
    @abstractmethod
    def collect(self) -> List[Article]:
        """記事を収集する抽象メソッド"""
        pass
    
    def filter_by_keywords(self, articles: List[Article]) -> List[Article]:
        """キーワードフィルタリング
        
        Args:
            articles: フィルタリング対象の記事リスト
            
        Returns:
            フィルタリング後の記事リスト
            
        Raises:
            ValueError: キーワード設定が不正な場合
        """
        if not articles:
            return []
            
        try:
            keywords_config: Dict[str, Any] = self.config.keywords
            include_keywords: List[str] = keywords_config.get('include_keywords', [])
            exclude_keywords: List[str] = keywords_config.get('exclude_keywords', [])
            
            # 型チェック
            if not isinstance(include_keywords, list):
                raise ValueError("include_keywords must be a list")
            if not isinstance(exclude_keywords, list):
                raise ValueError("exclude_keywords must be a list")
                
        except (AttributeError, KeyError) as e:
            raise ValueError(f"Invalid keywords configuration: {e}")
        
        filtered_articles: List[Article] = []
        
        for article in articles:
            if not isinstance(article, Article):
                continue  # 不正な記事オブジェクトをスキップ
                
            text: str = f"{article.title} {article.summary}".lower()
            
            # 除外キーワードチェック
            if any(exclude_kw.lower() in text for exclude_kw in exclude_keywords 
                   if isinstance(exclude_kw, str)):
                continue
            
            # 含有キーワードチェック
            if any(include_kw.lower() in text for include_kw in include_keywords 
                   if isinstance(include_kw, str)):
                filtered_articles.append(article)
        
        return filtered_articles