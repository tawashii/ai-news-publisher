import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

class Config:
    """設定管理クラス - 型安全性を強化"""
    
    def __init__(self) -> None:
        self.base_dir: Path = Path(__file__).parent.parent.parent
        self.config_dir: Path = self.base_dir / "config"
        
        # キャッシュ機能
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_ttl: timedelta = timedelta(minutes=5)  # 5分間キャッシュ
        
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """YAML設定ファイルを読み込み（キャッシュ付き）
        
        Args:
            filename: 読み込むYAMLファイル名
            
        Returns:
            設定データ辞書
            
        Raises:
            FileNotFoundError: ファイルが見つからない場合
            ValueError: YAML解析エラーの場合
        """
        # キャッシュチェック
        now = datetime.now()
        if (filename in self._cache and 
            filename in self._cache_timestamps and
            now - self._cache_timestamps[filename] < self._cache_ttl):
            return self._cache[filename]
        
        file_path: Path = self.config_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = yaml.safe_load(f) or {}
                
                # 型チェック
                if not isinstance(data, dict):
                    raise ValueError(f"設定ファイルは辞書形式である必要があります: {filename}")
                
                # キャッシュに保存
                self._cache[filename] = data
                self._cache_timestamps[filename] = now
                
                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"設定ファイルが見つかりません: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML解析エラー: {e}")
    
    def clear_cache(self) -> None:
        """キャッシュをクリア"""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    @property
    def sources(self) -> Dict[str, Any]:
        """ソース設定を取得"""
        return self.load_yaml("sources.yml")
    
    @property 
    def keywords(self) -> Dict[str, List[str]]:
        """キーワード設定を取得"""
        return self.load_yaml("keywords.yml")
    
    @property
    def control(self) -> Dict[str, Union[bool, int]]:
        """制御設定を取得"""
        return self.load_yaml("control.yml")
    
    @property
    def templates(self) -> Dict[str, Any]:
        """テンプレート設定を取得"""
        return self.load_yaml("templates.yml")
    
    @property
    def hatena_api_key(self) -> Optional[str]:
        """はてなAPIキーを取得"""
        return os.environ.get('HATENA_API_KEY')
    
    @property
    def hatena_username(self) -> Optional[str]:
        """はてなユーザー名を取得"""
        return os.environ.get('HATENA_USERNAME')
    
    @property
    def hatena_blog_id(self) -> Optional[str]:
        """はてなブログIDを取得"""
        return os.environ.get('HATENA_BLOG_ID')
    
    @property
    def gemini_api_key(self) -> Optional[str]:
        """Gemini APIキーを取得"""
        return os.environ.get('GEMINI_API_KEY')
    
    def validate_env_vars(self) -> bool:
        """必要な環境変数が設定されているかチェック
        
        Returns:
            全ての必要な環境変数が設定されている場合True
            
        Raises:
            ValueError: 必要な環境変数が不足している場合
        """
        required_vars: List[str] = [
            'HATENA_API_KEY',
            'HATENA_USERNAME', 
            'HATENA_BLOG_ID',
            'GEMINI_API_KEY'
        ]
        
        missing_vars: List[str] = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"必要な環境変数が設定されていません: {', '.join(missing_vars)}")
        
        return True