import React, { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { Source } from '../contexts/ChatContext'

interface SourceCitationsProps {
  sources: Source[]
}

const SourceCitations: React.FC<SourceCitationsProps> = ({ sources }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-3 max-w-full">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center space-x-2 text-xs text-gray-600 hover:text-gray-800 transition-colors"
      >
        <BookOpen className="w-3 h-3" />
        <span>{sources.length} source{sources.length > 1 ? 's' : ''}</span>
        {isExpanded ? (
          <ChevronUp className="w-3 h-3" />
        ) : (
          <ChevronDown className="w-3 h-3" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-2">
          {sources.map((source, index) => (
            <div
              key={index}
              className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="font-medium text-gray-900">
                  {source.book}
                  {source.chapter && (
                    <span className="text-gray-600 font-normal"> - {source.chapter}</span>
                  )}
                </div>
                {source.page > 0 && (
                  <div className="text-gray-500 text-xs">
                    Page {source.page}
                  </div>
                )}
              </div>
              
              {source.text_snippet && (
                <div className="text-gray-700 italic">
                  "{source.text_snippet}"
                </div>
              )}
              
              <div className="mt-2 flex items-center justify-between">
                <div className="text-gray-500">
                  Citation {index + 1}
                </div>
                <button className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 transition-colors">
                  <ExternalLink className="w-3 h-3" />
                  <span>View Source</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SourceCitations

