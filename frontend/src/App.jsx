import { Navigate, Route, Routes } from 'react-router-dom'
import LoginPage from './pages/LoginPage.jsx'
import LandingPage from './pages/LandingPage.jsx'
import SelectQuestionPage from './pages/SelectQuestionPage.jsx'
import RespondPage from './pages/RespondPage.jsx'
import RoundDashboardPage from './pages/RoundDashboardPage.jsx'
import RequireAuth from './auth/RequireAuth.jsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/landing"
        element={
          <RequireAuth>
            <LandingPage />
          </RequireAuth>
        }
      />
      <Route
        path="/select-question"
        element={
          <RequireAuth>
            <SelectQuestionPage />
          </RequireAuth>
        }
      />
      <Route path="/respond/:token" element={<RespondPage />} />
      <Route
        path="/round/:id"
        element={
          <RequireAuth>
            <RoundDashboardPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
