import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface ChatResponse {
  response: string
  sources: Array<{
    book: string
    chapter: string
    page: number
    text_snippet: string
  }>
  conversation_id: string
}

export interface BookInfo {
  title: string
  author: string
  chapters: string[]
  status: string
}

export const sendMessage = async (
  message: string, 
  conversationId?: string | null
): Promise<ChatResponse> => {
  const response = await api.post('/chat', {
    message,
    conversation_id: conversationId,
  })
  return response.data
}

export const getAvailableBooks = async (): Promise<{ books: BookInfo[] }> => {
  const response = await api.get('/books')
  return response.data
}

export const performSemanticSearch = async (
  query: string,
  limit: number = 5
): Promise<{
  query: string
  results: any[]
  message: string
}> => {
  const response = await api.post('/search', null, {
    params: { query, limit }
  })
  return response.data
}

export const checkHealth = async (): Promise<{
  status: string
  message: string
}> => {
  const response = await api.get('/health')
  return response.data
}

export default api

