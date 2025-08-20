import React from 'react'
import { PlusCircle, MessageSquare, BookOpen, TrendingUp, Users, DollarSign } from 'lucide-react'
import { useChat } from '../contexts/ChatContext'

const Sidebar: React.FC = () => {
  const { dispatch } = useChat()

  const handleNewChat = () => {
    dispatch({ type: 'CLEAR_MESSAGES' })
  }

  const quickTopics = [
    { icon: DollarSign, label: 'Pricing & Offers', query: 'How should I price my services?' },
    { icon: TrendingUp, label: 'Lead Generation', query: 'What are the best ways to generate leads?' },
    { icon: Users, label: 'Sales Process', query: 'How can I improve my sales process?' },
    { icon: BookOpen, label: 'Business Strategy', query: 'What business strategy should I focus on?' },
  ]

  const handleQuickTopic = (query: string) => {
    // This will be implemented when we have the chat functionality
    console.log('Quick topic clicked:', query)
  }

  return (
    <aside className="w-80 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4">
        <button 
          onClick={handleNewChat}
          className="w-full flex items-center space-x-3 px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
        >
          <PlusCircle className="w-5 h-5" />
          <span className="font-medium">New Conversation</span>
        </button>
      </div>

      <div className="px-4 pb-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Quick Topics</h3>
        <div className="space-y-2">
          {quickTopics.map((topic, index) => (
            <button
              key={index}
              onClick={() => handleQuickTopic(topic.query)}
              className="w-full flex items-center space-x-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors text-left"
            >
              <topic.icon className="w-4 h-4 text-gray-500" />
              <span className="text-sm">{topic.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 px-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Recent Conversations</h3>
        <div className="space-y-2">
          <div className="flex items-center space-x-3 px-3 py-2 bg-gray-50 rounded-lg">
            <MessageSquare className="w-4 h-4 text-gray-500" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-900 truncate">Current Session</p>
              <p className="text-xs text-gray-500">Just now</p>
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <p className="mb-1">Powered by Alex Hormozi's teachings</p>
          <p>AI-generated advice for educational purposes</p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar

