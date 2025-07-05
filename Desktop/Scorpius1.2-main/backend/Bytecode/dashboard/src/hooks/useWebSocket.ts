import { useEffect, useState } from 'react'
import { useWebSocketContext } from '../contexts/WebSocketContext'

interface UseWebSocketOptions {
  onMessage?: (message: any) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const { socket, isConnected, lastMessage, sendMessage, connectionStatus } = useWebSocketContext()
  const [messages, setMessages] = useState<any[]>([])

  useEffect(() => {
    if (lastMessage && options.onMessage) {
      options.onMessage(lastMessage)
    }
    
    if (lastMessage) {
      setMessages(prev => [...prev, lastMessage])
    }
  }, [lastMessage, options.onMessage])

  useEffect(() => {
    if (isConnected && options.onConnect) {
      options.onConnect()
    }
  }, [isConnected, options.onConnect])

  useEffect(() => {
    if (!isConnected && connectionStatus === 'disconnected' && options.onDisconnect) {
      options.onDisconnect()
    }
  }, [isConnected, connectionStatus, options.onDisconnect])

  const clearMessages = () => {
    setMessages([])
  }

  const subscribe = (messageType: string, callback: (data: any) => void) => {
    useEffect(() => {
      if (lastMessage && lastMessage.type === messageType) {
        callback(lastMessage.data)
      }
    }, [lastMessage, messageType, callback])
  }

  return {
    socket,
    isConnected,
    connectionStatus,
    messages,
    lastMessage,
    sendMessage,
    clearMessages,
    subscribe
  }
}

export default useWebSocket
