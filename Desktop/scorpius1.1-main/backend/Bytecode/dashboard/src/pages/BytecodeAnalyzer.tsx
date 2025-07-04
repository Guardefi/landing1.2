import React, { useState } from 'react'
import { DocumentTextIcon, ArrowPathIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline'

interface ComparisonResult {
  similarity_score: number
  jaccard_similarity: number
  cosine_similarity: number
  semantic_similarity: number
  threat_assessment: {
    level: 'low' | 'medium' | 'high'
    confidence: number
    indicators: string[]
  }
  execution_time: number
}

export const BytecodeAnalyzer: React.FC = () => {
  const [bytecode1, setBytecode1] = useState('')
  const [bytecode2, setBytecode2] = useState('')
  const [isComparing, setIsComparing] = useState(false)
  const [result, setResult] = useState<ComparisonResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleCompare = async () => {
    if (!bytecode1.trim() || !bytecode2.trim()) {
      setError('Please provide both bytecode samples')
      return
    }

    setIsComparing(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/compare', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bytecode1: bytecode1.trim(),
          bytecode2: bytecode2.trim(),
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during comparison')
    } finally {
      setIsComparing(false)
    }
  }

  const handleClear = () => {
    setBytecode1('')
    setBytecode2('')
    setResult(null)
    setError(null)
  }

  const loadSampleData = () => {
    setBytecode1('608060405234801561001057600080fd5b5060c78061001f6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c80636d4ce63c146037578063b43f15731460535760405162461bcd60e51b815260040160405180910390fd5b60005460405190815260200160405180910390f35b606081600055806000556040517f28ca10e5bf7979fdac94fbf3b4cea4b3...')
    setBytecode2('608060405234801561001057600080fd5b5060c78061001f6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c80636d4ce63c146037578063b43f15731460535760405162461bcd60e51b815260040160405180910390fd5b60005460405190815260200160405180910390f35b606081600055806000556040517f28ca10e5bf7979fdac94fbf3b4cea4b4...')
  }

  const getThreatColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-600 bg-red-100 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200'
      default: return 'text-green-600 bg-green-100 border-green-200'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Bytecode Analyzer</h1>
        <button
          onClick={loadSampleData}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <DocumentTextIcon className="h-4 w-4 mr-2" />
          Load Sample Data
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-4">
          <div>
            <label htmlFor="bytecode1" className="block text-sm font-medium text-gray-700 mb-2">
              Bytecode 1
            </label>
            <textarea
              id="bytecode1"
              rows={12}
              className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm font-mono"
              placeholder="Enter the first bytecode sample (hex format)..."
              value={bytecode1}
              onChange={(e) => setBytecode1(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="bytecode2" className="block text-sm font-medium text-gray-700 mb-2">
              Bytecode 2
            </label>
            <textarea
              id="bytecode2"
              rows={12}
              className="block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm font-mono"
              placeholder="Enter the second bytecode sample (hex format)..."
              value={bytecode2}
              onChange={(e) => setBytecode2(e.target.value)}
            />
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleCompare}
              disabled={isComparing || !bytecode1.trim() || !bytecode2.trim()}
              className="flex-1 inline-flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isComparing ? (
                <>
                  <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Compare Bytecodes'
              )}
            </button>
            <button
              onClick={handleClear}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          <h2 className="text-lg font-medium text-gray-900">Analysis Results</h2>
          
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <ExclamationCircleIcon className="h-5 w-5 text-red-400" />
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Overall Similarity Score */}
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Overall Similarity</h3>
                  <CheckCircleIcon className="h-6 w-6 text-green-500" />
                </div>
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {(result.similarity_score * 100).toFixed(2)}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${result.similarity_score * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Detailed Metrics */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Detailed Metrics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Jaccard Similarity</span>
                    <span className="text-sm font-medium">{(result.jaccard_similarity * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Cosine Similarity</span>
                    <span className="text-sm font-medium">{(result.cosine_similarity * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Semantic Similarity</span>
                    <span className="text-sm font-medium">{(result.semantic_similarity * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Execution Time</span>
                    <span className="text-sm font-medium">{result.execution_time.toFixed(0)}ms</span>
                  </div>
                </div>
              </div>

              {/* Threat Assessment */}
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Threat Assessment</h3>
                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mb-3 ${getThreatColor(result.threat_assessment.level)}`}>
                  {result.threat_assessment.level.toUpperCase()}
                </div>
                <div className="text-sm text-gray-600 mb-3">
                  Confidence: {(result.threat_assessment.confidence * 100).toFixed(1)}%
                </div>
                {result.threat_assessment.indicators.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Risk Indicators</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {result.threat_assessment.indicators.map((indicator, index) => (
                        <li key={index} className="text-sm text-gray-600">{indicator}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {!result && !error && !isComparing && (
            <div className="bg-gray-50 rounded-lg p-8 text-center">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-500">Enter bytecode samples above and click "Compare Bytecodes" to see analysis results.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
