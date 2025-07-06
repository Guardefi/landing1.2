import React, { useState, useEffect } from 'react'
import { 
  CogIcon, 
  ShieldCheckIcon, 
  ChartBarIcon,
  ServerIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface EngineSettings {
  similarity_threshold: number
  cache_enabled: boolean
  batch_size: number
  max_concurrent_comparisons: number
  neural_network_enabled: boolean
  preprocessing_level: 'basic' | 'advanced' | 'comprehensive'
  threat_detection_sensitivity: 'low' | 'medium' | 'high'
}

interface SystemSettings {
  log_level: 'debug' | 'info' | 'warning' | 'error'
  metrics_retention_days: number
  max_api_rate_limit: number
  websocket_enabled: boolean
}

export const Settings: React.FC = () => {
  const [engineSettings, setEngineSettings] = useState<EngineSettings>({
    similarity_threshold: 0.8,
    cache_enabled: true,
    batch_size: 10,
    max_concurrent_comparisons: 5,
    neural_network_enabled: true,
    preprocessing_level: 'advanced',
    threat_detection_sensitivity: 'medium'
  })

  const [systemSettings, setSystemSettings] = useState<SystemSettings>({
    log_level: 'info',
    metrics_retention_days: 30,
    max_api_rate_limit: 1000,
    websocket_enabled: true
  })

  const [isSaving, setIsSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle')

  useEffect(() => {
    // Load settings from API
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      // Mock loading settings - replace with actual API call
      console.log('Loading settings from API...')
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  const handleSaveSettings = async () => {
    setIsSaving(true)
    setSaveStatus('idle')

    try {
      // Mock API call - replace with actual implementation
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const payload = {
        engine: engineSettings,
        system: systemSettings
      }
      
      console.log('Saving settings:', payload)
      
      setSaveStatus('success')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } catch (error) {
      console.error('Failed to save settings:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    } finally {
      setIsSaving(false)
    }
  }

  const handleEngineSettingChange = <K extends keyof EngineSettings>(
    key: K,
    value: EngineSettings[K]
  ) => {
    setEngineSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSystemSettingChange = <K extends keyof SystemSettings>(
    key: K,
    value: SystemSettings[K]
  ) => {
    setSystemSettings(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <div className="flex items-center space-x-3">
          {saveStatus === 'success' && (
            <div className="flex items-center text-green-600">
              <CheckIcon className="h-5 w-5 mr-1" />
              <span className="text-sm">Settings saved</span>
            </div>
          )}
          {saveStatus === 'error' && (
            <div className="flex items-center text-red-600">
              <ExclamationTriangleIcon className="h-5 w-5 mr-1" />
              <span className="text-sm">Save failed</span>
            </div>
          )}
          <button
            onClick={handleSaveSettings}
            disabled={isSaving}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Engine Settings */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center">
              <CogIcon className="h-6 w-6 text-primary-600 mr-3" />
              <h2 className="text-lg font-medium text-gray-900">Engine Configuration</h2>
            </div>
          </div>
          <div className="px-6 py-4 space-y-6">
            {/* Similarity Threshold */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Similarity Threshold
              </label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.01"
                value={engineSettings.similarity_threshold}
                onChange={(e) => handleEngineSettingChange('similarity_threshold', parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0.1</span>
                <span className="font-medium">{engineSettings.similarity_threshold.toFixed(2)}</span>
                <span>1.0</span>
              </div>
            </div>

            {/* Cache Settings */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={engineSettings.cache_enabled}
                  onChange={(e) => handleEngineSettingChange('cache_enabled', e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">Enable Caching</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">Cache comparison results for improved performance</p>
            </div>

            {/* Batch Size */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Batch Size
              </label>
              <select
                value={engineSettings.batch_size}
                onChange={(e) => handleEngineSettingChange('batch_size', parseInt(e.target.value))}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>

            {/* Max Concurrent Comparisons */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Concurrent Comparisons
              </label>
              <select
                value={engineSettings.max_concurrent_comparisons}
                onChange={(e) => handleEngineSettingChange('max_concurrent_comparisons', parseInt(e.target.value))}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value={1}>1</option>
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={10}>10</option>
              </select>
            </div>

            {/* Neural Network */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={engineSettings.neural_network_enabled}
                  onChange={(e) => handleEngineSettingChange('neural_network_enabled', e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">Enable Neural Network Analysis</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">Use Siamese neural network for enhanced similarity detection</p>
            </div>

            {/* Preprocessing Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preprocessing Level
              </label>
              <select
                value={engineSettings.preprocessing_level}
                onChange={(e) => handleEngineSettingChange('preprocessing_level', e.target.value as EngineSettings['preprocessing_level'])}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="basic">Basic</option>
                <option value="advanced">Advanced</option>
                <option value="comprehensive">Comprehensive</option>
              </select>
            </div>

            {/* Threat Detection Sensitivity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Threat Detection Sensitivity
              </label>
              <select
                value={engineSettings.threat_detection_sensitivity}
                onChange={(e) => handleEngineSettingChange('threat_detection_sensitivity', e.target.value as EngineSettings['threat_detection_sensitivity'])}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
        </div>

        {/* System Settings */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center">
              <ServerIcon className="h-6 w-6 text-primary-600 mr-3" />
              <h2 className="text-lg font-medium text-gray-900">System Configuration</h2>
            </div>
          </div>
          <div className="px-6 py-4 space-y-6">
            {/* Log Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Log Level
              </label>
              <select
                value={systemSettings.log_level}
                onChange={(e) => handleSystemSettingChange('log_level', e.target.value as SystemSettings['log_level'])}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>

            {/* Metrics Retention */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Metrics Retention (days)
              </label>
              <input
                type="number"
                min="1"
                max="365"
                value={systemSettings.metrics_retention_days}
                onChange={(e) => handleSystemSettingChange('metrics_retention_days', parseInt(e.target.value))}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>

            {/* API Rate Limit */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Rate Limit (requests/hour)
              </label>
              <input
                type="number"
                min="100"
                max="10000"
                step="100"
                value={systemSettings.max_api_rate_limit}
                onChange={(e) => handleSystemSettingChange('max_api_rate_limit', parseInt(e.target.value))}
                className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>

            {/* WebSocket */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={systemSettings.websocket_enabled}
                  onChange={(e) => handleSystemSettingChange('websocket_enabled', e.target.checked)}
                  className="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">Enable WebSocket Real-time Updates</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">Real-time monitoring and notifications</p>
            </div>
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <ChartBarIcon className="h-6 w-6 text-primary-600 mr-3" />
            <h2 className="text-lg font-medium text-gray-900">System Information</h2>
          </div>
        </div>
        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Version</dt>
              <dd className="mt-1 text-sm text-gray-900">SCORPIUS v1.0.0</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Build</dt>
              <dd className="mt-1 text-sm text-gray-900">Enterprise Edition</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Python Version</dt>
              <dd className="mt-1 text-sm text-gray-900">3.11.0</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">PyTorch Version</dt>
              <dd className="mt-1 text-sm text-gray-900">2.1.0</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd className="mt-1 text-sm text-gray-900">{new Date().toLocaleDateString()}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">License</dt>
              <dd className="mt-1 text-sm text-gray-900">Enterprise</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}
