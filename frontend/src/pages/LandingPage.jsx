import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import './LandingPage.css'

function LandingPage() {
  const navigate = useNavigate()
  const { user, member, signOut } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    function onDocMouseDown(e) {
      if (!menuRef.current) return
      if (!menuRef.current.contains(e.target)) {
        setMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', onDocMouseDown)
    return () => document.removeEventListener('mousedown', onDocMouseDown)
  }, [])

  async function onLogout() {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="landing-container">
      <div className="landing-content">
        <h1 className="landing-title">Welcome to Word Cloud Game</h1>
        <p className='landing-thoughts'>-Turn Thoughts into Winning Words</p>
        <p className="landing-subtitle">Your Battle Begins Here . . !</p>
        <p className="landing-description">Test your vocabulary skills and compete with your friends and families in this engaging Word Cloud Game.</p>
        
        <div className="landing-cta-container">
          <button className="cta-button cta-primary" onClick={() => navigate('/game')}>
            Start Game
          </button>
          <button className="cta-button cta-secondary" onClick={() => navigate('/rules')}>
            Learn Rules
          </button>
        </div>

        <div className="landing-features">
          <div className="feature-card">
            <div className="feature-icon">🎮</div>
            <h3 className="feature-title">Engaging Gameplay</h3>
            <p className="feature-description">Challenge yourself with dynamic word puzzles designed to test your vocabulary and puzzle-solving abilities.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🏆</div>
            <h3 className="feature-title">Team Competition</h3>
            <p className="feature-description">Collaborate with your hackathon team and compete for the highest scores and top rankings.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3 className="feature-title">Real-time Challenges</h3>
            <p className="feature-description">Test your speed and accuracy in real-time word cloud challenges with dynamic difficulty levels.</p>
          </div>
        </div>

        <div className="landing-user-info">
          <p><strong>Team No:</strong> {user?.team_no ?? '--'}</p>
          <p><strong>Player:</strong> {member?.name || '--'}</p>
          <p><strong>Email:</strong> {member?.email || '--'}</p>
          <button 
            className="cta-button cta-secondary landing-logout-btn" 
            onClick={onLogout}
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

export default LandingPage
