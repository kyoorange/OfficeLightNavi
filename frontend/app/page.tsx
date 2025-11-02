"use client"

import { useState } from 'react'
import ChatMessage from '@/components/ChatMessage'
import ChatInput from '@/components/ChatInput'
import { Message, ChatRequest, ChatResponse } from '@/app/types/chat'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'こんにちは！施設照明器具の選定を支援いたします。\n\n物件情報（物件名、部屋名、天井高、図面からの印象など）をお教えください。'
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [context, setContext] = useState<ChatRequest['context']>({})

  const extractProjectInfo = (text: string): Partial<ChatRequest['context']> => {
    const info: Partial<ChatRequest['context']> = {}
    
    // 物件名の抽出
    const propertyMatch = text.match(/物件名[：:]\s*(.+)/)
    if (propertyMatch) info.property_name = propertyMatch[1].trim()
    
    // 部屋名の抽出
    const roomMatch = text.match(/部屋名[：:]\s*(.+)/)
    if (roomMatch) info.room_name = roomMatch[1].trim()
    
    // 天井高の抽出
    const heightMatch = text.match(/天井高[：:]\s*(\d+(?:\.\d+)?)\s*m/)
    if (heightMatch) info.ceiling_height = parseFloat(heightMatch[1])
    
    // 図面からの印象の抽出
    const impressionMatch = text.match(/図面からの印象[：:]\s*(.+)/)
    if (impressionMatch) info.impression = impressionMatch[1].trim()
    
    // 案件タイプの抽出
    if (text.includes('新規見積') || text.includes('デフォルト')) info.project_type = '新規見積'
    if (text.includes('リニューアル')) info.project_type = 'リニューアル'
    if (text.includes('相見積もり')) info.project_type = '相見積もり'
    
    // 特殊環境の抽出
    info.special_environment = text.includes('特殊環境') || text.includes('はい')
    
    // 調光・調色の抽出
    if (text.includes('調光') && !text.includes('不可')) info.dimming = true
    if (text.includes('調色') && !text.includes('不可')) info.color_temperature = true
    
    return info
  }

  const handleSendMessage = async (content: string) => {
    // ユーザーメッセージを追加
    const userMessage: Message = {
      role: 'user',
      content
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    // コンテキスト情報を抽出・更新
    const extractedInfo = extractProjectInfo(content)
    const updatedContext = { ...context, ...extractedInfo }
    setContext(updatedContext)

    try {
      // APIにリクエスト
      const request: ChatRequest = {
        messages: [...messages, userMessage].map(m => ({
          role: m.role,
          content: m.content
        })),
        context: updatedContext
      }

      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        throw new Error(`APIエラー: ${response.status}`)
      }

      const data: ChatResponse = await response.json()

      // アシスタントメッセージを追加
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.message,
        thinking: data.thinking,
        candidates: data.candidates,
        search_queries: data.search_queries,
        metadata: data.metadata
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('エラー:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: `申し訳ございません。エラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}`
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="w-full max-w-4xl">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
          Lighting Agent - 照明器具選定支援
        </h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6 h-[600px] flex flex-col">
          <div className="flex-1 overflow-y-auto mb-4 space-y-4">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 rounded-lg px-4 py-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </main>
  )
}

