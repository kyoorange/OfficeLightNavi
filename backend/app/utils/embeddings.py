"""OpenAI Embedding APIを使用したベクトル化ロジック"""
import os
from typing import List, Optional
from openai import AsyncOpenAI
import asyncio


# グローバルなクライアントインスタンス
_client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """OpenAIクライアントを取得（シングルトン）"""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEYが設定されていません")
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def get_embedding(
    text: str,
    model: str = "text-embedding-3-small",
    dimensions: int = 1536
) -> List[float]:
    """
    テキストをベクトル化する
    
    Args:
        text: ベクトル化するテキスト
        model: 使用するEmbeddingモデル（デフォルト: text-embedding-3-small）
        dimensions: ベクトルの次元数（デフォルト: 1536）
    
    Returns:
        ベクトル（浮動小数点数のリスト）
    """
    client = get_openai_client()
    
    try:
        response = await client.embeddings.create(
            model=model,
            input=text,
            dimensions=dimensions
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding生成エラー: {e}")
        raise


async def get_embeddings_batch(
    texts: List[str],
    model: str = "text-embedding-3-small",
    dimensions: int = 1536,
    batch_size: int = 100
) -> List[List[float]]:
    """
    複数のテキストをバッチでベクトル化する
    
    Args:
        texts: ベクトル化するテキストのリスト
        model: 使用するEmbeddingモデル
        dimensions: ベクトルの次元数
        batch_size: 1回のAPI呼び出しで処理するテキスト数（OpenAIの制限は最大2048）
    
    Returns:
        ベクトルのリスト
    """
    client = get_openai_client()
    results = []
    
    # バッチ処理
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = await client.embeddings.create(
                model=model,
                input=batch,
                dimensions=dimensions
            )
            # レスポンスの順序を保持
            batch_results = [item.embedding for item in response.data]
            results.extend(batch_results)
        except Exception as e:
            print(f"バッチEmbedding生成エラー（バッチ {i//batch_size + 1}）: {e}")
            # エラーが発生した場合は空のベクトルを追加（エラーハンドリング）
            results.extend([[0.0] * dimensions] * len(batch))
    
    return results


def prepare_text_for_embedding(
    description: str,
    suitable_for: List[str]
) -> str:
    """
    カテゴリ情報をembedding用のテキストに変換
    
    Args:
        description: カテゴリの説明
        suitable_for: 用途のリスト
    
    Returns:
        embedding用に整形されたテキスト
    """
    parts = []
    if description:
        parts.append(description.strip())
    
    if suitable_for:
        suitable_text = ", ".join(suitable_for)
        parts.append(f"用途: {suitable_text}")
    
    return "\n".join(parts) if parts else ""


def prepare_text_for_embedding_from_dict(category: dict) -> str:
    """
    カテゴリ辞書からembedding用のテキストを生成
    
    Args:
        category: カテゴリ情報の辞書
    
    Returns:
        embedding用に整形されたテキスト
    """
    description = category.get("description", "") or ""
    suitable_for = category.get("suitable_for", []) or []
    
    return prepare_text_for_embedding(description, suitable_for)

