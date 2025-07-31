#!/usr/bin/env python3
"""
型チェック用スクリプト
GitHub Copilotが推奨した型安全性チェックを実行
"""

import subprocess
import sys
import os

def run_command(command: str, description: str) -> bool:
    """コマンドを実行して結果を表示"""
    print(f"\n🔍 {description}")
    print(f"実行: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            print("✅ 成功")
            if result.stdout.strip():
                print(f"出力: {result.stdout}")
            return True
        else:
            print("❌ 失敗")
            if result.stderr.strip():
                print(f"エラー: {result.stderr}")
            if result.stdout.strip():
                print(f"出力: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        return False

def main() -> None:
    """メイン処理"""
    print("🚀 型安全性チェック開始")
    
    # 開発用依存関係のインストール確認
    print("\n📦 開発用依存関係のインストール確認...")
    dev_deps_result = run_command(
        "pip install -r requirements-dev.txt", 
        "開発用依存関係インストール"
    )
    
    if not dev_deps_result:
        print("⚠️  開発用依存関係のインストールに失敗。手動でインストールしてください。")
    
    # 型チェック (mypy)
    mypy_result = run_command(
        "mypy src/ --ignore-missing-imports --no-strict-optional",
        "型チェック (mypy)"
    )
    
    # コードフォーマットチェック (black)
    black_result = run_command(
        "black --check --diff src/",
        "コードフォーマットチェック (black)"
    )
    
    # インポート順序チェック (isort)
    isort_result = run_command(
        "isort --check-only --diff src/",
        "インポート順序チェック (isort)"
    )
    
    # リンターチェック (flake8)
    flake8_result = run_command(
        "flake8 src/ --max-line-length=100 --ignore=E203,W503",
        "リンターチェック (flake8)"
    )
    
    # セキュリティチェック (bandit)
    bandit_result = run_command(
        "bandit -r src/ -f txt",
        "セキュリティチェック (bandit)"
    )
    
    # 結果サマリー
    results = [
        ("型チェック", mypy_result),
        ("フォーマット", black_result),
        ("インポート順序", isort_result),
        ("リンター", flake8_result), 
        ("セキュリティ", bandit_result)
    ]
    
    print(f"\n📊 結果サマリー:")
    passed = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 合格: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 すべてのチェックが成功しました！")
        sys.exit(0)
    else:
        print("⚠️  一部のチェックが失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main()