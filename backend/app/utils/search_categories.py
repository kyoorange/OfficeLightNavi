"""製品カテゴリ検索ロジック（Supabase + Embedding対応）"""
import json
from typing import List, Dict, Any, Optional
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from app.utils.embeddings import get_embedding, prepare_text_for_embedding
from langchain_openai import ChatOpenAI

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL環境変数が設定されていません")

# SQLAlchemy用にURLを正規化（schemaパラメータを除去）
# psycopg2はschemaパラメータをサポートしていないため
if "?schema=" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

engine = create_engine(DATABASE_URL)


async def search_categories_by_embedding(
    query: str,
    limit: int = 20,
    use_db: bool = True
) -> List[Dict[str, Any]]:
    """
    Embedding類似度検索（pgvectorを使用）
    
    Args:
        query: 検索クエリ（自然言語）
        limit: 取得件数
        use_db: データベースを使用するか（Falseの場合は空リストを返す）
    
    Returns:
        検索結果のカテゴリリスト
    """
    if not use_db:
        return []

    try:
        # クエリのベクトルを生成
        query_embedding = await get_embedding(query)
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

        # pgvectorで類似度検索
        sql_query = text(f"""
            SELECT
                id,
                name,
                manufacturer,
                series,
                ceiling_height_min,
                ceiling_height_max,
                suitable_for,
                description,
                1 - (embedding <=> '{embedding_str}'::vector) as similarity
            FROM product_categories
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> '{embedding_str}'::vector
            LIMIT {limit}
        """)

        with engine.connect() as conn:
            result = conn.execute(sql_query)
            rows = result.fetchall()

            categories = []
            for row in rows:
                category = {
                    "id": row[0],
                    "name": row[1],
                    "manufacturer": row[2],
                    "series": row[3],
                    "ceiling_height_min": float(row[4]) if row[4] else 0.0,
                    "ceiling_height_max": float(row[5]) if row[5] else 0.0,
                    "suitable_for": row[6] if isinstance(row[6], list) else json.loads(row[6]) if row[6] else [],
                    "description": row[7],
                    "similarity": float(row[8]) if row[8] else 0.0
                }
                categories.append(category)

            return categories

    except Exception as e:
        print(f"Embedding検索エラー: {e}")
        return []


async def search_categories(
    query: Optional[str] = None,
    keywords: Optional[List[str]] = None,
    use_embedding: bool = True,
    use_llm: bool = False,
    llm: Optional[ChatOpenAI] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    製品カテゴリを検索（ハイブリッド検索）
    
    Args:
        query: 自然言語クエリ
        keywords: キーワードリスト
        use_embedding: Embedding検索を使用するか
        use_llm: LLM検索を使用するか
        llm: Langchain LLMインスタンス（LLM検索時）
        limit: 取得件数
    
    Returns:
        検索結果のカテゴリリスト
    """
    # ステップ1: Embedding検索
    if use_embedding and query:
        embedding_results = await search_categories_by_embedding(query, limit=limit)
        if embedding_results:
            return embedding_results
    
    # ステップ2: LLM検索（フォールバック）
    if use_llm and llm and query:
        # まず全件取得してからLLMでフィルタリング
        all_categories = search_categories_by_keywords([], limit=limit)
        if all_categories:
            return await search_categories_by_text(
                query=query,
                categories=all_categories,
                llm=llm,
                max_results=limit
            )
    
    # ステップ3: キーワード検索（フォールバック）
    if keywords:
        return search_categories_by_keywords(keywords, limit=limit)
    
    return []


def search_categories_by_keywords(
    keywords: List[str],
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    キーワードで製品カテゴリを検索
    
    Args:
        keywords: 検索キーワードのリスト
        limit: 取得件数
    
    Returns:
        検索結果のカテゴリリスト
    """
    try:
        if not keywords:
            # キーワードがない場合は全件取得
            sql_query = text("""
                SELECT
                    id,
                    name,
                    manufacturer,
                    series,
                    ceiling_height_min,
                    ceiling_height_max,
                    suitable_for,
                    description
                FROM product_categories
                LIMIT :limit
            """)
            params = {"limit": limit}
        else:
            # キーワード検索（name, description, suitable_forで検索）
            keyword_conditions = []
            params = {"limit": limit}
            
            for i, keyword in enumerate(keywords):
                keyword_conditions.append(f"""
                    (name ILIKE :keyword{i} OR 
                     description ILIKE :keyword{i} OR
                     suitable_for::text ILIKE :keyword{i})
                """)
                params[f"keyword{i}"] = f"%{keyword}%"
            
            where_clause = " OR ".join(keyword_conditions)
            
            sql_query = text(f"""
                SELECT
                    id,
                    name,
                    manufacturer,
                    series,
                    ceiling_height_min,
                    ceiling_height_max,
                    suitable_for,
                    description
                FROM product_categories
                WHERE {where_clause}
                LIMIT :limit
            """)

        with engine.connect() as conn:
            result = conn.execute(sql_query, params)
            rows = result.fetchall()

            categories = []
            for row in rows:
                category = {
                    "id": row[0],
                    "name": row[1],
                    "manufacturer": row[2],
                    "series": row[3],
                    "ceiling_height_min": float(row[4]) if row[4] else 0.0,
                    "ceiling_height_max": float(row[5]) if row[5] else 0.0,
                    "suitable_for": row[6] if isinstance(row[6], list) else json.loads(row[6]) if row[6] else [],
                    "description": row[7]
                }
                categories.append(category)

            return categories

    except Exception as e:
        print(f"キーワード検索エラー: {e}")
        return []


async def search_categories_by_text(
    query: str,
    categories: List[Dict[str, Any]],
    llm: ChatOpenAI,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    LLMを使用してカテゴリリストを再ランキング/フィルタリング
    
    Args:
        query: 検索クエリ（自然言語）
        categories: 候補カテゴリのリスト
        llm: Langchain LLMインスタンス
        max_results: 最大結果数
    
    Returns:
        再ランキングされたカテゴリリスト
    """
    if not categories:
        return []
    
    if len(categories) <= max_results:
        return categories
    
    # カテゴリ情報をテキストに変換
    categories_text = ""
    for i, cat in enumerate(categories[:50], 1):  # 最大50件までLLMに渡す
        cat_text = f"{i}. {cat.get('name', '')}\n"
        if cat.get('manufacturer'):
            cat_text += f"   メーカー: {cat.get('manufacturer')}\n"
        if cat.get('description'):
            desc = cat.get('description', '')[:200]  # 説明を200文字に制限
            cat_text += f"   説明: {desc}\n"
        if cat.get('suitable_for'):
            suitable = ', '.join(cat.get('suitable_for', []))
            cat_text += f"   用途: {suitable}\n"
        categories_text += cat_text + "\n"
    
    # LLMに再ランキングを依頼
    from langchain_core.messages import HumanMessage, SystemMessage
    
    prompt = f"""以下の照明器具カテゴリリストから、ユーザーのクエリ「{query}」に最も適した上位{max_results}件を選定してください。

カテゴリリスト:
{categories_text}

選定基準:
1. クエリの意図に最も合致するカテゴリ
2. 用途や説明がクエリに関連しているカテゴリ
3. 一般的な用途のカテゴリも考慮

選定したカテゴリの番号を、重要度の高い順にカンマ区切りで回答してください。
例: 1, 5, 3, 12, 8, ...

回答形式: 番号のみ（例: 1,5,3,12,8）
"""
    
    try:
        messages = [
            SystemMessage(content="あなたは照明器具選定の専門家です。与えられたカテゴリリストから最適なカテゴリを選定してください。"),
            HumanMessage(content=prompt)
        ]
        response = await llm.ainvoke(messages)
        
        # 回答から番号を抽出
        response_text = response.content.strip()
        selected_indices = []
        
        for part in response_text.split(','):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1  # 1-indexedから0-indexedに変換
                if 0 <= idx < len(categories):
                    selected_indices.append(idx)
        
        # 重複を除去し、順序を保持
        seen = set()
        result = []
        for idx in selected_indices:
            if idx not in seen:
                seen.add(idx)
                result.append(categories[idx])
                if len(result) >= max_results:
                    break
        
        # もし選定数が足りない場合は、最初のカテゴリを追加
        while len(result) < max_results and len(result) < len(categories):
            for cat in categories:
                if cat not in result:
                    result.append(cat)
                    break
            else:
                break
        
        return result[:max_results]
        
    except Exception as e:
        print(f"LLM再ランキングエラー: {e}")
        # エラー時は最初のmax_results件を返す
        return categories[:max_results]

