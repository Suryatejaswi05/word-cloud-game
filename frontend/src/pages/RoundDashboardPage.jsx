import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../auth/useAuth.js'
import { apiGetRoundDetails, apiGetWordCloud, apiGetLeaderboard, apiRecordShare, apiEndRound } from '../api/authApi.js'

function RoundDashboardPage() {
  const { id: roundId } = useParams()
  const { token, user } = useAuth()
  const [round, setRound] = useState(null)
  const [frequencies, setFrequencies] = useState([])
  const [leaderboard, setLeaderboard] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadData = useCallback(async () => {
    try {
      const [roundRes, cloudRes, leaderRes] = await Promise.all([
        apiGetRoundDetails({ roundId }),
        apiGetWordCloud({ roundId }),
        apiGetLeaderboard({ roundId })
      ])
      setRound(roundRes)
      setFrequencies(cloudRes.frequencies)
      setLeaderboard(leaderRes.leaderboard)
    } catch (error) {
      setError(error.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }, [roundId])

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [loadData])

  function handleShare() {
    const playerId = `sharer_${Date.now()}`
    const shareUrl = `${window.location.origin}/respond/${round.share_token}`
    navigator.clipboard.writeText(shareUrl)
    apiRecordShare({ roundId, playerId })
    alert('Link copied to clipboard!')
  }

  async function handleEndRound() {
    if (confirm('Are you sure you want to end this round?')) {
      try {
        await apiEndRound({ token, roundId })
        loadData()
      } catch {
        alert('Failed to end round')
      }
    }
  }

  if (loading) return <div className="fixed-screen"><p>Loading...</p></div>
  if (error) return <div className="fixed-screen"><p>Error: {error}</p></div>
  if (!round) return <div className="fixed-screen"><p>Round not found</p></div>

  const maxCount = Math.max(...frequencies.map(f => f.count), 1)
  const minSize = 14
  const maxSize = 48

  return (
    <div style={{ minHeight: '100vh', background: 'var(--light-4)', padding: '24px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h1 className="heading-3" style={{ color: 'var(--dark-1)' }}>Round Dashboard</h1>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn-secondary" onClick={handleShare}>
              Share Link
            </button>
            {round.created_by === user?.id && round.status === 'active' && (
              <button className="btn-primary" onClick={handleEndRound}>
                End Round
              </button>
            )}
          </div>
        </div>

        <div style={{ background: 'var(--white)', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
          <h2 className="heading-5" style={{ color: 'var(--dark-1)' }}>Question</h2>
          <p className="lead-paragraph" style={{ color: 'var(--dark-2)' }}>{round.question}</p>
          <p className="body-small" style={{ color: 'var(--dark-3)' }}>
            Status: {round.status} | Responses: {round.response_count}
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
          <div style={{ background: 'var(--white)', borderRadius: '12px', padding: '24px' }}>
            <h2 className="heading-5" style={{ color: 'var(--dark-1)', marginBottom: '16px' }}>Word Cloud</h2>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
              gap: '12px',
              alignItems: 'center',
              justifyItems: 'center'
            }}>
              {frequencies.map((freq, index) => {
                const size = minSize + ((freq.count / maxCount) * (maxSize - minSize))
                const colors = ['#3377FF', '#2659BF', '#99BBFF', '#E3EDFF', '#06C270', '#FFCC00']
                const color = colors[index % colors.length]
                return (
                  <div
                    key={freq.word}
                    style={{
                      fontSize: `${size}px`,
                      color,
                      fontWeight: freq.count > maxCount * 0.5 ? 700 : 400,
                      textAlign: 'center',
                      padding: '8px',
                      borderRadius: '8px',
                      background: 'var(--light-4)',
                      minHeight: '60px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      wordBreak: 'break-word'
                    }}
                  >
                    {freq.word}
                  </div>
                )
              })}
            </div>
          </div>

          <div style={{ background: 'var(--white)', borderRadius: '12px', padding: '24px' }}>
            <h2 className="heading-5" style={{ color: 'var(--dark-1)', marginBottom: '16px' }}>Leaderboard</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {leaderboard.slice(0, 10).map((entry, index) => (
                <div key={entry.player_id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '8px 12px',
                  background: index === 0 ? 'var(--primary-subtle)' : 'var(--light-4)',
                  borderRadius: '6px'
                }}>
                  <span className="body-normal" style={{ color: 'var(--dark-1)' }}>
                    {index + 1}. {entry.player_id.slice(0, 10)}...
                  </span>
                  <span className="body-normal" style={{ color: 'var(--primary)', fontWeight: 600 }}>
                    {entry.score}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RoundDashboardPage