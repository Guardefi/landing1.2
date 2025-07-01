import React, { useState, useEffect } from 'react'
import { 
  ChartBarIcon, 
  ClockIcon, 
  ServerIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import { useWebSocket } from '../hooks/useWebSocket'

interface SystemMetrics {
  timestamp: string
  cpu_usage: number
  memory_usage: number
  active_connections: number
  requests_per_minute: number
  response_time: number
}

interface AlertMessage {
  id: string
  type: 'info' | 'warning' | 'error'
  message: string
  timestamp: string
}

export const RealTimeMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics[]>([])
  const [alerts, setAlerts] = useState<AlertMessage[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)

  const { isConnected, lastMessage } = useWebSocket({
    onMessage: (message) => {
      if (message.type === 'system_metrics') {
        setMetrics(prev => [...prev.slice(-19), message.data]) // Keep last 20 points
      } else if (message.type === 'alert') {
        setAlerts(prev => [message.data, ...prev.slice(0, 9)]) // Keep last 10 alerts
      }
    },
    onConnect: () => {
      setIsMonitoring(true)
    },
    onDisconnect: () => {
      setIsMonitoring(false)
    }
  })

  useEffect(() => {
    // Simulate initial data
    const initialMetrics: SystemMetrics[] = Array.from({ length: 10 }, (_, i) => ({
      timestamp: new Date(Date.now() - (9 - i) * 60000).toISOString(),
      cpu_usage: Math.random() * 80 + 10,
      memory_usage: Math.random() * 70 + 20,
      active_connections: Math.floor(Math.random() * 100) + 50,
      requests_per_minute: Math.floor(Math.random() * 500) + 100,
      response_time: Math.random() * 200 + 50
    }))
    setMetrics(initialMetrics)

    const initialAlerts: AlertMessage[] = [
      {
        id: '1',
        type: 'info',
        message: 'System monitoring started',
        timestamp: new Date().toISOString()
      },
      {
        id: '2',
        type: 'warning',
        message: 'High CPU usage detected on analysis node',
        timestamp: new Date(Date.now() - 1800000).toISOString()
      }
    ]
    setAlerts(initialAlerts)
  }, [])

  const getLatestMetric = () => {
    return metrics[metrics.length - 1] || {
      timestamp: new Date().toISOString(),
      cpu_usage: 0,
      memory_usage: 0,
      active_connections: 0,
      requests_per_minute: 0,
      response_time: 0
    }
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
      default:
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />
    }
  }

  const getAlertColorClass = (type: string) => {
    switch (type) {
      case 'error':
        return 'border-red-200 bg-red-50'
      case 'warning':
        return 'border-yellow-200 bg-yellow-50'
      default:
        return 'border-blue-200 bg-blue-50'
    }
  }

  const latest = getLatestMetric()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Real-time Monitor</h1>
        <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
          isMonitoring ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            isMonitoring ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <span>{isMonitoring ? 'Monitoring Active' : 'Monitoring Offline'}</span>
        </div>
      </div>

      {/* Real-time Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ServerIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">CPU Usage</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {latest.cpu_usage.toFixed(1)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Memory Usage</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {latest.memory_usage.toFixed(1)}%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ServerIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Connections</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {latest.active_connections}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Requests/min</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {latest.requests_per_minute}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Response Time</dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {latest.response_time.toFixed(0)}ms
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart Placeholder */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Trends</h3>
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400 mb-2" />
              <p className="text-gray-500">Chart visualization would be rendered here</p>
              <p className="text-sm text-gray-400">Integration with charting library needed</p>
            </div>
          </div>
        </div>

        {/* System Alerts */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Alerts</h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {alerts.length > 0 ? (
              alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`border rounded-lg p-3 ${getAlertColorClass(alert.type)}`}
                >
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      {getAlertIcon(alert.type)}
                    </div>
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">
                        {alert.message}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(alert.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <CheckCircleIcon className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                <p className="text-gray-500">No alerts at this time</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-green-800">Similarity Engine</p>
              <p className="text-xs text-green-600">Operational</p>
            </div>
            <CheckCircleIcon className="h-6 w-6 text-green-500" />
          </div>
          
          <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-green-800">Neural Network</p>
              <p className="text-xs text-green-600">Operational</p>
            </div>
            <CheckCircleIcon className="h-6 w-6 text-green-500" />
          </div>
          
          <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-green-800">Cache System</p>
              <p className="text-xs text-green-600">Operational</p>
            </div>
            <CheckCircleIcon className="h-6 w-6 text-green-500" />
          </div>
        </div>
      </div>
    </div>
  )
}
