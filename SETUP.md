# AI News Publisher セットアップガイド

## 1. 事前準備

### 必要なアカウント
- **Gemini API**: https://makersuite.google.com/app/apikey
- **はてなブログ**: AtomPub API有効化が必要
- **GitHub**: リポジトリとSecrets設定

### はてなブログ API設定
1. はてなブログにログイン
2. 設定 → 詳細設定 → AtomPub → 「有効にする」をチェック
3. API キーをメモ（ブログ設定ページで確認可能）

## 2. ローカル実行

### 環境変数設定
```bash
cp .env.example .env
# .envファイルを編集して実際の値を設定
```

### 依存関係インストール
```bash
pip install -r requirements.txt
```

### テスト実行
```bash
python3 test_config.py
```

### 本番実行
```bash
cd src
python3 main.py
```

## 3. GitHub Actions自動化

### Secretsの設定
GitHubリポジトリの Settings → Secrets and variables → Actions で以下を設定：

- `GEMINI_API_KEY`: Gemini APIキー
- `HATENA_USERNAME`: はてなブログのユーザー名
- `HATENA_API_KEY`: はてなブログのAPIキー
- `HATENA_BLOG_ID`: ブログID（ブログURLの一部）
- `GITHUB_TOKEN`: GitHub Personal Access Token（エラー通知用、オプション）

### ワークフロー確認
- `.github/workflows/daily-publish.yml` が自動で毎日8:30 JSTに実行されます
- 手動実行も可能（Actions タブから「Run workflow」）

## 4. 設定のカスタマイズ

### ニュースソースの追加/削除
- `config/sources.yml` を編集

### キーワードフィルタの調整
- `config/keywords.yml` を編集

### 緊急停止・メンテナンス
- `config/control.yml` で `maintenance_mode: true` に設定

## 5. トラブルシューティング

### よくある問題
1. **Gemini API制限**: 無料枠は月15リクエスト
2. **はてなブログ接続エラー**: APIが無効化されていないか確認
3. **記事収集失敗**: nitterインスタンスがダウンしている可能性

### ログ確認
```bash
tail -f logs/ai_news_publisher.log
```

### 手動デバッグ
```bash
cd src
python3 -c "
from utils.config import Config
config = Config()
print('設定読み込み成功')
"
```

## 6. 運用開始チェックリスト

- [ ] 全ての環境変数が設定済み
- [ ] テストが全て成功
- [ ] はてなブログAPI接続確認済み
- [ ] GitHub Secrets設定済み
- [ ] 初回手動実行でエラーなし