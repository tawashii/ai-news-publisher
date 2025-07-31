#!/usr/bin/env python3
"""
設定とコンポーネントの基本テスト
"""

import sys
import os
sys.path.append('src')

def test_config_loading():
    """設定ファイルの読み込みテスト"""
    print("🧪 設定ファイル読み込みテスト開始...")
    
    try:
        from utils.config import Config
        config = Config()
        
        # 各設定ファイルの読み込みテスト
        sources = config.sources
        print(f"  ✅ sources.yml: {len(sources.get('rss_sources', []))}個のRSSソース")
        print(f"  ✅ sources.yml: {len(sources.get('twitter_accounts', []))}個のTwitterアカウント")
        
        keywords = config.keywords
        print(f"  ✅ keywords.yml: {len(keywords.get('include_keywords', []))}個の含有キーワード")
        
        control = config.control
        print(f"  ✅ control.yml: skip={control.get('skip_next_publish')}, maintenance={control.get('maintenance_mode')}")
        
        templates = config.templates
        print(f"  ✅ templates.yml: テンプレート読み込み成功")
        
        print("✅ 設定ファイル読み込みテスト: 成功")
        return True
        
    except Exception as e:
        print(f"❌ 設定ファイル読み込みテスト: 失敗 - {e}")
        return False

def test_database():
    """データベース接続テスト"""
    print("\n🧪 データベース接続テスト開始...")
    
    try:
        from utils.database import ArticleHistoryDB
        db = ArticleHistoryDB()
        
        # テストデータ追加
        test_url = "https://test.example.com/article1"
        test_title = "テスト記事"
        
        result = db.add_article(test_url, test_title)
        print(f"  ✅ 記事追加: {result}")
        
        # 重複チェック
        is_duplicate = db.is_duplicate(test_url)
        print(f"  ✅ 重複チェック: {is_duplicate}")
        
        # 履歴取得
        recent = db.get_recent_articles(days=1)
        print(f"  ✅ 最近の記事: {len(recent)}件")
        
        # クリーンアップ
        db.cleanup_old_records(days=0)  # 今作ったテストデータを削除
        
        print("✅ データベーステスト: 成功")
        return True
        
    except Exception as e:
        print(f"❌ データベーステスト: 失敗 - {e}")
        return False

def test_rss_collector():
    """RSS収集テスト"""
    print("\n🧪 RSS収集テスト開始...")
    
    try:
        from utils.config import Config
        from collectors.rss_collector import RSSCollector
        
        config = Config()
        collector = RSSCollector(config)
        
        print("  📡 RSS記事を収集中...")
        articles = collector.collect()
        
        print(f"  ✅ 収集記事数: {len(articles)}件")
        
        if articles:
            sample = articles[0]
            print(f"  📄 サンプル記事:")
            print(f"    タイトル: {sample.title[:50]}...")
            print(f"    ソース: {sample.source}")
            print(f"    スコア: {sample.score}")
        
        print("✅ RSS収集テスト: 成功")
        return True
        
    except Exception as e:
        print(f"❌ RSS収集テスト: 失敗 - {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")
        return False

def test_content_filter():
    """コンテンツフィルターテスト"""
    print("\n🧪 コンテンツフィルターテスト開始...")
    
    try:
        from utils.config import Config
        from processors.content_filter import ContentFilter
        from collectors.base_collector import Article
        from datetime import datetime
        
        config = Config()
        filter_processor = ContentFilter(config)
        
        # テスト記事作成
        test_articles = [
            Article("AI記事1", "http://test1.com", "AI関連の記事です", datetime.now(), "Test"),
            Article("重複記事", "http://test1.com", "重複する記事", datetime.now(), "Test"),  # 重複
            Article("AI記事2", "http://test2.com", "機械学習の話", datetime.now(), "Test"),
        ]
        
        print(f"  📄 入力記事数: {len(test_articles)}件")
        
        filtered = filter_processor.filter_articles(test_articles)
        print(f"  ✅ フィルター後: {len(filtered)}件")
        
        print("✅ コンテンツフィルターテスト: 成功")
        return True
        
    except Exception as e:
        print(f"❌ コンテンツフィルターテスト: 失敗 - {e}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 AI News Publisher テスト開始\n")
    
    results = []
    results.append(test_config_loading())
    results.append(test_database())
    results.append(test_rss_collector())
    results.append(test_content_filter())
    
    print(f"\n📊 テスト結果: {sum(results)}/{len(results)} 成功")
    
    if all(results):
        print("🎉 すべてのテストが成功しました！")
        return 0
    else:
        print("⚠️  一部のテストが失敗しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())