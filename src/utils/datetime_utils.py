"""
日時処理のユーティリティ関数
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional

from .constants import TIMEZONE_JST, DATE_FORMAT, DATETIME_FORMAT

def now_jst() -> datetime:
    """現在の日本時間を取得"""
    return datetime.now(ZoneInfo(TIMEZONE_JST))

def today_jst_str() -> str:
    """今日の日付を日本時間で文字列取得 (YYYY/MM/DD形式)"""
    return now_jst().strftime(DATE_FORMAT)

def now_jst_str() -> str:
    """現在の日時を日本時間で文字列取得 (YYYY-MM-DD HH:MM:SS形式)"""
    return now_jst().strftime(DATETIME_FORMAT)

def days_ago_jst(days: int) -> datetime:
    """指定日数前の日本時間を取得"""
    return now_jst() - timedelta(days=days)

def hours_ago_jst(hours: int) -> datetime:
    """指定時間前の日本時間を取得"""
    return now_jst() - timedelta(hours=hours)

def utc_to_jst(utc_dt: datetime) -> datetime:
    """UTC時間を日本時間に変換"""
    if utc_dt.tzinfo is None:
        # ナイーブなdatetimeはUTCとして扱う
        utc_dt = utc_dt.replace(tzinfo=ZoneInfo('UTC'))
    return utc_dt.astimezone(ZoneInfo(TIMEZONE_JST))