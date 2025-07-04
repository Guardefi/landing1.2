import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { Dashboard } from './pages/Dashboard'
import { BytecodeAnalyzer } from './pages/BytecodeAnalyzer'
import { RealTimeMonitor } from './pages/RealTimeMonitor'
import { Settings } from './pages/Settings'
import { useWebSocket } from './hooks/useWebSocket'
import { WebSocketProvider } from './contexts/WebSocketContext'

function App() {
  return (
    <WebSocketProvider>
      <div className="min-h-screen bg-secondary-50 flex">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto">
            <div className="container mx-auto px-6 py-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/analyzer" element={<BytecodeAnalyzer />} />
                <Route path="/monitor" element={<RealTimeMonitor />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </WebSocketProvider>
  )
}

export default App
