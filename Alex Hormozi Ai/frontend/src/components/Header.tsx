import React from 'react'
import { MessageCircle, BookOpen, Settings } from 'lucide-react'

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6">
      <div className="flex items-center space-x-3">
        <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
          <MessageCircle className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-gray-900">Hormozi AI</h1>
          <p className="text-sm text-gray-500">Business Advisor</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <button className="flex items-center space-x-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
          <BookOpen className="w-5 h-5" />
          <span className="text-sm font-medium">Knowledge Base</span>
        </button>
        
        <button className="flex items-center justify-center w-10 h-10 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
          <Settings className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}

export default Header

