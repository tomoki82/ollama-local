#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import time

def test_ollama_connection(base_url="http://localhost:11434", model="codellama"):
    """
    Ollamaサーバーへの接続をテストする関数

    Args:
        base_url: OllamaサーバーのベースURL
        model: テストに使用するモデル名

    Returns:
        bool: 接続が成功したかどうか
    """
    print(f"Ollamaサーバー ({base_url}) への接続をテストしています...")

    # バージョン確認エンドポイントをテスト
    try:
        version_url = f"{base_url}/api/version"
        print(f"バージョンエンドポイントにリクエスト送信中: {version_url}")
        version_response = requests.get(version_url, timeout=10)
        print(f"バージョンエンドポイント応答: {version_response.status_code}")
        print(f"応答内容: {version_response.json()}")
    except Exception as e:
        print(f"バージョンエンドポイントへの接続に失敗しました: {e}")
        return False

    # モデル一覧エンドポイントをテスト
    try:
        models_url = f"{base_url}/api/tags"
        print(f"\nモデル一覧エンドポイントにリクエスト送信中: {models_url}")
        models_response = requests.get(models_url, timeout=10)
        print(f"モデル一覧エンドポイント応答: {models_response.status_code}")
        if models_response.status_code == 200:
            models = models_response.json().get("models", [])
            print(f"利用可能なモデル: {[m.get('name') for m in models]}")

            # 指定されたモデルが存在するか確認
            model_exists = any(m.get('name') == model for m in models)
            if not model_exists:
                print(f"警告: 指定されたモデル '{model}' が見つかりません。")
                print(f"利用可能なモデルのいずれかを使用してください。")
    except Exception as e:
        print(f"モデル一覧エンドポイントへの接続に失敗しました: {e}")

    # 埋め込みエンドポイントをテスト
    try:
        print(f"\n埋め込みエンドポイントにリクエスト送信中...")
        start_time = time.time()
        embed_response = requests.post(
            f"{base_url}/api/embeddings",
            json={"model": model, "prompt": "Test embedding"},
            timeout=30
        )
        elapsed_time = time.time() - start_time
        print(f"埋め込みエンドポイント応答: {embed_response.status_code} (処理時間: {elapsed_time:.2f}秒)")

        if embed_response.status_code == 200:
            embed_data = embed_response.json()
            embed_length = len(embed_data.get("embedding", []))
            print(f"埋め込みベクトルの次元数: {embed_length}")
            return True
        else:
            print(f"エラー詳細: {embed_response.text}")
            return False
    except Exception as e:
        print(f"埋め込みエンドポイントへの接続に失敗しました: {e}")
        return False

def test_with_alternative_urls():
    """
    複数の代替URLでOllamaサーバーへの接続をテストする
    """
    urls_to_try = [
        "http://localhost:11434",
        "http://127.0.0.1:11434",
        "http://0.0.0.0:11434"
    ]

    for url in urls_to_try:
        print("\n" + "=" * 50)
        print(f"{url} でテスト中...")
        print("=" * 50)
        success = test_ollama_connection(url)
        if success:
            print(f"\n✅ {url} への接続に成功しました！")
            print(f"この接続URLをコードで使用してください。")
            return url
        else:
            print(f"\n❌ {url} への接続に失敗しました。")

    print("\n全ての接続テストに失敗しました。")
    return None

if __name__ == "__main__":
    print("Ollamaサーバー接続テストを開始します...")

    if len(sys.argv) > 1:
        # コマンドライン引数からURLとモデルを取得
        base_url = sys.argv[1]
        model = sys.argv[2] if len(sys.argv) > 2 else "codellama"
        test_ollama_connection(base_url, model)
    else:
        # 複数のURLで接続テスト
        working_url = test_with_alternative_urls()

        if working_url:
            print("\n接続設定の推奨例:")
            print(f"""
from llama_index.embeddings.ollama import OllamaEmbedding

embed_model = OllamaEmbedding(
    model_name="codellama",  # または利用可能な別のモデル
    base_url="{working_url}",
    request_timeout=30.0
)
""")
