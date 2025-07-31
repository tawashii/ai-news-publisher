import logging
import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class NewsPublisherLogger:
    """AIニュース投稿システム専用ロガー"""
    
    def __init__(self, name: str, log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 重複ハンドラー防止
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """ログハンドラーの設定"""
        # コンソール出力
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # ログフォーマット
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        # GitHub Actions環境でのログファイル出力
        try:
            log_dir = Path(__file__).parent.parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"news_publisher_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
        except Exception:
            # ファイルログが作成できない場合はスキップ
            pass
    
    def info(self, message: str, **kwargs):
        """情報ログ"""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """警告ログ"""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """エラーログ"""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """デバッグログ"""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """コンテキスト付きログ出力"""
        if kwargs:
            context_str = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context_str}"
        else:
            full_message = message
        
        self.logger.log(level, full_message)
    
    def start_process(self, process_name: str):
        """処理開始ログ"""
        self.info(f"🚀 {process_name} 開始")
    
    def end_process(self, process_name: str, success: bool = True, **kwargs):
        """処理終了ログ"""
        status = "✅" if success else "❌"
        self.info(f"{status} {process_name} {'完了' if success else '失敗'}", **kwargs)
    
    def collect_stats(self, source: str, count: int, success: bool = True):
        """収集統計ログ"""
        status = "✅" if success else "⚠️"
        self.info(f"{status} {source} 収集", count=count, success=success)
    
    def api_call(self, api_name: str, success: bool = True, response_time: float = None):
        """API呼び出しログ"""
        status = "✅" if success else "❌"
        kwargs = {"api": api_name, "success": success}
        if response_time:
            kwargs["response_time"] = f"{response_time:.2f}s"
        
        self.info(f"{status} {api_name} API呼び出し", **kwargs)

# デフォルトロガーインスタンス
logger = NewsPublisherLogger("news_publisher")

# 各モジュール用のロガー取得関数
def get_logger(module_name: str) -> NewsPublisherLogger:
    """モジュール専用ロガーを取得"""
    return NewsPublisherLogger(f"news_publisher.{module_name}")