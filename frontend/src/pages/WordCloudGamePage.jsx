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
      const data = await apiRequest('/api/questions/');
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

    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      await apiRequest(
        '/api/submit-answer/',
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
      setError('Failed to submit answer');
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
};

export default WordCloudGamePage;