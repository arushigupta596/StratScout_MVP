import { ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Target, TrendingUp, Lightbulb, MessageSquare, FileText, LogOut } from 'lucide-react'
import clsx from 'clsx'
import { useAuth } from '../contexts/AuthContext'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Report', href: '/dashboard', icon: FileText },
  { name: 'Predictions', href: '/predictions', icon: TrendingUp },
  { name: 'Gap Analysis', href: '/gaps', icon: Target },
  { name: 'Scout AI', href: '/scout', icon: MessageSquare },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { signOut, user } = useAuth()

  const handleSignOut = () => {
    signOut()
    navigate('/signin')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center h-16 px-6 border-b border-gray-200">
            <Lightbulb className="w-8 h-8 text-primary-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">StratScout</span>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors',
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            {user && (
              <div className="mb-3 px-2">
                <p className="text-xs text-gray-500 truncate">{user.email}</p>
              </div>
            )}
            <button
              onClick={handleSignOut}
              className="w-full flex items-center justify-center px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sign out
            </button>
            <p className="text-xs text-gray-500 text-center mt-3">
              StratScout MVP v1.0
            </p>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="min-h-screen">
          {children}
        </main>
      </div>
    </div>
  )
}
