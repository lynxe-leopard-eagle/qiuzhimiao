import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import { useThemeStore } from './stores/themeStore'
import ErrorBoundary from './components/ErrorBoundary'
import Navbar from './components/layout/Navbar'
import Footer from './components/layout/Footer'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ResumeUploadPage from './pages/ResumeUploadPage'
import DiagnosisPage from './pages/DiagnosisPage'
import MatchingPage from './pages/MatchingPage'
import SkillPage from './pages/SkillPage'
import InterviewPage from './pages/InterviewPage'
import ReviewPage from './pages/ReviewPage'
import GrowthPage from './pages/GrowthPage'
import ApplicationPage from './pages/ApplicationPage'
import CoachPage from './pages/CoachPage'

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col relative" style={{ zIndex: 1 }}>
      <Navbar />
      <main className="flex-1 relative" style={{ zIndex: 1 }}>{children}</main>
      <Footer />
    </div>
  )
}

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  useThemeStore((s) => s.theme)
  const basename = import.meta.env.BASE_URL

  return (
    <BrowserRouter basename={basename}>
      <Layout>
        <ErrorBoundary>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
          <Route path="/upload" element={<PrivateRoute><ResumeUploadPage /></PrivateRoute>} />
          <Route path="/diagnosis" element={<PrivateRoute><DiagnosisPage /></PrivateRoute>} />
          <Route path="/matching" element={<PrivateRoute><MatchingPage /></PrivateRoute>} />
          <Route path="/skills" element={<PrivateRoute><SkillPage /></PrivateRoute>} />
          <Route path="/interview" element={<PrivateRoute><InterviewPage /></PrivateRoute>} />
          <Route path="/review/:reviewId?" element={<PrivateRoute><ReviewPage /></PrivateRoute>} />
          <Route path="/growth" element={<PrivateRoute><GrowthPage /></PrivateRoute>} />
          <Route path="/applications" element={<PrivateRoute><ApplicationPage /></PrivateRoute>} />
          <Route path="/coach" element={<PrivateRoute><CoachPage /></PrivateRoute>} />
        </Routes>
        </ErrorBoundary>
      </Layout>
    </BrowserRouter>
  )
}
