import React, { useState, useEffect } from 'react'
import { 
  ShieldCheckIcon, 
  ExclamationTriangleIcon, 
  ClockIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import { useWebSocket } from '../hooks/useWebSocket'

interface SystemStats {
  total_comparisons: number
  cache_hits: number
  cache_misses: number
  active_connections: number
  avg_response_time: number
  threat_level: 'low' | 'medium' | 'high'
}

interface RecentAnalysis {
  id: string
  contract_name: string
  similarity_score: number
  threat_level: 'low' | 'medium' | 'high'
  timestamp: string
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<SystemStats>({
    total_comparisons: 0,
    cache_hits: 0,
    cache_misses: 0,
    active_connections: 0,
    avg_response_time: 0,
    threat_level: 'low'
  })
  
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([])
  const [loading, setLoading] = useState(true)

  const { isConnected, lastMessage } = useWebSocket({
    onMessage: (message) => {
      if (message.type === 'stats_update') {
        setStats(message.data)
      } else if (message.type === 'analysis_complete') {
        setRecentAnalyses(prev => [message.data, ...prev.slice(0, 9)])
      }
    }
  })

  useEffect(() => {
    fetchStats()
    fetchRecentAnalyses()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRecentAnalyses = async () => {
    try {
      // Mock data for now - replace with actual API call
      const mockData: RecentAnalysis[] = [
        {
          id: '1',
          contract_name: 'UniswapV3Pool',
          similarity_score: 0.95,
          threat_level: 'low',
          timestamp: new Date().toISOString()
        },
        {
          id: '2',
          contract_name: 'SuspiciousContract',
          similarity_score: 0.78,
          threat_level: 'high',
          timestamp: new Date(Date.now() - 3600000).toISOString()
        }
      ]
      setRecentAnalyses(mockData)
    } catch (error) {
      console.error('Failed to fetch recent analyses:', error)
    }
  }

  const getThreatColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-600 bg-red-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-green-600 bg-green-100'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Security Dashboard</h1>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {isConnected ? 'Live Monitoring Active' : 'Monitoring Offline'}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ShieldCheckIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Comparisons
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.total_comparisons.toLocaleString()}
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
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Cache Hit Rate
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {((stats.cache_hits / (stats.cache_hits + stats.cache_misses)) * 100).toFixed(1)}%
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
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Avg Response Time
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.avg_response_time.toFixed(0)}ms
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
                <ExclamationTriangleIcon className={`h-6 w-6 ${
                  stats.threat_level === 'high' ? 'text-red-600' :
                  stats.threat_level === 'medium' ? 'text-yellow-600' : 'text-green-600'
                }`} />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Threat Level
                  </dt>
                  <dd className={`text-lg font-medium capitalize ${
                    stats.threat_level === 'high' ? 'text-red-600' :
                    stats.threat_level === 'medium' ? 'text-yellow-600' : 'text-green-600'
                  }`}>
                    {stats.threat_level}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Analyses */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Recent Analyses
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Latest bytecode similarity comparisons and threat assessments
          </p>
        </div>
        <ul className="divide-y divide-gray-200">
          {recentAnalyses.map((analysis) => (
            <li key={analysis.id}>
              <div className="px-4 py-4 flex items-center justify-between">
                <div className="flex items-center">
                  <div className="flex-shrink-0 h-10 w-10">
                    <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <ShieldCheckIcon className="h-6 w-6 text-gray-600" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-sm font-medium text-gray-900">
                      {analysis.contract_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      Similarity: {(analysis.similarity_score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getThreatColor(analysis.threat_level)}`}>
                    {analysis.threat_level}
                  </span>
                  <div className="text-sm text-gray-500">
                    {new Date(analysis.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
