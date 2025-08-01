import google.generativeai as genai
from datetime import datetime
from typing import List
import random
import sys
import os

# パスの設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.base_collector import Article
from utils.rate_limiter import rate_limited, retry_with_backoff
from utils.constants import TARGET_ARTICLE_LENGTH, MAX_ARTICLES_PER_POST, DATE_FORMAT
from utils.datetime_utils import today_jst_str
from utils.logger import get_logger

class AISummarizer:
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("ai_summarizer")
        self.templates = config.templates
        
        # Gemini API設定
        api_key = config.gemini_api_key
        if not api_key:
            raise ValueError("GEMINI_API_KEY環境変数が設定されていません")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_article(self, articles: List[Article]) -> str:
        """記事一覧からブログ記事を生成"""
        if not articles:
            raise ValueError("記事が空です")
        
        try:
            # メイン: Gemini APIで生成
            content = self._generate_with_gemini(articles)
            print("✅ Gemini APIで記事生成完了")
            return content
        
        except Exception as e:
            print(f"⚠️  Gemini API失敗: {e}")
            # フォールバック: ollama
            try:
                content = self._generate_with_ollama(articles)
                print("✅ ollamaで記事生成完了")
                return content
            except Exception as e2:
                print(f"❌ ollama生成も失敗: {e2}")
                raise Exception(f"記事生成に失敗しました。Gemini: {e}, Ollama: {e2}")
    
    @rate_limited('gemini_api', max_calls_per_minute=15)
    @retry_with_backoff(max_retries=2, base_delay=2.0)
    def _generate_with_gemini(self, articles: List[Article]) -> str:
        """Gemini APIで記事生成（レート制限・リトライ付き）"""
        today = today_jst_str()
        article_count = len(articles)
        
        # 記事情報を整理
        article_info = []
        for i, article in enumerate(articles[:MAX_ARTICLES_PER_POST]):
            article_info.append(f"""
記事{i+1}:
- タイトル: {article.title}
- 要約: {article.summary}
- URL: {article.url}
- ソース: {article.source}
- スコア: {article.score}
""")
        
        prompt = f"""
以下のAI関連ニュースを参考に、自然で読みやすいはてなブログ記事を作成してください。

【重要】Markdown記法を正しく使用:
- 見出しは必ず ## から始める（#は1つだけタイトル用）
- 段落間は必ず空行を入れる
- リスト項目の前後に空行を入れる

【文体のポイント】:
- カジュアルで親しみやすい口調（「〜ですね」「〜みたいです」「個人的には〜」）
- 読者に語りかけるような表現
- 技術的な内容をわかりやすく噛み砕いて説明
- 短い段落で読みやすく構成
- 個人的な感想や所感を織り交ぜる

【テンプレート】必ずこの形式で書いてください:

# 今日のAIニュース（{today}）

今日もAI関連で面白いニュースがいくつか出てきたので、気になったものをピックアップしてみました。

## [記事1の見出し]

[記事の要点を1-2文で簡潔に]

[技術的な背景や意味を噛み砕いて説明。個人的な感想も含める]

{article.url}

## [記事2の見出し]

[記事の要点を1-2文で簡潔に]

[技術的な背景や意味を噛み砕いて説明。個人的な感想も含める]

{article.url}

## 個人的に気になったポイント

今日のニュースを見ていて感じたことをいくつか：

- [技術トレンドや業界の動きについての所感]
- [実用性や影響について]
- [今後の展開予想]

参考データ:
{"".join(article_info)}

【重要な指示】:
- 「ご紹介します」「詳しく解説」等のAI的表現は絶対使わない
- 「〜ですね」「〜みたいです」「個人的には」等のカジュアルな表現を使う
- 短い段落で区切り、読みやすくする
- URLはそのまま貼って埋め込み表示にする
- 技術的な内容も一般読者にわかりやすく説明
"""

        response = self.model.generate_content(prompt)
        return response.text
    
    def _generate_with_ollama(self, articles: List[Article]) -> str:
        """ollamaで記事生成（フォールバック）"""
        try:
            import ollama
        except ImportError:
            raise ImportError("ollamaがインストールされていません")
        
        today = today_jst_str()
        article_count = len(articles)
        
        # シンプルなプロンプト
        article_summaries = []
        for article in articles[:MAX_ARTICLES_PER_POST]:
            article_summaries.append(f"- {article.title}: {article.summary[:100]}")
        
        prompt = f"""
以下のAI関連ニュースを元に、{TARGET_ARTICLE_LENGTH}文字程度のブログ記事を作成してください。

タイトル: 今日のAIニュースまとめ（{today}）

記事数: {article_count}記事

記事内容:
{chr(10).join(article_summaries)}

構成:
1. 導入文
2. 各記事の要約と詳細
3. まとめ

自然で読みやすい日本語で書いてください。
"""

        response = ollama.generate(
            model='llama3.1',
            prompt=prompt
        )
        
        return response['response']
    
    def _select_emoji(self) -> str:
        """ランダムに絵文字を選択"""
        emojis = self.templates.get('emojis', ['🚀', '🤖', '💡', '🔬', '⚡'])
        return random.choice(emojis)