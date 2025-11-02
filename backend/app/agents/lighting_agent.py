"""照明器具選定エージェント"""
import os
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.models.chat import Message, ChatResponse, ProjectInfo
from app.utils.search_categories import search_categories, search_categories_by_keywords, search_categories_by_text
import json

class LightingAgent:
    """照明器具選定を支援するエージェント"""
    
    def __init__(self):
        """エージェントの初期化"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEYが設定されていません")
        
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            api_key=api_key
        )

        # システムプロンプト
        self.system_prompt = """あなたは照明器具の選定を支援する専門家です。
                            ユーザーから物件情報（物件名、部屋名、天井高、図面からの印象など）を受け取り、
                            適切な照明器具を選定する支援を行います。

                            対話の流れ:
                            1. ユーザーから物件情報を受け取る
                            2. 必要に応じて、案件タイプ、特殊環境、調光・調色について質問する
                            3. 情報をもとに思考プロセスを表示する
                            4. カタログから適切な機種を検索する
                            5. 候補機種を提示する

                            常に丁寧で親しみやすい口調で応答してください。
                            思考プロセスは明確に表示し、ユーザーが理解しやすいように説明してください。
                            """

    async def process_message(
        self,
        messages: List[Message],
        context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """
        メッセージを処理して応答を生成
        
        Args:
            messages: 会話履歴
            context: 追加のコンテキスト（物件情報など）
        
        Returns:
            エージェントの応答
        """
        # 会話履歴をLangchain形式に変換
        langchain_messages = [SystemMessage(content=self.system_prompt)]
        
        for msg in messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
        
        # コンテキストから物件情報を抽出
        project_info = None
        if context:
            try:
                project_info = ProjectInfo(**context)
            except:
                pass
        
        # ユーザーの最新メッセージを解析
        latest_message = messages[-1].content if messages else ""
        
        # 物件情報が含まれているかチェック
        if project_info and project_info.property_name:
            # 物件情報が揃っている場合は機種検索を実行
            return await self._generate_search_response(
                project_info,
                latest_message,
                langchain_messages
            )
        else:
            # 物件情報が不足している場合は質問を生成
            return await self._generate_question_response(
                latest_message,
                langchain_messages
            )
    
    async def _generate_question_response(
        self,
        user_message: str,
        langchain_messages: List
    ) -> ChatResponse:
        """質問を生成する"""

        # チャット履歴を準備（システムメッセージを含む）
        messages = langchain_messages.copy()
        messages.append(HumanMessage(content=f"""ユーザーのメッセージを分析し、必要に応じて以下の情報について質問してください:

            1. 案件タイプ: リニューアル、他社との相見積もり、新規見積
            2. 特殊環境: はい/いいえ（クリーンルーム、無塵室など）
            3. 調光・調色: はい/いいえ

            ユーザーが既に物件情報を提供している場合は、まずそれを確認し、不足している情報について質問してください。
            物件情報が不足している場合は、物件名、部屋名、天井高、図面からの印象などを尋ねてください。

            応答は親しみやすく、丁寧な口調でお願いします。

            ユーザーのメッセージ: {user_message}
            """))
        # LLMを直接呼び出す
        response = await self.llm.ainvoke(messages)
        response_text = response.content

        return ChatResponse(
            message=response_text,
            thinking=None,
            search_queries=None,
            candidates=None
        )

    async def _generate_search_response(
        self,
        project_info: ProjectInfo,
        user_message: str,
        langchain_messages: List
    ) -> ChatResponse:
        """機種検索を行い、応答を生成する"""

        # 思考プロセスを生成
        thinking = await self._generate_thinking(project_info, user_message)

        # 物件情報から検索キーワードを生成
        keywords = []
        query_parts = []

        if project_info.property_name:
            query_parts.append(project_info.property_name)
            keywords.append(project_info.property_name)

        if project_info.room_name:
            query_parts.append(project_info.room_name)
            keywords.append(project_info.room_name)

        if project_info.ceiling_height:
            if project_info.ceiling_height > 8:
                keywords.append("高天井")
                query_parts.append("高天井")
            else:
                keywords.append("低天井")
        
        if project_info.special_environment:
            keywords.append("特殊環境")
            query_parts.append("特殊環境")
            if "クリーン" in user_message or "無塵" in user_message:
                keywords.append("クリーンルーム")
            if "厨房" in user_message or "HACCP" in user_message:
                keywords.append("厨房")
        
        # 自然言語クエリを生成
        query = f"{' '.join(query_parts)}に適した照明器具"
        
        # ステップ1: Embedding類似度検索で上位20件を取得（高速）
        embedding_candidates = await search_categories(
            query=query,
            use_embedding=True,
            use_llm=False
        )
        
        # ステップ2: 上位20件のみをLLMに渡して再ランキング/詳細判定（低コスト）
        if embedding_candidates and len(embedding_candidates) > 0:
            # 上位候補のみをLLMに渡して最終選定
            candidates = await search_categories_by_text(
                query=query,
                categories=embedding_candidates,
                llm=self.llm,
                max_results=10
            )
        else:
            # Embedding検索が失敗した場合は従来の方法にフォールバック
            candidates = await search_categories(
                query=query,
                keywords=keywords if keywords else None,
                use_llm=True,
                use_embedding=False,
                llm=self.llm
            )
        
        # キーワード検索も併用（候補が少ない場合の補完）
        if len(candidates) < 3:
            keyword_candidates = search_categories_by_keywords(keywords)
            # 重複を避けながら追加
            existing_ids = {c.get('id') for c in candidates}
            for candidate in keyword_candidates:
                if candidate.get('id') not in existing_ids:
                    candidates.append(candidate)
                if len(candidates) >= 5:
                    break
        
        # 応答を生成
        response_message = await self._generate_candidates_response(
            project_info,
            candidates,
            user_message,
            langchain_messages
        )
        
        return ChatResponse(
            message=response_message,
            thinking=thinking,
            search_queries=[query] + keywords,
            candidates=candidates[:10],  # 最大10件
            metadata={
                "project_info": project_info.model_dump(),
                "search_count": len(candidates),
                "search_method": "llm_text_search"
            }
        )
    
    async def _generate_thinking(
        self,
        project_info: ProjectInfo,
        user_message: str
    ) -> str:
        """思考プロセスを生成"""
        
        messages = [
            SystemMessage(content="""あなたは照明器具選定の専門家です。
物件情報を分析し、適切な機種選定の思考プロセスを簡潔に説明してください。"""),
            HumanMessage(content=f"""以下の物件情報をもとに、機種選定の思考プロセスを説明してください:

物件名: {project_info.property_name or "未指定"}
部屋名: {project_info.room_name or "未指定"}
天井高: {project_info.ceiling_height or 0}m
図面からの印象: {project_info.impression or "未指定"}
案件タイプ: {project_info.project_type}
特殊環境: {"はい" if project_info.special_environment else "いいえ"}
調光: {"可能" if project_info.dimming else "不可"}
調色: {"可能" if project_info.color_temperature else "不可"}

思考プロセスは2-3行程度で簡潔に、専門的すぎない言葉で説明してください。
""")
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def _generate_candidates_response(
        self,
        project_info: ProjectInfo,
        candidates: List[Dict[str, Any]],
        user_message: str,
        langchain_messages: List
    ) -> str:
        """候補機種の応答を生成"""
        
        candidates_text = ""
        for i, candidate in enumerate(candidates[:5], 1):
            candidates_text += f"{i}. {candidate.get('name', '')}\n"
            if candidate.get('manufacturer'):
                candidates_text += f"   メーカー: {candidate.get('manufacturer', '')}\n"
            if candidate.get('series'):
                candidates_text += f"   シリーズ: {candidate.get('series', '')}\n"
            if candidate.get('description'):
                desc = candidate.get('description', '')[:100]  # 説明を100文字に制限
                candidates_text += f"   説明: {desc}...\n"
            if candidate.get('suitable_for'):
                suitable_for = ', '.join(candidate.get('suitable_for', []))
                candidates_text += f"   用途: {suitable_for}\n"
            candidates_text += "\n"
        
        # チャット履歴を準備
        messages = langchain_messages.copy()
        messages.append(HumanMessage(content=f"""以下の候補機種をもとに、ユーザーに親しみやすく、丁寧な口調で応答してください。

候補機種:
{candidates_text or "候補が見つかりませんでした。"}

物件情報:
物件名: {project_info.property_name or "未指定"}
部屋名: {project_info.room_name or "未指定"}
天井高: {project_info.ceiling_height or 0}m

候補機種の特徴を簡潔に説明し、必要に応じて追加の条件について尋ねてください。
"""))
        
        response = await self.llm.ainvoke(messages)
        return response.content

