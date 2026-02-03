import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth.js'
import './LandingPage.css'

function LandingPage() {
  const navigate = useNavigate()
  const { user, member, signOut } = useAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    function onDocMouseDown(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
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

      {/* 🔝 Account Icon */}
      <div className="account-wrapper" ref={menuRef}>
        <div className="account-icon" onClick={() => setMenuOpen(!menuOpen)}>
          👤
        </div>

        {menuOpen && (
          <div className="account-dropdown">
            <p><strong>{member?.name}</strong></p>
            <p className="email">{member?.email}</p>
            <button onClick={onLogout}>Logout</button>
          </div>
        )}
      </div>

      <div className="landing-content">
        <h1 className="landing-title">Welcome to Word Cloud Game</h1>
        <p className="landing-thoughts">- Turn Thoughts into Winning Words</p>
        <p className="landing-subtitle">Your Battle Begins Here . . !</p>
        <p className="landing-description">
          Test your vocabulary skills and compete with your friends and families in this engaging Word Cloud Game.
        </p>

        {/* 🚀 CTA */}
        <div className="landing-cta-container">
          <button
            className="cta-button cta-primary-highlight"
            onClick={() => navigate('/game')}
          >
            Start Game
          </button>
        </div>

        {/* ⭐ Features */}
        <div className="landing-features">
          <div className="feature-card">
            <div className="feature-icon">📋</div>
            <h3 className="feature-title">Game Rules</h3>
            <ul className="feature-rules">
              <li>Answer questions with programming language names only</li>
              <li>Only valid programming languages are accepted</li>
              <li>Earn +1 point for each correct answer</li>
              <li>Earn +1 point for sharing the game</li>
            </ul>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🏆</div>
            <h3 className="feature-title">Team Competition</h3>
            <p className="feature-description">
              Collaborate with your hackathon team and compete for top rankings.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3 className="feature-title">Real-time Challenges</h3>
            <p className="feature-description">
              Test your speed and accuracy in real-time word cloud challenges.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LandingPage
