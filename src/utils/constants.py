"""
AIニュース投稿システムの定数定義
"""

# 記事処理関連
MAX_ARTICLES_PER_POST = 5
MIN_ARTICLES_REQUIRED = 2
DEFAULT_ARTICLE_COUNT = 4

# 文字数制限
MAX_TITLE_LENGTH = 100
MAX_SUMMARY_LENGTH = 200
TARGET_ARTICLE_LENGTH = 800
MIN_TITLE_LENGTH = 10
MIN_SUMMARY_LENGTH = 20

# 時間設定
HISTORY_RETENTION_DAYS = 30
CONFIG_CACHE_TTL_MINUTES = 5
DEFAULT_SEARCH_HOURS_BACK = 20

# API制限
GEMINI_MAX_CALLS_PER_MINUTE = 15
DEFAULT_REQUEST_TIMEOUT = 10
RETRY_MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 1.0

# RSS取得
RSS_MAX_ENTRIES = 10
NITTER_REQUEST_TIMEOUT = 10

# スコアリング
BASE_SCORE = 5.0
HIGH_IMPORTANCE_BONUS = 2.0
MEDIUM_IMPORTANCE_BONUS = 1.0
MAX_SCORE = 10.0

# ファイルパス
LOG_DIR_NAME = "logs"
DATA_DIR_NAME = "data"
CONFIG_DIR_NAME = "config"

# ネットワーク
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 重要度キーワード
HIGH_IMPORTANCE_KEYWORDS = [
    '発表', 'リリース', '新機能', '発売', 'ベータ', '更新',
    'announcement', 'release', 'launch', 'beta'
]

MEDIUM_IMPORTANCE_KEYWORDS = [
    '改善', 'アップデート', '機能', '追加', '修正',
    'improvement', 'update', 'feature', 'fix'
]

AI_RELATED_KEYWORDS = [
    'ai', 'chatgpt', 'claude', 'gemini', 'openai', 'anthropic',
    '機械学習', '人工知能', 'llm', 'gpt', 'エージェント',
    'machine learning', 'artificial intelligence', 'neural network'
]

# nitterインスタンス
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.it", 
    "https://nitter.unixfox.eu"
]

# 日付フォーマット
DATE_FORMAT = '%Y/%m/%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_DATE_FORMAT = '%Y%m%d'

# タイムゾーン設定
TIMEZONE_JST = 'Asia/Tokyo'