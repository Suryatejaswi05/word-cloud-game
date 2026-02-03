import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

function WordCloudPage() {
  const navigate = useNavigate();
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // 🔥 Store previous frequencies safely
  const prevFreqRef = useRef({});

  const apiUrl =
    import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

  /* ---------- COLOR ---------- */
  const getColorFromWord = (word) => {
    let hash = 0;
    for (let i = 0; i < word.length; i++) {
      hash = word.charCodeAt(i) + ((hash << 5) - hash);
    }
    return `hsl(${hash % 360}, 70%, 45%)`;
  };

  /* ---------- LOAD WORD CLOUD ---------- */
  useEffect(() => {
    loadWordCloud();

    // 🔁 live refresh for animation
    const interval = setInterval(loadWordCloud, 3000);
    return () => clearInterval(interval);
  }, []);

  async function loadWordCloud() {
    try {
      const res = await fetch(`${apiUrl}/api/wordcloud`);
      const data = await res.json();

      const sorted = (data.words || []).sort(
        (a, b) =>
          (b.value || b.frequency || 1) -
          (a.value || a.frequency || 1)
      );

      setWords(sorted);
    } catch {
      setError("Failed to load word cloud");
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <p style={{ padding: 40 }}>Loading Word Cloud…</p>;

  /* ---------- STRONG SIZE SCALING ---------- */
  const getFontSize = (freq) => {
    const BASE = 18;
    const SCALE = 18; // 👈 increase for more impact
    const MAX = 96;

    return Math.min(
      MAX,
      BASE + Math.log2(freq + 1) * SCALE
    );
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "20px",
        position: "relative",
        overflowX: "hidden",
        overflowY: "auto",
      }}
    >
      {/* Animated particles background */}
      <div style={{
        position: "absolute",
        width: "100%",
        height: "100%",
        backgroundImage: `
          radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
          radial-gradient(circle at 40% 20%, rgba(34, 197, 94, 0.1) 0%, transparent 50%)
        `,
        animation: "particleMove 20s ease-in-out infinite",
        pointerEvents: "none",
        zIndex: 0,
      }} />
      <style>{`
        @keyframes particleMove {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -30px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        @media (max-width: 768px) {
          .word-cloud-title {
            font-size: 2rem !important;
          }
          .word-cloud-subtitle {
            font-size: 0.95rem !important;
          }
          .word-cloud-card {
            padding: 20px !important;
            border-radius: 16px !important;
          }
          .word-cloud-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 30px 20px !important;
            min-height: 300px !important;
          }
          .word-cloud-button {
            margin-top: 20px !important;
            padding: 12px 30px !important;
            font-size: 14px !important;
          }
        }
        @media (max-width: 480px) {
          .word-cloud-title {
            font-size: 1.5rem !important;
          }
          .word-cloud-subtitle {
            font-size: 0.85rem !important;
            margin-bottom: 20px !important;
          }
          .word-cloud-card {
            padding: 15px !important;
          }
          .word-cloud-grid {
            grid-template-columns: 1fr !important;
            gap: 20px !important;
            min-height: 250px !important;
          }
        }
      `}</style>
      
      <div style={{ width: "100%", maxWidth: 1100, textAlign: "center", position: "relative", zIndex: 1 }}>
        {/* TITLE */}
        <h1
          className="word-cloud-title"
          style={{
            color: "white",
            fontSize: "3.6rem",
            fontWeight: 900,
            marginBottom: 12,
            textShadow: "0 4px 12px rgba(0, 0, 0, 0.3)",
          }}
        >
          Word Cloud
        </h1>

        <p
          className="word-cloud-subtitle"
          style={{
            color: "rgba(255, 255, 255, 0.85)",
            fontSize: "1.15rem",
            marginBottom: 36,
          }}
        >
          Collective thoughts from all players
        </p>

        {/* CARD */}
        <div
          className="word-cloud-card"
          style={{
            background: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)",
            borderRadius: 24,
            padding: 50,
            boxShadow: "0 30px 80px rgba(0, 0, 0, 0.4)",
            border: "1px solid rgba(255, 255, 255, 0.3)",
            position: "relative",
          }}
        >
          {/* Shimmer border effect */}
          <div style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: "5px",
            background: "linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%)",
            backgroundSize: "200% 100%",
            borderRadius: "24px 24px 0 0",
            animation: "shimmer 3s linear infinite",
          }} />
          <style>{`
            @keyframes shimmer {
              0% { background-position: 0% 0%; }
              100% { background-position: 200% 0%; }
            }
          `}</style>
          {/* GRID – NO OVERLAP */}
          <div
            className="word-cloud-grid"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, 1fr)",
              gap: "60px 40px",
              justifyItems: "center",
              alignItems: "center",
              minHeight: 450,
            }}
          >
            {words.map((w) => {
              const text = (w.text || w.word || "").toUpperCase();
              const freq = w.value || w.frequency || 1;
              const isVertical = text.length <= 5;

              const fontSize = getFontSize(freq);

              // 🔥 detect growth
              const prevFreq = prevFreqRef.current[text] || 0;
              const hasGrown = freq > prevFreq;

              // store new freq
              prevFreqRef.current[text] = freq;

              return (
                <div
                  key={`${text}-${freq}`} // ✅ CRITICAL FIX
                  title={`"${text}" used ${freq} times`}
                  style={{
                    display: "flex",
                    flexDirection: isVertical ? "column" : "row",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize,
                    fontWeight: 800,
                    color: getColorFromWord(text),
                    lineHeight: isVertical ? "1.1" : "1",
                    letterSpacing: isVertical ? "0" : "2px",
                    userSelect: "none",
                    cursor: "pointer",

                    /* 🔥 ANIMATION */
                    transform: hasGrown ? "scale(1.25)" : "scale(1)",
                    transition:
                      "transform 0.35s ease, font-size 0.6s ease",

                    textShadow:
                      freq > 3
                        ? "0 10px 25px rgba(0,0,0,0.35)"
                        : "none",
                  }}
                  onTransitionEnd={(e) => {
                    e.currentTarget.style.transform = "scale(1)";
                  }}
                >
                  {isVertical
                    ? text.split("").map((ch, i) => (
                        <span key={i}>{ch}</span>
                      ))
                    : text}
                </div>
              );
            })}
          </div>
        </div>

        {/* BACK */}
        <button
          className="word-cloud-button"
          onClick={() => navigate("/game")}
          style={{
            marginTop: 40,
            padding: "14px 46px",
            background: "rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(20px)",
            WebkitBackdropFilter: "blur(20px)",
            color: "white",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            borderRadius: 999,
            fontSize: 16,
            fontWeight: 700,
            cursor: "pointer",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
            transition: "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(255, 255, 255, 0.2)";
            e.currentTarget.style.transform = "scale(1.05)";
            e.currentTarget.style.boxShadow = "0 12px 40px rgba(0, 0, 0, 0.3)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
            e.currentTarget.style.transform = "scale(1)";
            e.currentTarget.style.boxShadow = "0 8px 32px rgba(0, 0, 0, 0.2)";
          }}
        >
          ← Back to Game
        </button>

        {error && (
          <p style={{ marginTop: 20, color: "#dc2626" }}>
            {error}
          </p>
        )}
      </div>
    </div>
  );
}

export default WordCloudPage;
