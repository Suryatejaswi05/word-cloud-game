import { Navigate, Route, Routes } from 'react-router-dom'
import LoginPage from './pages/LoginPage.jsx'
import LandingPage from './pages/LandingPage.jsx'
import RequireAuth from './auth/RequireAuth.jsx'
import StartGame from './pages/startGame.jsx'
import WordCloudGamePage from './pages/WordCloudGamePage.jsx'
function App() {
  return (
    <>
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
        path="/game"
        element={
          <RequireAuth>
            <StartGame />
          </RequireAuth>
        }
      />
      <Route
        path="/word-cloud/:roundToken?"
        element={
          <RequireAuth>
            <WordCloudGamePage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
    
    </>
   
    
  )
}

export default App
