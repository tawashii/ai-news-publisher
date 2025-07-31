import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

class ArticleHistoryDB:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = Path(__file__).parent.parent.parent
            db_path = base_dir / "data" / "history.db"
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベース初期化"""
        # データディレクトリが存在しない場合は作成
        self.db_path.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                url_hash TEXT NOT NULL,
                published_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # インデックス作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_url_hash ON article_history(url_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON article_history(created_at)')
        
        conn.commit()
        conn.close()
    
    def generate_url_hash(self, url):
        """URLのハッシュ値を生成"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def is_duplicate(self, url):
        """URLが重複しているかチェック"""
        url_hash = self.generate_url_hash(url)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT COUNT(*) FROM article_history WHERE url_hash = ?',
            (url_hash,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def add_article(self, url, title, published_date=None):
        """記事をデータベースに追加"""
        if published_date is None:
            published_date = datetime.now().date()
        
        url_hash = self.generate_url_hash(url)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO article_history (url, title, url_hash, published_date)
                VALUES (?, ?, ?, ?)
            ''', (url, title, url_hash, published_date))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 既に存在する場合
            return False
        finally:
            conn.close()
    
    def cleanup_old_records(self, days=30):
        """古いレコードを削除（デフォルト30日）"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM article_history WHERE created_at < ?',
            (cutoff_date,)
        )
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_recent_articles(self, days=7):
        """最近の記事一覧を取得"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, title, published_date, created_at 
            FROM article_history 
            WHERE created_at >= ?
            ORDER BY created_at DESC
        ''', (cutoff_date,))
        
        articles = cursor.fetchall()
        conn.close()
        
        return articles