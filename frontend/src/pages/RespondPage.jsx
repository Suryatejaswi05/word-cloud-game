import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiSubmitResponse } from '../api/authApi.js'

function RespondPage() {
  const { token: shareToken } = useParams()
  const navigate = useNavigate()
  const [question, setQuestion] = useState('')
  const [word, setWord] = useState('')
  const [playerId, setPlayerId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    // Generate a unique player ID if not set
    if (!playerId) {
      setPlayerId(`player_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
    }

    // Fetch question (assuming GET /respond/:token returns question)
    fetch(`/respond/${shareToken}`)
      .then(res => res.json())
      .then(data => {
        if (data.question) {
          setQuestion(data.question)
        } else {
          setError('Invalid or expired link')
        }
      })
      .catch(() => setError('Failed to load question'))
  }, [shareToken, playerId])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!word.trim()) return

    const cleanWord = word.trim().toLowerCase()
    if (!/^[a-z]+$/.test(cleanWord)) {
      setError('Please enter a single word with letters only')
      return
    }

    setLoading(true)
    setError('')

    try {
      await apiSubmitResponse({ shareToken, word: cleanWord, playerId })
      setSubmitted(true)
    } catch (err) {
      setError(err.message || 'Failed to submit response')
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="fixed-screen">
        <div className="center-card" style={{ background: 'var(--white)' }}>
          <h1 className="heading-3" style={{ color: 'var(--success)' }}>Response Submitted!</h1>
          <p className="body-normal" style={{ color: 'var(--dark-2)' }}>
            Thank you for your response. The word cloud will update shortly.
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn-primary" onClick={() => window.location.reload()}>
              Share Again
            </button>
            <button className="btn-ghost" onClick={() => navigate('/')}>
              Exit
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed-screen">
      <div className="center-card" style={{ background: 'var(--white)', maxWidth: '600px' }}>
        <h1 className="heading-4" style={{ margin: 0, color: 'var(--dark-1)' }}>Respond to Question</h1>
        {question && (
          <p className="lead-paragraph" style={{ color: 'var(--dark-1)', textAlign: 'center' }}>
            {question}
          </p>
        )}
        <form onSubmit={handleSubmit} style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label className="body-normal" style={{ display: 'block', marginBottom: '8px', color: 'var(--dark-1)' }}>
              Your Response (single word)
            </label>
            <input
              type="text"
              className="input-field"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              placeholder="Enter one word..."
              required
            />
          </div>
          {error && <p style={{ color: 'var(--error)', margin: 0 }} className="body-small">{error}</p>}
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button type="submit" className="btn-primary" disabled={loading || !question}>
              {loading ? 'Submitting...' : 'Submit Response'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RespondPage