import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { useChat } from '../contexts/ChatContext'
import MessageBubble from './MessageBubble'
import { sendMessage } from '../services/api'

const ChatInterface: React.FC = () => {
  const { state, dispatch } = useChat()
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [state.messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim() || state.isLoading) return

    const userMessage = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      role: 'user' as const,
      timestamp: new Date()
    }

    dispatch({ type: 'ADD_MESSAGE', payload: userMessage })
    dispatch({ type: 'SET_LOADING', payload: true })
    setInputValue('')

    // Add typing indicator
    const typingMessage = {
      id: `typing-${Date.now()}`,
      content: '',
      role: 'assistant' as const,
      timestamp: new Date(),
      isTyping: true
    }
    dispatch({ type: 'ADD_MESSAGE', payload: typingMessage })

    try {
      const response = await sendMessage(inputValue.trim(), state.currentConversationId)
      
      // Update the typing message with the actual response
      dispatch({ 
        type: 'UPDATE_MESSAGE', 
        payload: { 
          id: typingMessage.id, 
          content: response.response,
          sources: response.sources 
        }
      })
      
      if (response.conversation_id) {
        dispatch({ type: 'SET_CONVERSATION_ID', payload: response.conversation_id })
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      dispatch({ 
        type: 'UPDATE_MESSAGE', 
        payload: { 
          id: typingMessage.id, 
          content: "I apologize, but I'm having trouble connecting to the server right now. Please try again in a moment."
        }
      })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [inputValue])

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {state.messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 bg-white p-6">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="flex items-end space-x-4">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask me anything about business, offers, leads, sales, or operations..."
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 scrollbar-thin"
                rows={1}
                style={{ minHeight: '48px', maxHeight: '120px' }}
                disabled={state.isLoading}
              />
              <div className="absolute right-3 bottom-3 text-xs text-gray-400">
                {inputValue.length > 0 && `${inputValue.length} chars`}
              </div>
            </div>
            <button
              type="submit"
              disabled={!inputValue.trim() || state.isLoading}
              className="flex items-center justify-center w-12 h-12 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
            >
              {state.isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
          
          <div className="mt-2 text-xs text-gray-500 text-center">
            Press Enter to send, Shift+Enter for new line. AI responses are for educational purposes.
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface

