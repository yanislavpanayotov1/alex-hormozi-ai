import React, { createContext, useContext, useReducer, ReactNode } from 'react'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  sources?: Source[]
  isTyping?: boolean
}

export interface Source {
  book: string
  chapter: string
  page: number
  text_snippet: string
}

interface ChatState {
  messages: Message[]
  isLoading: boolean
  currentConversationId: string | null
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_TYPING'; payload: { messageId: string; isTyping: boolean } }
  | { type: 'UPDATE_MESSAGE'; payload: { id: string; content: string; sources?: Source[] } }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'SET_CONVERSATION_ID'; payload: string }

const initialState: ChatState = {
  messages: [
    {
      id: '1',
      content: "Hello! I'm your AI business advisor trained on Alex Hormozi's teachings. I can help you with questions about offers, lead generation, sales, marketing, and business operations. What would you like to know?",
      role: 'assistant',
      timestamp: new Date(),
      sources: []
    }
  ],
  isLoading: false,
  currentConversationId: null
}

const chatReducer = (state: ChatState, action: ChatAction): ChatState => {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload]
      }
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      }
    case 'SET_TYPING':
      return {
        ...state,
        messages: state.messages.map(msg =>
          msg.id === action.payload.messageId
            ? { ...msg, isTyping: action.payload.isTyping }
            : msg
        )
      }
    case 'UPDATE_MESSAGE':
      return {
        ...state,
        messages: state.messages.map(msg =>
          msg.id === action.payload.id
            ? { ...msg, content: action.payload.content, sources: action.payload.sources, isTyping: false }
            : msg
        )
      }
    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: [initialState.messages[0]]
      }
    case 'SET_CONVERSATION_ID':
      return {
        ...state,
        currentConversationId: action.payload
      }
    default:
      return state
  }
}

const ChatContext = createContext<{
  state: ChatState
  dispatch: React.Dispatch<ChatAction>
} | null>(null)

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState)

  return (
    <ChatContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatContext.Provider>
  )
}

export const useChat = () => {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}

