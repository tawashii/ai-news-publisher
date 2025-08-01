import requests
import base64
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

class HatenaPublisher:
    def __init__(self, config):
        self.config = config
        self.user_id = config.hatena_username
        self.blog_id = config.hatena_blog_id
        self.api_key = config.hatena_api_key
        
        if not all([self.user_id, self.blog_id, self.api_key]):
            raise ValueError("はてなブログの認証情報が不足しています")
        
        self.api_url = f"https://blog.hatena.ne.jp/{self.user_id}/{self.blog_id}/atom/entry"
    
    def publish(self, title: str, content: str, category: str = "AI") -> bool:
        """はてなブログに記事を投稿"""
        try:
            # AtomPub形式のXMLを作成
            entry_xml = self._create_entry_xml(title, content, category)
            
            # デバッグ: 生成XMLの全体を表示
            print(f"🔍 生成XML全体:")
            print(entry_xml)
            print("🔍 XML終了")
            
            # Basic認証のヘッダー作成
            headers = self._create_auth_headers()
            headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
            
            # はてなブログAPIに投稿（UTF-8バイト文字列として送信）
            response = requests.post(
                self.api_url,
                data=entry_xml.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                print(f"✅ はてなブログ投稿成功: {response.status_code}")
                
                # 投稿されたエントリのURLを取得
                entry_url = self._extract_entry_url(response.text)
                if entry_url:
                    print(f"📝 投稿URL: {entry_url}")
                
                return True
            else:
                print(f"❌ はてなブログ投稿失敗: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ はてなブログ投稿エラー: {e}")
            return False
    
    def _create_entry_xml(self, title: str, content: str, category: str) -> str:
        """AtomPub形式のXMLエントリを作成（最もシンプルな形式）"""
        # 最もシンプルなAtomエントリ
        xml_template = '''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
  <title>{title}</title>
  <content type="text/x-markdown">{content}</content>
  <category term="{category}" />
</entry>'''
        
        # XMLエスケープ処理
        import html
        escaped_title = html.escape(title)
        escaped_content = html.escape(content)
        escaped_category = html.escape(category)
        
        return xml_template.format(
            title=escaped_title,
            content=escaped_content,
            category=escaped_category
        )
    
    def _create_auth_headers(self) -> dict:
        """Basic認証のヘッダーを作成"""
        # はてなブログはユーザーIDとAPIキーでBasic認証
        credentials = f"{self.user_id}:{self.api_key}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        return {
            'Authorization': f'Basic {encoded_credentials}',
            'User-Agent': 'AI-News-Publisher/1.0'
        }
    
    def _extract_entry_url(self, response_text: str) -> str:
        """レスポンスからエントリURLを抽出"""
        try:
            from xml.etree.ElementTree import fromstring
            
            root = fromstring(response_text)
            
            # 名前空間を考慮してlink要素を探す
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for link in root.findall('.//atom:link', ns):
                if link.get('rel') == 'alternate':
                    return link.get('href')
            
            return None
        
        except Exception as e:
            print(f"URL抽出エラー: {e}")
            return None
    
    def test_connection(self) -> bool:
        """はてなブログAPI接続テスト"""
        try:
            headers = self._create_auth_headers()
            
            # エントリ一覧を取得してテスト（公式ドキュメント準拠）
            blog_url = f"https://blog.hatena.ne.jp/{self.user_id}/{self.blog_id}/atom/entry"
            response = requests.get(blog_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ はてなブログAPI接続成功")
                return True
            else:
                print(f"❌ はてなブログAPI接続失敗: {response.status_code}")
                print(f"🔍 接続先URL: {blog_url}")
                print(f"🔍 レスポンス: {response.text[:200]}")
                return False
        
        except Exception as e:
            print(f"❌ はてなブログAPI接続エラー: {e}")
            return False