import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import CompetitorDeepDive from './pages/CompetitorDeepDive'
import GapAnalysis from './pages/GapAnalysis'
import Predictions from './pages/Predictions'
import Report from './pages/Report'
import Scout from './pages/Scout'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Report />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/competitor/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <CompetitorDeepDive />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/gaps"
            element={
              <ProtectedRoute>
                <Layout>
                  <GapAnalysis />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/predictions"
            element={
              <ProtectedRoute>
                <Layout>
                  <Predictions />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/report"
            element={
              <ProtectedRoute>
                <Layout>
                  <Report />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/scout"
            element={
              <ProtectedRoute>
                <Layout>
                  <Scout />
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
