#!/bin/bash
# AI News Publisher 実行スクリプト

set -e  # エラー時に終了

echo "🚀 AI News Publisher を開始します..."

# 環境変数チェック
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY が設定されていません"
    echo "   .env ファイルを作成するか、環境変数を設定してください"
    exit 1
fi

if [ -z "$HATENA_USERNAME" ] || [ -z "$HATENA_API_KEY" ] || [ -z "$HATENA_BLOG_ID" ]; then
    echo "❌ はてなブログの設定が不完全です"
    echo "   HATENA_USERNAME, HATENA_API_KEY, HATENA_BLOG_ID を設定してください"
    exit 1
fi

# .envファイルがあれば読み込み
if [ -f .env ]; then
    echo "📄 .env ファイルを読み込み中..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 依存関係チェック
echo "📦 依存関係をチェック中..."
python3 -c "import feedparser, requests, google.generativeai" 2>/dev/null || {
    echo "❌ 依存関係が不足しています"
    echo "   pip install -r requirements.txt を実行してください"
    exit 1
}

# ログディレクトリ作成
mkdir -p logs

# メイン処理実行
echo "🤖 処理を開始..."
cd src
python3 main.py

echo "✅ 完了しました！"