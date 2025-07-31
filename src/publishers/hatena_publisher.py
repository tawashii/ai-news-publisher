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
            
            # Basic認証のヘッダー作成
            headers = self._create_auth_headers()
            headers['Content-Type'] = 'application/xml'
            
            # はてなブログAPIに投稿
            response = requests.post(
                self.api_url,
                data=entry_xml,
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
        """AtomPub形式のXMLエントリを作成"""
        # XMLネームスペース
        atom_ns = "http://www.w3.org/2005/Atom"
        app_ns = "http://www.w3.org/2007/app"
        hatena_ns = "http://www.hatena.ne.jp/info/xmlns#"
        
        # ルート要素
        entry = Element("entry")
        entry.set("xmlns", atom_ns)
        entry.set("xmlns:app", app_ns)
        entry.set("xmlns:hatena", hatena_ns)
        
        # タイトル
        title_elem = SubElement(entry, "title")
        title_elem.text = title
        
        # 本文
        content_elem = SubElement(entry, "content")
        content_elem.set("type", "text/x-markdown")  # Markdown形式で投稿
        content_elem.text = content
        
        # カテゴリ
        category_elem = SubElement(entry, "category")
        category_elem.set("term", category)
        
        # はてなブログ固有の設定
        # 下書きではなく公開
        app_control = SubElement(entry, "{http://www.w3.org/2007/app}control")
        app_draft = SubElement(app_control, "{http://www.w3.org/2007/app}draft")
        app_draft.text = "no"
        
        # XMLを文字列に変換
        xml_string = tostring(entry, encoding='unicode')
        return f'<?xml version="1.0" encoding="utf-8"?>\n{xml_string}'
    
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
            
            # ブログ情報を取得してテスト
            blog_url = f"https://blog.hatena.ne.jp/{self.user_id}/{self.blog_id}/atom"
            response = requests.get(blog_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ はてなブログAPI接続成功")
                return True
            else:
                print(f"❌ はてなブログAPI接続失敗: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ はてなブログAPI接続エラー: {e}")
            return False