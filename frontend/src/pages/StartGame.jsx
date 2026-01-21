import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function StartGame() {
  const navigate = useNavigate();

  const [questions, setQuestions] = useState([]);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [shareLink, setShareLink] = useState("");
  const [showShareModal, setShowShareModal] = useState(false);
  const [score, setScore] = useState(0);
  const [answeredQuestions, setAnsweredQuestions] = useState(new Set());
  const [shareCount, setShareCount] = useState(0);
  const [scoreUpdated, setScoreUpdated] = useState(false);

  const apiUrl =
    import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

  /* ---------- WORD COLOR FUNCTION ---------- */
  const getColorFromWord = (word) => {
    let hash = 0;
    for (let i = 0; i < word.length; i++) {
      hash = word.charCodeAt(i) + ((hash << 5) - hash);
    }
    return `hsl(${hash % 360}, 70%, 50%)`;
  };

  useEffect(() => {
    loadQuestions();
  }, []);

  async function loadQuestions() {
    try {
      setLoading(true);
      const res = await fetch(`${apiUrl}/api/questions/`);
      const data = await res.json();
      setQuestions(data.questions || []);
      if (data.questions?.length) loadWordCloud();
    } catch (err) {
      setError("Failed to load questions");
    } finally {
      setLoading(false);
    }
  }

  async function loadWordCloud() {
    try {
      const res = await fetch(`${apiUrl}/api/wordcloud/`);
      const data = await res.json();
      setWords(data.words || []);
    } catch (err) {
      console.error(err);
    }
  }

  async function onSubmit() {
    if (!answer.trim()) return;

    try {
      const res = await fetch(`${apiUrl}/api/submit-answer/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: 1,
          question_id: questions[index]?.id,
          answer: answer.trim(),
        }),
      });

      const data = await res.json();

      setAnswer("");
      setIndex((prev) => (prev + 1) % questions.length);

      const newAnswered = new Set(answeredQuestions);
      newAnswered.add(index);
      setAnsweredQuestions(newAnswered);

      setScore(newAnswered.size + shareCount);
      setScoreUpdated(true);
      setTimeout(() => setScoreUpdated(false), 600);

      loadWordCloud();

      setSuccess(`✓ Submitted "${data.word}"`);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError("Submission failed");
    }
  }

  const createShareableGame = async () => {
    const gameId = `game_${Date.now()}`;
    const link = `${window.location.origin}/join/${gameId}`;
    setShareLink(link);
    await navigator.clipboard.writeText(link);

    const newShareCount = shareCount + 1;
    setShareCount(newShareCount);
    setScore(answeredQuestions.size + newShareCount);

    setShowShareModal(true);
    setTimeout(() => setShowShareModal(false), 5000);
  };

  if (loading) return <p style={{ padding: 40 }}>Loading...</p>;

  return (
    <div style={{ padding: 20, maxWidth: 1000, margin: "0 auto" }}>
      {/* HEADER */}
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h1>Word Game</h1>
        <div
          style={{
            background: "white",
            padding: "10px 20px",
            borderRadius: 8,
            boxShadow: "0 2px 10px rgba(0,0,0,.15)",
          }}
        >
          <div>Your Score</div>
          <div style={{ fontSize: 28, fontWeight: "bold" }}>{score}</div>
          <div style={{ fontSize: 12 }}>
            Answers: {answeredQuestions.size} | Shares: {shareCount}
          </div>
        </div>
      </div>

      {/* QUESTION */}
      <div
        style={{
          background: "#f5f5f5",
          padding: 20,
          borderRadius: 10,
          marginTop: 30,
        }}
      >
        <h2>
          Question {index + 1} of {questions.length}
        </h2>
        <p>{questions[index]?.text}</p>
      </div>

      {/* INPUT + BUTTONS — SINGLE LINE */}
      <div className="mb-3"
        style={{
          display: "flex",
          gap: 10,
          marginTop: 20,
          alignItems: "center",
        }}
      >
        <input
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Enter one word answer"
          style={{
            flex: 2,
            padding: 12,
            fontSize: 16,
            borderRadius: 6,
            border: "1px solid #ddd",
          }}
          onKeyDown={(e) => e.key === "Enter" && onSubmit()}
        />

        <button
          onClick={onSubmit}
          disabled={!answer.trim()}
          style={{
            padding: 12,
            background: answer.trim() ? "#3377ff" : "#ccc",
            color: "white",
            border: "none",
            borderRadius: 6,
            fontSize: 16,
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          Submit Answer
        </button>

        <button
          onClick={createShareableGame}
          style={{
            padding: 12,
            background: "#28a745",
            color: "white",
            border: "none",
            borderRadius: 6,
            fontSize: 16,
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          🔗 Share Game
        </button>
      </div>
      <div
  style={{
    border: "1px solid #ddd",
    padding: "30px",
    minHeight: "220px",
    borderRadius: "8px",
    background: "#fff",
    textAlign: "center",
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center",
    alignItems: "center",
    gap: "12px"
  }}
>
  {words.length > 0 ? (
    words.map((w, idx) => {
      const freq = w.value || w.frequency || 1;

      return (
        <span
          key={idx}
          style={{
            fontSize: `${20 + freq * 14}px`,
            fontWeight: freq > 4 ? "900" : freq > 2 ? "700" : "500",
            color: getColorFromWord(w.text || w.word),
            transform:
              freq > 4
                ? "rotate(0deg)"
                : idx % 3 === 0
                ? "rotate(-10deg)"
                : idx % 3 === 1
                ? "rotate(10deg)"
                : "rotate(0deg)",
            margin: "6px",
            whiteSpace: "nowrap",
            display: "inline-block",
            lineHeight: "1"
          }}
        >
          {w.text || w.word}
        </span>
      );
    })
  ) : (
    <p style={{ color: "#999" }}>No words yet</p>
  )}
</div>


      {/* SHARE MODAL */}
      {showShareModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              background: "white",
              padding: 30,
              borderRadius: 10,
              width: 400,
            }}
          >
            <h3>Game Link</h3>
            <input
              value={shareLink}
              readOnly
              style={{ width: "100%", padding: 10 }}
            />
            <button
              onClick={() => setShowShareModal(false)}
              style={{
                marginTop: 15,
                width: "100%",
                padding: 10,
                background: "#6c757d",
                color: "white",
                border: "none",
                borderRadius: 6,
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default StartGame;
