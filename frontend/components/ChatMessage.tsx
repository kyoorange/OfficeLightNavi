"use client"

import { Message } from '@/app/types/chat'

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div
        className={`max-w-3xl rounded-2xl px-4 py-3 shadow-sm transition-colors ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-100'
        }`}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        
        {message.thinking && (
          <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
            <div className="text-sm font-semibold mb-1">思考プロセス:</div>
            <div className="text-sm opacity-80 italic">{message.thinking}</div>
          </div>
        )}
        
        {message.candidates && message.candidates.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
            <div className="text-sm font-semibold mb-2">候補機種:</div>
            <div className="space-y-2">
              {message.candidates.slice(0, 5).map((candidate: any, index: number) => (
                <div
                  key={index}
                  className="text-sm rounded-lg p-2 bg-white/70 text-gray-800 dark:bg-gray-800 dark:text-gray-50"
                >
                  <div className="font-medium">{candidate.name}</div>
                  <div className="text-xs opacity-90">
                    {candidate.manufacturer} - {candidate.series}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

