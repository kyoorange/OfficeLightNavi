"use client"

import { Message } from '@/app/types/chat'

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-3xl rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 text-gray-800'
        }`}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        
        {message.thinking && (
          <div className="mt-2 pt-2 border-t border-gray-300">
            <div className="text-sm font-semibold mb-1">思考プロセス:</div>
            <div className="text-sm opacity-80 italic">{message.thinking}</div>
          </div>
        )}
        
        {message.candidates && message.candidates.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-300">
            <div className="text-sm font-semibold mb-2">候補機種:</div>
            <div className="space-y-1">
              {message.candidates.slice(0, 5).map((candidate: any, index: number) => (
                <div key={index} className="text-sm bg-white bg-opacity-20 rounded p-2">
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

