#!/usr/bin/env python3
"""
AI Tech News Auto Publisher
メインスクリプト
"""

import sys
import traceback
import requests
from datetime import datetime
from typing import List, Optional, NoReturn

from utils.config import Config
from utils.database import ArticleHistoryDB
from utils.github_issues import GitHubIssueCreator
from utils.logger import get_logger
from utils.constants import MAX_ARTICLES_PER_POST, MIN_ARTICLES_REQUIRED, DATE_FORMAT
from utils.datetime_utils import now_jst_str, today_jst_str
from collectors.base_collector import Article
from collectors.rss_collector import RSSCollector
from collectors.twitter_collector import TwitterCollector
from processors.content_filter import ContentFilter
from processors.popularity_scorer import PopularityScorer
from generators.ai_summarizer import AISummarizer
from publishers.hatena_publisher import HatenaPublisher

class NewsPublisher:
    """AIニュース自動投稿システムのメインクラス - 型安全性を強化"""
    
    def __init__(self) -> None:
        self.logger = get_logger("main")
        self.config: Config = Config()
        self.db: ArticleHistoryDB = ArticleHistoryDB()
        self.github: GitHubIssueCreator = GitHubIssueCreator()
        
        # 各コンポーネントの初期化
        self.rss_collector: RSSCollector = RSSCollector(self.config)
        self.twitter_collector: TwitterCollector = TwitterCollector(self.config)
        self.content_filter: ContentFilter = ContentFilter(self.config)
        self.popularity_scorer: PopularityScorer = PopularityScorer(self.config)
        self.ai_summarizer: AISummarizer = AISummarizer(self.config)
        self.hatena_publisher: HatenaPublisher = HatenaPublisher(self.config)
    
    def run(self) -> None:
        """メイン処理を実行"""
        try:
            self.logger.start_process("AI Tech News Auto Publisher")
            self.logger.info("実行開始", timestamp=now_jst_str())
            
            # 1. 設定チェック
            self._check_configuration()
            
            # 2. メンテナンスモードチェック
            if self._is_maintenance_mode():
                self.logger.info("🔧 メンテナンスモードのため処理をスキップ")
                return
            
            # 3. 手動スキップチェック
            if self._should_skip():
                self.logger.info("⏭️ 手動スキップが設定されているため処理をスキップ")
                self.github.create_skip_issue("手動スキップ", "control.ymlでskip_next_publishがtrueに設定されています")
                return
            
            # 4. 情報収集
            print("\n📰 情報収集を開始...")
            articles = self._collect_articles()
            
            if len(articles) < self.config.control.get('min_articles_required', MIN_ARTICLES_REQUIRED):
                error_msg = f"記事数が不足しています（{len(articles)}件 < 最低2件）"
                print(f"❌ {error_msg}")
                self.github.create_skip_issue("記事不足", error_msg)
                return
            
            print(f"✅ {len(articles)}件の記事を収集しました")
            
            # 5. 記事生成
            print("\n🤖 記事生成を開始...")
            blog_content = self.ai_summarizer.generate_article(articles[:MAX_ARTICLES_PER_POST])
            
            # 6. はてなブログ投稿
            print("\n📝 はてなブログ投稿を開始...")
            title = f"今日のAIニュース（{today_jst_str()}）"
            
            success = self.hatena_publisher.publish(title, blog_content)
            
            if success:
                print("✅ 投稿が完了しました！")
                
                # 7. 投稿した記事をデータベースに記録
                for article in articles[:MAX_ARTICLES_PER_POST]:
                    self.db.add_article(article.url, article.title)
                
                # 8. 古いレコードのクリーンアップ
                deleted_count = self.db.cleanup_old_records(days=30)
                if deleted_count > 0:
                    print(f"🧹 {deleted_count}件の古い記録を削除しました")
                
            else:
                error_msg = "はてなブログへの投稿に失敗しました"
                print(f"❌ {error_msg}")
                self.github.create_error_issue("投稿失敗", error_msg)
        
        except KeyboardInterrupt:
            print("\n⏹️  処理が中断されました")
            sys.exit(0)
        
        except ValueError as e:
            # 設定エラーなど回復可能性の低いエラー
            error_msg = f"設定エラー: {str(e)}"
            print(f"❌ {error_msg}")
            self.github.create_error_issue("設定エラー", str(e))
            sys.exit(1)
        
        except requests.RequestException as e:
            # ネットワーク関連エラー
            error_msg = f"ネットワークエラー: {str(e)}"
            print(f"❌ {error_msg}")
            self.github.create_error_issue("ネットワークエラー", str(e))
            sys.exit(1)
        
        except Exception as e:
            # その他の予期しないエラー
            error_msg = f"予期しないエラーが発生しました: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"スタックトレース:\n{traceback.format_exc()}")
            
            self.github.create_error_issue(
                "予期しないエラー",
                str(e),
                f"スタックトレース:\n```\n{traceback.format_exc()}\n```"
            )
            
            sys.exit(1)
    
    def _check_configuration(self):
        """設定の有効性をチェック"""
        print("🔧 設定をチェック中...")
        
        try:
            self.config.validate_env_vars()
            print("✅ 環境変数の設定OK")
        except ValueError as e:
            print(f"❌ 設定エラー: {e}")
            raise
        
        # はてなブログ接続テスト
        if not self.hatena_publisher.test_connection():
            raise ValueError("はてなブログAPIへの接続に失敗しました")
    
    def _is_maintenance_mode(self) -> bool:
        """メンテナンスモードかどうかチェック"""
        return self.config.control.get('maintenance_mode', False)
    
    def _should_skip(self) -> bool:
        """手動スキップが設定されているかチェック"""
        return self.config.control.get('skip_next_publish', False)
    
    def _collect_articles(self) -> List[Article]:
        """全ソースから記事を収集"""
        all_articles = []
        
        # RSS記事の収集
        print("📡 RSS記事を収集中...")
        try:
            rss_articles = self.rss_collector.collect()
            all_articles.extend(rss_articles)
            print(f"  ✅ RSS: {len(rss_articles)}件")
        except Exception as e:
            print(f"  ⚠️  RSS収集エラー: {e}")
        
        # Twitter記事の収集
        print("🐦 Twitter記事を収集中...")
        try:
            twitter_articles = self.twitter_collector.collect()
            all_articles.extend(twitter_articles)
            print(f"  ✅ Twitter: {len(twitter_articles)}件")
        except Exception as e:
            print(f"  ⚠️  Twitter収集エラー: {e}")
        
        # フィルタリング
        print("🔍 記事をフィルタリング中...")
        filtered_articles = self.content_filter.filter_articles(all_articles)
        print(f"  ✅ フィルタ後: {len(filtered_articles)}件")
        
        # スコアリング
        print("📊 記事をスコアリング中...")
        scored_articles = self.popularity_scorer.score_articles(filtered_articles)
        
        # 上位記事の表示
        print("\n📈 上位記事:")
        for i, article in enumerate(scored_articles[:5], 1):
            print(f"  {i}. {article.title[:50]}... (スコア: {article.score:.1f})")
        
        return scored_articles

def main():
    """エントリーポイント"""
    publisher = NewsPublisher()
    publisher.run()

if __name__ == "__main__":
    main()