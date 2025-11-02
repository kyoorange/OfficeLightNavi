"""チャット関連のデータモデル"""
from pydantic import BaseModel
from typing import List, Optional, Literal


class Message(BaseModel):
    """メッセージモデル"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """チャットリクエストモデル"""
    messages: List[Message]
    context: Optional[dict] = None  # 物件情報などのコンテキスト


class ChatResponse(BaseModel):
    """チャットレスポンスモデル"""
    message: str
    thinking: Optional[str] = None
    search_queries: Optional[List[str]] = None
    candidates: Optional[List[dict]] = None
    metadata: Optional[dict] = None


class ProjectInfo(BaseModel):
    """物件情報モデル"""
    property_name: Optional[str] = None  # 物件名
    room_name: Optional[str] = None  # 部屋名
    ceiling_height: Optional[float] = None  # 天井高
    impression: Optional[str] = None  # 図面からの印象
    project_type: str = "新規見積"  # 案件タイプ: リニューアル, 相見積もり, 新規見積
    special_environment: bool = False  # 特殊環境
    dimming: bool = False  # 調光
    color_temperature: bool = False  # 調色

