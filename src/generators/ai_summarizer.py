import google.generativeai as genai
from datetime import datetime
from typing import List
import random
from ..collectors.base_collector import Article
from ..utils.rate_limiter import rate_limited, retry_with_backoff
from ..utils.constants import TARGET_ARTICLE_LENGTH, MAX_ARTICLES_PER_POST, DATE_FORMAT
from ..utils.logger import get_logger

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
        today = datetime.now().strftime(DATE_FORMAT)
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
以下のAI関連ニュース記事を元に、読みやすいブログ記事を作成してください。

条件:
- 文字数: 約{TARGET_ARTICLE_LENGTH}文字
- 読了時間: 3-4分
- 自然で人間らしい文章
- AIが書いたと分からないような文体
- 絵文字を適度に使用して親しみやすく

記事構成:
# 今日のAIニュースまとめ（{today}）

今日注目のAI関連ニュースを{article_count}記事ピックアップしてお届けします。

## 🚀 [記事1のタイトルを魅力的に]
**要約**: [簡潔で分かりやすい要約 50文字程度]
**詳細**: [詳しい解説や意義について 100-150文字]
[元記事を読む]({article.url})

[他の記事も同様の構成で...]

## 💡 今日のまとめ
- [今日の注目ポイント1]
- [今日の注目ポイント2] 
- [今日の注目ポイント3]

入力記事データ:
{"".join(article_info)}

※絵文字は以下から選択: 🚀 🤖 💡 🔬 ⚡ 🎯 🌟 📊
※記事のタイトルは元のタイトルをより魅力的に改変してください
※「です・ます調」で親しみやすく書いてください
"""

        response = self.model.generate_content(prompt)
        return response.text
    
    def _generate_with_ollama(self, articles: List[Article]) -> str:
        """ollamaで記事生成（フォールバック）"""
        try:
            import ollama
        except ImportError:
            raise ImportError("ollamaがインストールされていません")
        
        today = datetime.now().strftime(DATE_FORMAT)
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