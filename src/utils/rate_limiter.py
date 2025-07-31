import time
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List

class RateLimiter:
    """API レート制限管理クラス"""
    
    def __init__(self):
        self._call_history: Dict[str, List[datetime]] = {}
    
    def is_allowed(self, api_name: str, max_calls: int, time_window_minutes: int) -> bool:
        """指定されたAPI呼び出しが制限内かチェック"""
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=time_window_minutes)
        
        # 履歴の初期化
        if api_name not in self._call_history:
            self._call_history[api_name] = []
        
        # 古い履歴を削除
        self._call_history[api_name] = [
            call_time for call_time in self._call_history[api_name]
            if call_time > cutoff_time
        ]
        
        # 制限チェック
        return len(self._call_history[api_name]) < max_calls
    
    def record_call(self, api_name: str):
        """API呼び出しを記録"""
        now = datetime.now()
        if api_name not in self._call_history:
            self._call_history[api_name] = []
        
        self._call_history[api_name].append(now)
    
    def wait_if_needed(self, api_name: str, max_calls: int, time_window_minutes: int):
        """必要に応じて待機"""
        if not self.is_allowed(api_name, max_calls, time_window_minutes):
            # 最も古い呼び出し時刻から計算
            oldest_call = min(self._call_history[api_name])
            wait_until = oldest_call + timedelta(minutes=time_window_minutes)
            wait_seconds = (wait_until - datetime.now()).total_seconds()
            
            if wait_seconds > 0:
                print(f"⏳ {api_name} レート制限: {wait_seconds:.1f}秒待機中...")
                time.sleep(wait_seconds)

# グローバルレートリミッター
rate_limiter = RateLimiter()

def rate_limited(api_name: str, max_calls_per_minute: int = 15):
    """
    レート制限デコレータ
    
    Args:
        api_name: API名
        max_calls_per_minute: 1分あたりの最大呼び出し数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # レート制限チェック
            rate_limiter.wait_if_needed(api_name, max_calls_per_minute, 1)
            
            try:
                result = func(*args, **kwargs)
                rate_limiter.record_call(api_name)
                return result
            except Exception as e:
                # エラーの場合もレート制限にカウント（不正利用防止）
                rate_limiter.record_call(api_name)
                raise e
        
        return wrapper
    return decorator

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    指数バックオフによるリトライデコレータ
    
    Args:
        max_retries: 最大リトライ回数
        base_delay: 基本待機時間（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        # 最後の試行で失敗した場合は例外を再発生
                        raise e
                    
                    # 指数バックオフで待機
                    delay = base_delay * (2 ** attempt)
                    print(f"  ⚠️  試行 {attempt + 1}/{max_retries + 1} 失敗: {e}")
                    print(f"  ⏳ {delay}秒後にリトライ...")
                    time.sleep(delay)
            
        return wrapper
    return decorator