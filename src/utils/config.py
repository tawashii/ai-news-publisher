import os
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta

class Config:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.config_dir = self.base_dir / "config"
        
        # キャッシュ機能
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)  # 5分間キャッシュ
        
    def load_yaml(self, filename):
        """YAML設定ファイルを読み込み（キャッシュ付き）"""
        # キャッシュチェック
        now = datetime.now()
        if (filename in self._cache and 
            filename in self._cache_timestamps and
            now - self._cache_timestamps[filename] < self._cache_ttl):
            return self._cache[filename]
        
        file_path = self.config_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                # キャッシュに保存
                self._cache[filename] = data
                self._cache_timestamps[filename] = now
                
                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"設定ファイルが見つかりません: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML解析エラー: {e}")
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    @property
    def sources(self):
        return self.load_yaml("sources.yml")
    
    @property 
    def keywords(self):
        return self.load_yaml("keywords.yml")
    
    @property
    def control(self):
        return self.load_yaml("control.yml")
    
    @property
    def templates(self):
        return self.load_yaml("templates.yml")
    
    @property
    def hatena_api_key(self):
        return os.environ.get('HATENA_API_KEY')
    
    @property
    def hatena_user_id(self):
        return os.environ.get('HATENA_USER_ID')
    
    @property
    def hatena_blog_id(self):
        return os.environ.get('HATENA_BLOG_ID')
    
    @property
    def gemini_api_key(self):
        return os.environ.get('GEMINI_API_KEY')
    
    def validate_env_vars(self):
        """必要な環境変数が設定されているかチェック"""
        required_vars = [
            'HATENA_API_KEY',
            'HATENA_USER_ID', 
            'HATENA_BLOG_ID',
            'GEMINI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"必要な環境変数が設定されていません: {', '.join(missing_vars)}")
        
        return True