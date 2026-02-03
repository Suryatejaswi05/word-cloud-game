import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./StartGame.css";

function StartGame() {
  const navigate = useNavigate();
  const userId = 1;

  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState("");
  const [inputError, setInputError] = useState("");
  const [showShare, setShowShare] = useState(false);
  const [score, setScore] = useState(0);

  const apiUrl =
    import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    // Reset score on fresh login/mount
    setScore(0);
    loadQuestion();
    loadScore();
    const interval = setInterval(loadScore, 2000);
    return () => clearInterval(interval);
  }, []);

  async function loadQuestion() {
    const res = await fetch(`${apiUrl}/api/questions`);
    const data = await res.json();
    if (data.questions?.length) setQuestion(data.questions[0]);
    setLoading(false);
  }

  async function loadScore() {
    const res = await fetch(`${apiUrl}/api/user-score?user_id=${userId}`);
    const data = await res.json();
    setScore(data.total_score || 0);
  }

  async function onSubmit() {
    if (!answer.trim()) return;

    /* Removed character validation to allow any word/characters */
    /*
    if (!isValidAnswer(answer)) {
      setInputError(
        "❌ No special characters allowed. Only letters (A–Z, a–z) are allowed."
      );
      return;
    }
    */

    setInputError("");

    try {
      const res = await fetch(`${apiUrl}/api/submit-answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, answer }),
      });

      const data = await res.json();

      if (!res.ok) {
        setInputError(data.error || "Submission failed");
        return;
      }

      setSuccess("🎉 ANSWER SUBMITTED!");
      setAnswer("");
      loadScore();
      setTimeout(() => setSuccess(""), 2500);
    } catch (err) {
      setInputError("Failed to connect to server.");
    }
  }

  async function trackShare(platform) {
    try {
      await fetch(`${apiUrl}/api/record-share`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, platform }),
      });
      loadScore();
    } catch (e) {
      console.error("Share tracking failed", e);
    }
  }

  if (loading) return <div className="loading-screen"><div className="spinner"></div><p>Loading Game...</p></div>;

  return (
    <div className="start-game-container">
      <button onClick={() => navigate("/")} className="back-button">
        ← Back to Home
      </button>

      <div className="game-card">
        {/* HEADER */}
        <div className="game-header">
          <h1 className="game-title">🎮 Word Cloud Game</h1>
          <div className={`score-badge ${success ? 'score-pulse' : ''}`}>
            <span className="score-icon">⭐</span>
            <span className="score-label">Score</span>
            <span className="score-value">{score}</span>
          </div>
        </div>

        {/* QUESTION */}
        <div className="question-section">
          <h2 className="question-text">{question?.text}</h2>
        </div>

        {/* INPUT */}
        <div className="input-section">
          <input
            value={answer}
            onChange={(e) => {
              setAnswer(e.target.value);
              setInputError("");
            }}
            placeholder="Type your answer here..."
            onKeyDown={(e) => e.key === "Enter" && onSubmit()}
            className={`answer-input ${inputError ? 'input-error' : ''}`}
          />

          {inputError && (
            <p className="error-message">{inputError}</p>
          )}

          {/* SUBMIT */}
          <button onClick={onSubmit} className="submit-button">
            Submit Answer
          </button>

          {success && (
            <div className="success-message">
              {success}
            </div>
          )}
        </div>

        {/* ACTIONS */}
        <div className="action-buttons">
            <button onClick={() => setShowShare(true)} className="action-btn share-btn">
              <span className="btn-icon">🔗</span>
              Share Game
            </button>

            <button onClick={() => navigate("/word-cloud")} className="action-btn cloud-btn">
              <span className="btn-icon">☁️</span>
              View Word Cloud
            </button>

            <button onClick={() => navigate("/sample-cloud")} className="action-btn cloud-btn">
              <span className="btn-icon">🌥️</span>
              View Sample Cloud
            </button>
        </div>
      </div>

      {/* ---------------- SHARE MODAL ---------------- */}
      {showShare && (
        <div className="modal-overlay" onClick={() => setShowShare(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowShare(false)}>×</button>
            <h3 className="modal-title">Share this game!</h3>
            <p className="modal-description">
              Invite your friends to join the Word Cloud Game and compete together.
            </p>

            <div className="share-url-box">
              {window.location.href}
            </div>

            <div className="share-buttons">
              <button
                onClick={() => {
                  trackShare("whatsapp");
                  const url = window.location.href;
                  const text = `Join the Word Cloud Game! ${url}`;
                  window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank");
                }}
                className="share-btn-whatsapp"
              >
                <span>📱</span> WhatsApp
              </button>
              <button
                onClick={() => {
                  trackShare("clipboard");
                  navigator.clipboard.writeText(window.location.href);
                  setSuccess("✓ Link copied to clipboard!");
                  setShowShare(false);
                  setTimeout(() => setSuccess(""), 3000);
                }}
                className="share-btn-copy"
              >
                <span>📋</span> Copy Link
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default StartGame;