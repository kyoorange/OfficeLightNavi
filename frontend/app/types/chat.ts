export interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  thinking?: string
  candidates?: any[]
  search_queries?: string[]
  metadata?: any
}

export interface ChatRequest {
  messages: Message[]
  context?: {
    property_name?: string
    room_name?: string
    ceiling_height?: number
    impression?: string
    project_type?: string
    special_environment?: boolean
    dimming?: boolean
    color_temperature?: boolean
  }
}

export interface ChatResponse {
  message: string
  thinking?: string
  search_queries?: string[]
  candidates?: any[]
  metadata?: any
}

