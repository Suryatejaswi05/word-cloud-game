import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './WordCloudGame.css';


const WordCloudGamePage = () => {
  const { roundToken } = useParams();
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
  
  // Game States
  const [gamePhase, setGamePhase] = useState('play'); // play or scoreboard
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [userWord, setUserWord] = useState('');
  const [wordCloudData, setWordCloudData] = useState([]);
  const [scoreboard, setScoreboard] = useState([]);
  const [userScore, setUserScore] = useState(0);
  const [shareCount, setShareCount] = useState(0);
  const [answeredQuestions, setAnsweredQuestions] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [allAnswers, setAllAnswers] = useState([]);
  const [scoreUpdated, setScoreUpdated] = useState(false);
  
  // Helper function for API calls
  const apiRequest = async (url, method = 'GET', body = null, token = null) => {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
      method,
      headers,
    };
    
    if (body) {
      options.body = JSON.stringify(body);
    }
    
    const response = await fetch(`${apiUrl}${url}`, options);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  };
  
  // Initialize - Load questions
  useEffect(() => {
    loadQuestions();
  }, []);

  // Update scoreboard with user's answer
  useEffect(() => {
    if (answeredQuestions.size > 0 || shareCount > 0) {
      const newScore = answeredQuestions.size + shareCount;
      setUserScore(newScore);
      // Add animation effect
      setScoreUpdated(true);
      setTimeout(() => setScoreUpdated(false), 600);
    }
  }, [answeredQuestions, shareCount]);
  
  const loadQuestions = async () => {
    try {
      setLoading(true);
      const data = await apiRequest('/api/questions');
      setQuestions(data.questions || []);
      setError(null);
    } catch (err) {
      setError('Failed to load questions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!userAnswer.trim()) {
      setError('Please enter an answer');
      return;
    }

    // Validate programming language
    const programmingLanguages = [
      'python', 'javascript', 'java', 'c', 'c++', 'cpp', 'c#', 'csharp',
      'ruby', 'go', 'rust', 'swift', 'kotlin', 'php', 'typescript',
      'scala', 'perl', 'r', 'matlab', 'dart', 'lua', 'haskell',
      'objective-c', 'objectivec', 'shell', 'bash', 'powershell', 'sql',
      'html', 'css', 'xml', 'json', 'yaml', 'markdown', 'assembly',
      'fortran', 'cobol', 'lisp', 'scheme', 'elixir', 'erlang',
      'clojure', 'f#', 'fsharp', 'groovy', 'julia', 'racket', 'solidity',
      'vb', 'vba', 'pascal', 'ada', 'prolog', 'smalltalk', 'tcl',
      'ocaml', 'nim', 'crystal', 'zig', 'v', 'd'
    ];

    const normalizedAnswer = userAnswer.toLowerCase().trim().replace(/[\s\-_]/g, '');
    
    const isValidLanguage = programmingLanguages.some(lang => {
      const normalizedLang = lang.replace(/[\s\-_]/g, '');
      return normalizedAnswer === normalizedLang;
    });

    if (!isValidLanguage) {
      setError('⚠️ Only programming languages are allowed! Please enter a valid programming language.');
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      await apiRequest(
        '/api/submit-answer',
        'POST',
        { answer: userAnswer },
        token
      );

      // Add to answered and update word cloud
      const newAnswered = new Set(answeredQuestions);
      newAnswered.add(currentQuestionIndex);
      setAnsweredQuestions(newAnswered);
      setAllAnswers([...allAnswers, userAnswer]);
      setUserAnswer('');
      setSuccess('✓ Answer submitted! +1 point');
      setError(null);

      // Move to next question after a short delay
      setTimeout(() => {
        if (currentQuestionIndex < questions.length - 1) {
          setCurrentQuestionIndex(currentQuestionIndex + 1);
        } else {
          setGamePhase('scoreboard');
        }
      }, 800);
    } catch (err) {
      const errorMsg = err.message || 'Failed to submit answer';
      // Check if backend returned validation error
      if (errorMsg.includes('programming language')) {
        setError('⚠️ Only programming languages are allowed! Please enter a valid programming language.');
      } else {
        setError('Failed to submit answer');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const shareGame = () => {
    const shareUrl = `${window.location.origin}/#/word-cloud`;
    if (navigator.share) {
      navigator.share({
        title: 'Word Cloud Game',
        text: 'Join my word cloud game and test your vocabulary!',
        url: shareUrl
      });
    } else {
      navigator.clipboard.writeText(shareUrl);
      setSuccess('Game link copied to clipboard!');
    }
    const newShareCount = shareCount + 1;
    setShareCount(newShareCount);
    setUserScore(answeredQuestions.size + newShareCount);
  };

  const currentQuestion = questions[currentQuestionIndex];
  const isQuestionAnswered = answeredQuestions.has(currentQuestionIndex);

  return (
    <div className="word-cloud-game-container">
      <button onClick={() => navigate('/')} className="back-home-btn">
        ← Back to Home
      </button>

      <h1 className="game-title">☁️ Word Cloud Game</h1>

      {/* Score Display */}
      <div className="score-display">
        <div className={`score-box ${scoreUpdated ? 'score-updated' : ''}`}>
          <h3>Your Score</h3>
          <p className="score-value">{userScore}</p>
          <small>{answeredQuestions.size} answers + {shareCount} shares</small>
        </div>
      </div>

      {/* Alerts */}
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Game Phase - Play */}
      {gamePhase === 'play' && (
        <div className="play-phase">
          <div className="question-area">
            {loading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
                <p>Loading questions...</p>
              </div>
            ) : (
              <>
                <div className="question-header">
                  <h2>Question {currentQuestionIndex + 1} of {questions.length}</h2>
                </div>

                <div className="question-box">
                  <p className="question-text">
                    {currentQuestion?.text || 'No question available'}
                  </p>
                </div>

                <div className="form-group">
                  <label htmlFor="answer-input">Your Answer:</label>
                  <input
                    id="answer-input"
                    type="text"
                    className="form-control"
                    value={userAnswer}
                    onChange={(e) => {
                      setUserAnswer(e.target.value);
                      setError(null);
                    }}
                    onKeyDown={(e) => e.key === 'Enter' && submitAnswer()}
                    placeholder="Type your answer here..."
                    disabled={loading || isQuestionAnswered}
                  />
                </div>

                <div className="button-group">
                  <button
                    className="btn btn-primary"
                    onClick={submitAnswer}
                    disabled={loading || !userAnswer.trim() || isQuestionAnswered}
                  >
                    {loading ? 'Submitting...' : isQuestionAnswered ? 'Answered ✓' : 'Submit Answer'}
                  </button>

                  {currentQuestionIndex < questions.length - 1 ? (
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setCurrentQuestionIndex(currentQuestionIndex + 1);
                        setUserAnswer('');
                        setError(null);
                        setSuccess(null);
                      }}
                      disabled={loading}
                    >
                      Next Question →
                    </button>
                  ) : (
                    <button
                      className="btn btn-success"
                      onClick={() => setGamePhase('scoreboard')}
                    >
                      View Scoreboard 🏆
                    </button>
                  )}
                </div>

                <div className="game-actions">
                  <button className="btn btn-info" onClick={shareGame}>
                    🔗 Share Game (+1 point)
                  </button>
                </div>

                {/* Word Cloud Preview */}
                {allAnswers.length > 0 && (
                  <div className="word-cloud-preview">
                    <h3>Your Answers So Far:</h3>
                    <div className="words-display">
                      {allAnswers.map((word, idx) => (
                        <span 
                          key={idx} 
                          className="preview-word"
                          style={{
                            fontSize: `${14 + (idx % 3) * 8}px`,
                            color: `hsl(${(idx * 60) % 360}, 70%, 50%)`
                          }}
                        >
                          {word}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Game Phase - Scoreboard */}
      {gamePhase === 'scoreboard' && (
        <div className="scoreboard-phase">
          <div className="game-phase">
            <h2>🎉 Game Complete!</h2>
            
            <div className="final-score-card">
              <h3>Your Final Score</h3>
              <p className="final-score">{userScore}</p>
              <p className="score-breakdown">
                {answeredQuestions.size} questions answered + {shareCount} shares
              </p>
            </div>

            {/* Final Word Cloud */}
            <div className="final-word-cloud">
              <h3>Your Word Cloud:</h3>
              <div className="words-display">
                {allAnswers.map((word, idx) => (
                  <span 
                    key={idx} 
                    className="final-word"
                    style={{
                      fontSize: `${20 + (allAnswers.length - idx) * 4}px`,
                      color: `hsl(${(idx * 45) % 360}, 75%, 55%)`,
                      transform: `rotate(${(idx % 2 === 0 ? 1 : -1) * (idx % 15)}deg)`
                    }}
                  >
                    {word}
                  </span>
                ))}
              </div>
            </div>

            <div className="button-group">
              <button
                className="btn btn-primary"
                onClick={() => {
                  setGamePhase('play');
                  setCurrentQuestionIndex(0);
                  setAnsweredQuestions(new Set());
                  setAllAnswers([]);
                  setUserAnswer('');
                }}
              >
                🔄 Play Again
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => navigate('/')}
              >
                🏠 Back to Home
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WordCloudGamePage;