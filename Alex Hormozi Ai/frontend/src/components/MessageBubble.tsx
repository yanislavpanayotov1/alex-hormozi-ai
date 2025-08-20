import React from 'react'
import { User, Bot, BookOpen, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { Message } from '../contexts/ChatContext'
import TypingIndicator from './TypingIndicator'
import SourceCitations from './SourceCitations'

interface MessageBubbleProps {
  message: Message
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-primary-600 text-white' 
            : 'bg-gray-200 text-gray-600'
        }`}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-4 py-3 rounded-lg ${
            isUser 
              ? 'bg-primary-600 text-white' 
              : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
          }`}>
            {message.isTyping ? (
              <TypingIndicator />
            ) : (
              <div className="prose prose-sm max-w-none">
                {isUser ? (
                  <p className="m-0 whitespace-pre-wrap">{message.content}</p>
                ) : (
                  <ReactMarkdown
                    className="m-0"
                    components={{
                      p: ({ children }) => <p className="m-0 mb-2 last:mb-0">{children}</p>,
                      ul: ({ children }) => <ul className="m-0 mb-2 last:mb-0 pl-4">{children}</ul>,
                      ol: ({ children }) => <ol className="m-0 mb-2 last:mb-0 pl-4">{children}</ol>,
                      li: ({ children }) => <li className="mb-1">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      em: ({ children }) => <em className="italic">{children}</em>,
                      code: ({ children }) => (
                        <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm">
                          {children}
                        </code>
                      ),
                      pre: ({ children }) => (
                        <pre className="bg-gray-100 text-gray-800 p-3 rounded mt-2 overflow-x-auto">
                          {children}
                        </pre>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                )}
              </div>
            )}
          </div>

          {/* Timestamp */}
          <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
            {message.timestamp.toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>

          {/* Source Citations for AI messages */}
          {!isUser && message.sources && message.sources.length > 0 && !message.isTyping && (
            <SourceCitations sources={message.sources} />
          )}
        </div>
      </div>
    </div>
  )
}

export default MessageBubble

