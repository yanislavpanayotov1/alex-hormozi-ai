import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ChatInterface from './components/ChatInterface'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import { ChatProvider } from './contexts/ChatContext'

const App: React.FC = () => {
  return (
    <ChatProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <div className="flex h-[calc(100vh-4rem)]">
            <Sidebar />
            <main className="flex-1 overflow-hidden">
              <Routes>
                <Route path="/" element={<ChatInterface />} />
                <Route path="/chat" element={<ChatInterface />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </ChatProvider>
  )
}

export default App

