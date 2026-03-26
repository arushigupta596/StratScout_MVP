import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { auth } from '../lib/auth'

interface AuthContextType {
  isAuthenticated: boolean
  isLoading: boolean
  user: any | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, name: string) => Promise<void>
  confirmSignUp: (email: string, code: string) => Promise<void>
  signOut: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState<any | null>(null)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const session = await auth.getSession()
      if (session) {
        setIsAuthenticated(true)
        setUser(session.getIdToken().payload)
      }
    } catch {
      setIsAuthenticated(false)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const signIn = async (email: string, password: string) => {
    const result = await auth.signIn({ email, password })
    setIsAuthenticated(true)
    setUser(result.getIdToken().payload)
  }

  const signUp = async (email: string, password: string, name: string) => {
    await auth.signUp({ email, password, name })
  }

  const confirmSignUp = async (email: string, code: string) => {
    await auth.confirmSignUp(email, code)
  }

  const signOut = () => {
    auth.signOut()
    setIsAuthenticated(false)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, user, signIn, signUp, confirmSignUp, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
