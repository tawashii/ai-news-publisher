# AI Tech News Auto Publisher

AI関連のテックニュースを自動収集し、はてなブログに毎日投稿するシステムです。

## 🚀 特徴

- **完全自動化**: 毎日8:30に自動投稿
- **複数情報源**: RSS + Twitter/Xの情報を統合
- **AI記事生成**: Gemini API + ollama のハイブリッド構成
- **重複防止**: 30日間の投稿履歴で重複チェック
- **完全無料**: GitHub Actions + 無料APIのみ使用

## 📰 情報源

### RSS フィード
- ITmedia AI+
- はてなブックマーク テクノロジー
- Zenn AI関連記事

### Twitter/X アカウント (Gemini API経由)
- @chatgptlc (ChatGPT研究所)
- @schroneko (ぬこぬこ)
- @usutaku_channel (usutaku)
- @minorun365 (みのるん)

## 🛠️ セットアップ

### 1. 必要なAPIキーの取得

1. **はてなブログ APIキー**
   - はてなブログの設定 → 詳細設定 → AtomPub から取得

2. **Gemini API キー**
   - [Google AI Studio](https://makersuite.google.com/app/apikey) から取得

### 2. GitHub Secrets の設定

リポジトリの Settings → Secrets and variables → Actions で以下を設定:

```
HATENA_API_KEY=your_hatena_api_key
HATENA_USER_ID=your_hatena_user_id
HATENA_BLOG_ID=your_blog_id
GEMINI_API_KEY=your_gemini_api_key
```

### 3. 設定ファイルのカスタマイズ

- `config/sources.yml`: 情報源の追加・削除
- `config/keywords.yml`: フィルタキーワードの調整
- `config/control.yml`: 実行制御設定

## 📅 実行スケジュール

- **自動実行**: 毎日 8:15 (JST) 
- **処理内容**: 情報収集 → 記事生成 → 投稿
- **手動実行**: GitHub Actions の「Run workflow」から実行可能

## 🔧 設定管理

### 投稿をスキップしたい場合
```yaml
# config/control.yml
skip_next_publish: true
```

### メンテナンスモード
```yaml
# config/control.yml
maintenance_mode: true
```

### 情報源の追加
```yaml
# config/sources.yml
rss_sources:
  - name: "新しいサイト"
    url: "https://example.com/rss"
    enabled: true
```

## 📊 生成される記事の構成

```markdown
# 今日のAIニュースまとめ（YYYY/MM/DD）

今日注目のAI関連ニュースを4-5記事ピックアップしてお届けします。

## 🚀 [記事タイトル1]
**要約**: [簡潔な要約]
**詳細**: [詳しい解説]
[元記事を読む](URL)

## 🤖 [記事タイトル2]
...

## 💡 今日のまとめ
- 注目ポイント1
- 注目ポイント2
- 注目ポイント3
```

## 🔍 トラブルシューティング

### よくある問題

1. **記事生成に失敗する**
   - Gemini API の制限を確認
   - ollama のフォールバック機能が動作するか確認

2. **はてなブログ投稿に失敗する**
   - APIキーが正しいか確認
   - ブログIDが正しいか確認

3. **情報収集に失敗する**
   - RSS URLが有効か確認
   - Gemini API の残り回数を確認

### エラー時の対応

- エラーが発生すると自動的にGitHub Issueが作成されます
- Actions の「Artifacts」からログファイルをダウンロード可能

## 📈 システム構成

```
情報収集 → 重複チェック → AI記事生成 → はてなブログ投稿
    ↓           ↓            ↓           ↓
RSS/Twitter → SQLite → Gemini/ollama → AtomPub API
```

## 🛡️ セキュリティ

- APIキーは GitHub Secrets で管理
- ログにAPIキーが出力されないよう配慮
- 不正なコンテンツのフィルタリング機能

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

Issue や Pull Request をお気軽にお送りください。

---

🤖 **Generated with Claude Code** - AI-powered automated news publishing system