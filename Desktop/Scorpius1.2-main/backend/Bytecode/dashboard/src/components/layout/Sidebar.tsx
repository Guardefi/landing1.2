import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  CodeBracketIcon, 
  ChartBarIcon, 
  CogIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Bytecode Analyzer', href: '/analyzer', icon: CodeBracketIcon },
  { name: 'Real-time Monitor', href: '/monitor', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: CogIcon },
]

export const Sidebar: React.FC = () => {
  const location = useLocation()

  return (
    <div className="bg-primary-900 text-white w-64 min-h-screen p-4">
      <div className="flex items-center mb-8">
        <ShieldCheckIcon className="h-8 w-8 text-accent-400 mr-3" />
        <div>
          <h1 className="text-xl font-bold">SCORPIUS</h1>
          <p className="text-xs text-primary-300">Bytecode Security Engine</p>
        </div>
      </div>
      
      <nav className="space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-700 text-white'
                  : 'text-primary-300 hover:bg-primary-800 hover:text-white'
              }`}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      <div className="mt-8 pt-8 border-t border-primary-700">
        <div className="text-xs text-primary-400">
          <p>Version 1.0.0</p>
          <p className="mt-1">Enterprise Edition</p>
        </div>
      </div>
    </div>
  )
}
