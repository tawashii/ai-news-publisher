import requests
import os
from datetime import datetime

class GitHubIssueCreator:
    def __init__(self):
        # GitHub Actionsで自動的に設定される環境変数
        self.token = os.environ.get('GITHUB_TOKEN')
        self.repository = os.environ.get('GITHUB_REPOSITORY')  # 例: "username/repo-name"
        
        if not self.token:
            print("⚠️  GITHUB_TOKEN が設定されていません。Issue作成をスキップします。")
        
        if not self.repository:
            print("⚠️  GITHUB_REPOSITORY が設定されていません。Issue作成をスキップします。")
    
    def create_issue(self, title: str, body: str, labels: list = None) -> bool:
        """GitHubにIssueを作成"""
        if not self.token or not self.repository:
            print("❌ GitHub Issue作成: 認証情報が不足")
            return False
        
        try:
            api_url = f"https://api.github.com/repos/{self.repository}/issues"
            
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            issue_data = {
                'title': title,
                'body': body,
                'labels': labels or ['automation', 'error']
            }
            
            response = requests.post(api_url, json=issue_data, headers=headers, timeout=10)
            
            if response.status_code == 201:
                issue_url = response.json().get('html_url')
                print(f"✅ GitHub Issue作成成功: {issue_url}")
                return True
            else:
                print(f"❌ GitHub Issue作成失敗: {response.status_code}")
                print(f"レスポンス: {response.text}")
                return False
        
        except Exception as e:
            print(f"❌ GitHub Issue作成エラー: {e}")
            return False
    
    def create_error_issue(self, error_type: str, error_message: str, additional_info: str = "") -> bool:
        """エラー用のIssueを作成"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        title = f"🚨 自動投稿エラー: {error_type} ({timestamp})"
        
        body = f"""
## エラー概要
**エラータイプ**: {error_type}
**発生時刻**: {timestamp}

## エラー詳細
```
{error_message}
```

## 追加情報
{additional_info}

## 対応方法
- [ ] エラーの原因を調査
- [ ] 必要に応じて設定を修正
- [ ] 次回の自動実行を確認

## 自動生成
このIssueは自動投稿システムによって自動生成されました。
"""

        return self.create_issue(title, body, ['automation', 'error', 'high-priority'])
    
    def create_skip_issue(self, reason: str, details: str = "") -> bool:
        """投稿スキップ用のIssueを作成"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        title = f"⏭️  投稿スキップ: {reason} ({timestamp})"
        
        body = f"""
## スキップ理由
{reason}

## 詳細
{details}

## 発生時刻
{timestamp}

## 状況確認
- [ ] 情報源の状況確認
- [ ] API制限の確認  
- [ ] 設定ファイルの確認
- [ ] 次回実行の準備

## 自動生成
このIssueは自動投稿システムによって自動生成されました。
"""

        return self.create_issue(title, body, ['automation', 'skip', 'info'])