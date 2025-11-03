"use client"

import { useEffect, useState } from 'react'
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    const savedTheme = window.localStorage.getItem('theme')
    const shouldUseDark = savedTheme ? savedTheme === 'dark' : prefersDark
    setIsDarkMode(shouldUseDark)
  }, [])

  useEffect(() => {
    const root = document.documentElement
    if (isDarkMode) {
      root.classList.add('dark')
      window.localStorage.setItem('theme', 'dark')
    } else {
      root.classList.remove('dark')
      window.localStorage.setItem('theme', 'light')
    }
  }, [isDarkMode])

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768
      setIsMobile(mobile)
      setIsSidebarOpen(!mobile)
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

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
    const trimmed = content.trim()
    if (!trimmed) return

    // ユーザーメッセージを追加
    const userMessage: Message = {
      role: 'user',
      content: trimmed
    }
    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setIsLoading(true)

    // コンテキスト情報を抽出・更新
    const extractedInfo = extractProjectInfo(trimmed)
    const updatedContext = { ...context, ...extractedInfo }
    setContext(updatedContext)

    try {
      // APIにリクエスト
      const request: ChatRequest = {
        messages: updatedMessages.map(m => ({
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

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev)
  const toggleDarkMode = () => setIsDarkMode(prev => !prev)

  const formatBoolean = (value: boolean | undefined, positive: string, negative: string) => {
    if (value === undefined) return '未設定'
    return value ? positive : negative
  }

  const contextSummary = [
    { label: '物件名', value: context?.property_name || '未設定' },
    { label: '部屋名', value: context?.room_name || '未設定' },
    { label: '天井高', value: context?.ceiling_height ? `${context.ceiling_height} m` : '未設定' },
    { label: '案件タイプ', value: context?.project_type || '未設定' },
    { label: '特殊環境', value: formatBoolean(context?.special_environment, 'あり', 'なし') },
    { label: '調光', value: formatBoolean(context?.dimming, '可能', '不要') },
    { label: '調色', value: formatBoolean(context?.color_temperature, '可能', '不要') },
    { label: '図面からの印象', value: context?.impression || '未設定' },
  ]

  const showOverlay = isSidebarOpen && isMobile

  return (
    <main className="flex h-screen overflow-hidden bg-gray-100 text-gray-900 transition-colors duration-300 dark:bg-gray-950 dark:text-gray-100 md:pl-64">
      {showOverlay && (
        <div
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm md:hidden"
          onClick={toggleSidebar}
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-40 flex h-full w-64 flex-col border-r border-gray-200 bg-white/95 backdrop-blur-lg shadow-lg transition-transform duration-300 dark:border-gray-800 dark:bg-gray-900/95 ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0`}
      >
        <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-gray-200 dark:border-gray-800">
          <div>
            <p className="text-xs uppercase tracking-widest text-blue-500">OfficeLightNavi</p>
          </div>
          <button
            type="button"
            onClick={toggleSidebar}
            className="rounded-lg p-2 text-sm text-gray-500 transition hover:bg-gray-100 md:hidden dark:text-gray-300 dark:hover:bg-gray-800"
            aria-label="サイドバーを閉じる"
          >
            ✕
          </button>
        </div>

        <div className="flex h-full flex-col justify-between px-6 py-6">
          <div className="space-y-8 pr-1">

            <section className="space-y-3">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                入力済みの物件情報
              </h2>
              <div className="space-y-2 text-sm">
                {contextSummary.map((item) => (
                  <div
                    key={item.label}
                    className="rounded-lg border border-gray-200 bg-white/60 px-3 py-2 dark:border-gray-800 dark:bg-gray-800/60"
                  >
                    <p className="text-xs text-gray-500 dark:text-gray-400">{item.label}</p>
                    <p className="font-medium text-gray-800 dark:text-gray-100">{item.value}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>

          <div className="mt-6 space-y-3 text-xs text-gray-500 dark:text-gray-400">
            <p>プロジェクトを保存すると、次回から同じ条件で相談できます。</p>
          </div>
        </div>
      </aside>

      <div className="flex h-full flex-1 flex-col overflow-hidden">
        <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-gray-200 bg-white/70 px-4 py-4 shadow-sm backdrop-blur-lg transition dark:border-gray-800 dark:bg-gray-900/70">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={toggleSidebar}
              className="inline-flex items-center justify-center rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 md:hidden dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
            >
              {isSidebarOpen ? '閉じる' : 'メニュー'}
            </button>
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={toggleDarkMode}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:hover:bg-gray-700"
            >
              <span>{isDarkMode ? 'ライトモード' : 'ダークモード'}</span>
            </button>
          </div>
        </header>

        <section className="flex flex-1 min-h-0 flex-col overflow-hidden px-4 py-6 sm:px-8">
          <div className="flex flex-1 min-h-0 flex-col rounded-3xl border border-gray-200 bg-white/90 shadow-lg backdrop-blur-sm transition-colors dark:border-gray-800 dark:bg-gray-900/80">
            <div className="flex-1 min-h-0 space-y-4 overflow-y-auto px-4 py-6 sm:px-8">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="rounded-xl bg-blue-500/10 px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500"></div>
                      <div
                        className="h-2 w-2 animate-bounce rounded-full bg-blue-500"
                        style={{ animationDelay: '0.1s' }}
                      ></div>
                      <div
                        className="h-2 w-2 animate-bounce rounded-full bg-blue-500"
                        style={{ animationDelay: '0.2s' }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div className="border-t border-gray-200 px-4 py-4 sm:px-8 dark:border-gray-800">
              <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}

