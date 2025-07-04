import React from 'react'
import { BellIcon, UserCircleIcon } from '@heroicons/react/24/outline'
import { useWebSocket } from '../../hooks/useWebSocket'

export const Header: React.FC = () => {
  const { isConnected, connectionStatus } = useWebSocket()

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500'
      case 'connecting': return 'bg-yellow-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected'
      case 'connecting': return 'Connecting...'
      case 'error': return 'Connection Error'
      default: return 'Disconnected'
    }
  }

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-2xl font-semibold text-gray-900">
            Smart Contract Security Analysis
          </h2>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getStatusColor()}`}></div>
            <span className="text-sm text-gray-600">{getStatusText()}</span>
          </div>
          
          {/* Notifications */}
          <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <BellIcon className="h-6 w-6" />
          </button>
          
          {/* User Profile */}
          <button className="flex items-center space-x-2 p-2 text-gray-400 hover:text-gray-600 transition-colors">
            <UserCircleIcon className="h-8 w-8" />
            <span className="text-sm font-medium">Security Analyst</span>
          </button>
        </div>
      </div>
    </header>
  )
}
