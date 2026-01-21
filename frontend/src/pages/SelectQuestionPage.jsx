import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth.js'
import { apiQuestions, apiCreateRound } from '../api/authApi.js'

function SelectQuestionPage() {
  const navigate = useNavigate()
  const { token } = useAuth()
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    async function loadQuestions() {
      try {
        const res = await apiQuestions({ token })
        setQuestions(res.questions)
      } catch (err) {
        setError(err.message || 'Failed to load questions')
      } finally {
        setLoading(false)
      }
    }
    loadQuestions()
  }, [token])

  async function handleSelect(question) {
    setCreating(true)
    setError('')

    try {
      const res = await apiCreateRound({ token, question })
      navigate(`/respond/${res.share_token}`)
    } catch (err) {
      setError(err.message || 'Failed to create round')
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="fixed-screen">
        <div className="center-card" style={{ background: 'var(--white)' }}>
          <p className="body-normal">Loading questions...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed-screen">
      <div className="center-card" style={{ background: 'var(--white)', maxWidth: '800px' }}>
        <h1 className="heading-3" style={{ margin: 0, color: 'var(--dark-1)' }}>Select a Question</h1>
        <p className="body-normal" style={{ margin: '16px 0', color: 'var(--dark-2)' }}>
          Choose a question to start a new word cloud round. You'll earn 1 point for selecting!
        </p>
        {error && <p style={{ color: 'var(--error)', margin: 0 }} className="body-small">{error}</p>}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginTop: '24px' }}>
          {questions.map((question, index) => (
            <button
              key={index}
              className="btn-primary"
              onClick={() => handleSelect(question)}
              disabled={creating}
              style={{
                padding: '16px',
                textAlign: 'left',
                whiteSpace: 'normal',
                height: 'auto',
                minHeight: '80px',
                display: 'flex',
                alignItems: 'center',
              }}
            >
              {question}
            </button>
          ))}
        </div>
        <div style={{ marginTop: '24px' }}>
          <button
            type="button"
            className="btn-secondary btn-small"
            onClick={() => navigate('/landing')}
            disabled={creating}
          >
            Back
          </button>
        </div>
      </div>
    </div>
  )
}

export default SelectQuestionPage