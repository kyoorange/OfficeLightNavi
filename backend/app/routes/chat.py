"""チャット関連のAPIルート"""
from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse, Message
from app.agents.lighting_agent import LightingAgent
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
agent = LightingAgent()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    チャットエンドポイント
    
    ユーザーのメッセージを受け取り、エージェントの応答を返す
    """
    try:
        # OpenAI APIキーのチェック
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEYが設定されていません。.envファイルを確認してください。"
            )
        
        # エージェントにリクエストを渡す
        response = await agent.process_message(
            messages=request.messages,
            context=request.context
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラーが発生しました: {str(e)}")

