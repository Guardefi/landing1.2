import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

interface WebSocketMessage {
  type: string
  data: any
  timestamp: number
}

interface WebSocketContextType {
  socket: WebSocket | null
  isConnected: boolean
  lastMessage: WebSocketMessage | null
  sendMessage: (message: any) => void
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

interface WebSocketProviderProps {
  children: ReactNode
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')

  useEffect(() => {
    const connect = () => {
      try {
        setConnectionStatus('connecting')
        const ws = new WebSocket('ws://localhost:8000/ws')

        ws.onopen = () => {
          console.log('WebSocket connected')
          setIsConnected(true)
          setConnectionStatus('connected')
          setSocket(ws)
        }

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            const message: WebSocketMessage = {
              type: data.type || 'unknown',
              data: data.data || data,
              timestamp: Date.now()
            }
            setLastMessage(message)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }

        ws.onclose = () => {
          console.log('WebSocket disconnected')
          setIsConnected(false)
          setConnectionStatus('disconnected')
          setSocket(null)
          
          // Attempt to reconnect after 3 seconds
          setTimeout(connect, 3000)
        }

        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          setConnectionStatus('error')
        }

      } catch (error) {
        console.error('Failed to create WebSocket connection:', error)
        setConnectionStatus('error')
        // Retry connection after 5 seconds
        setTimeout(connect, 5000)
      }
    }

    connect()

    return () => {
      if (socket) {
        socket.close()
      }
    }
  }, [])

  const sendMessage = (message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }

  return (
    <WebSocketContext.Provider value={{
      socket,
      isConnected,
      lastMessage,
      sendMessage,
      connectionStatus
    }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider')
  }
  return context
}
