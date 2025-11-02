"""FastAPIアプリケーションのエントリーポイント"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat

app = FastAPI(
    title="OfficeLightNavi API",
    description="施設照明器具選定支援エージェントAPI",
    version="1.0.0"
)

# CORS設定
# 環境変数から許可するオリジンを取得（本番環境用）
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
# 環境変数に追加のオリジンが指定されている場合は追加
import os
extra_origins = os.getenv("CORS_ORIGINS", "").split(",")
allowed_origins.extend([origin.strip() for origin in extra_origins if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"message": "OfficeLightNavi API is running", "status": "ok"}

@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "healthy"}

