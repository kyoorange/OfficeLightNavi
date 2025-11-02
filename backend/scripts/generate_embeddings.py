"""product_categories テーブルのembeddingカラムを生成・更新するスクリプト"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# backendディレクトリをPythonパスに追加
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from app.utils.embeddings import get_embedding, prepare_text_for_embedding_from_dict  # noqa: E402


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def load_database_url() -> str:
    """環境変数からDATABASE_URLを取得する"""
    load_dotenv(dotenv_path=BACKEND_ROOT / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL が設定されていません")

    # SQLAlchemy向けにschemaクエリパラメータを除去
    if "?schema=" in database_url:
        database_url = database_url.split("?")[0]

    return database_url


def fetch_categories(engine) -> list[Dict[str, Any]]:
    """product_categories のレコードを取得する"""
    select_sql = text(
        """
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
        ORDER BY id
        """
    )

    with engine.connect() as conn:
        result = conn.execute(select_sql)
        return [dict(row) for row in result.mappings().all()]


def update_embedding(engine, category_id: int, embedding_str: str) -> None:
    """embeddingカラムを更新する"""
    update_sql = text(
        """
        UPDATE product_categories
        SET embedding = CAST(:embedding AS vector)
        WHERE id = :category_id
        """
    )

    with engine.begin() as conn:
        conn.execute(
            update_sql,
            {"embedding": embedding_str, "category_id": category_id},
        )


async def generate_embeddings() -> None:
    """全カテゴリのembeddingを生成して保存する"""
    database_url = load_database_url()
    engine = create_engine(database_url)

    categories = fetch_categories(engine)
    if not categories:
        print("📭 登録済みのカテゴリがありません")
        return

    total = len(categories)
    print(f"[INFO] embedding生成を開始します（対象: {total}件）")

    for index, category in enumerate(categories, start=1):
        text_for_embedding = prepare_text_for_embedding_from_dict(category)
        if not text_for_embedding.strip():
            print(f"[WARN] テキストが空のためスキップ: {category['name']}")
            continue

        try:
            embedding = await get_embedding(text_for_embedding)
        except Exception as exc:
            print(f"[ERROR] Embedding生成に失敗: {category['name']} ({exc})")
            continue

        embedding_str = "[" + ",".join(f"{value:.10f}" for value in embedding) + "]"
        update_embedding(engine, category["id"], embedding_str)

        print(f"[DONE] {index}/{total} {category['name']} のembeddingを更新しました")

    print("[INFO] 全てのembedding生成が完了しました")


if __name__ == "__main__":
    asyncio.run(generate_embeddings())


