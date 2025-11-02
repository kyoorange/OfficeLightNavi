"use client"

import { useState, FormEvent } from 'react'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
}

export default function ChatInput({ onSendMessage, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('')
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="メッセージを入力..."
        disabled={disabled}
        className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white text-gray-900 dark:bg-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 transition-colors"
      />
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className="px-6 py-3 bg-blue-500 text-white rounded-xl font-medium shadow-sm hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        送信
      </button>
    </form>
  )
}

