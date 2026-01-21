import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth.js'

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
    <div className="landing-shell">
      <div className="landing-topbar">
        <div className="landing-team">Team No: {user?.team_no ?? '--'}</div>
        <div style={{ marginLeft: 'auto', color: 'var(--dark-1)', fontWeight: 'bold' }}>Points: {user?.points ?? 0}</div>

        <div className="dropdown" ref={menuRef}>
          <button
            className="landing-userbtn"
            type="button"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((v) => !v)}
          >
            <i className="bi bi-person-circle" />
          </button>

          <ul
            className={`dropdown-menu dropdown-menu-end landing-dropdown${menuOpen ? ' show' : ''}`}
          >
            <li className="px-3 pt-2 pb-1">
              <div className="landing-userline">
                <i className="bi bi-person-circle" />
                <div>
                  <div className="landing-username">{member?.name || '--'}</div>
                  <div className="landing-userdetail">{member?.email || '--'}</div>
                  <div className="landing-userdetail">{member?.phone || '--'}</div>
                  <div className="landing-userdetail">{member?.member_id || '--'}</div>
                </div>
              </div>
            </li>
            <li>
              <hr className="dropdown-divider" />
            </li>
            <li className="px-3 pb-3">
              <button className="btn btn-danger w-100" type="button" onClick={onLogout}>
                Logout
              </button>
            </li>
          </ul>
        </div>
      </div>

      <main className="landing-center" aria-live="polite">
        <section className="center-section">
          <h2 className="title">Word Cloud</h2>
          <p className="description">
            Create a fresh word cloud and invite participants to submit their words for this round.
          </p>
          <button type="button" className="primary-button" onClick={() => navigate('/select-question')}>
            Start New Round
          </button>
        </section>
      </main>
    </div>
  )
}

export default LandingPage
