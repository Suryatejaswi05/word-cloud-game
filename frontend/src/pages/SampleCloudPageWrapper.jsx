import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import WordCloud from './SampleCloudPage';

function SampleCloudPageWrapper() {
  const navigate = useNavigate();
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const apiUrl = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

  useEffect(() => {
    async function fetchWords() {
      try {
        const url = `${apiUrl}/api/sample-wordcloud`;
        console.log("Fetching from:", url);
        
        const response = await fetch(url);
        console.log("Response status:", response.status);
        
        const data = await response.json();
        console.log("Response data:", data);
        
        if (data.words) {
          setWords(data.words);
        } else if (data.error) {
          setError(data.error);
          console.error("API error:", data.error);
        }
      } catch (error) {
        console.error("Error fetching words:", error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }
    
    fetchWords();
  }, [apiUrl]);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)' }}>
        <div style={{ fontSize: '1.5rem', color: '#667eea', fontWeight: 600 }}>Loading Sample Cloud...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)', padding: '20px' }}>
        <div style={{ 
          background: 'white', 
          padding: '40px', 
          borderRadius: '12px', 
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          maxWidth: '500px'
        }}>
          <h2 style={{ color: '#dc2626', marginBottom: '10px' }}>Error Loading Words</h2>
          <p style={{ color: '#666' }}>{error}</p>
          <button 
            onClick={() => navigate(-1)}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)', padding: '40px 20px', position: 'relative' }}>
      <button 
        onClick={() => navigate(-1)} 
        style={{
          position: 'absolute',
          top: '30px',
          left: '30px',
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          color: 'white',
          padding: '12px 24px',
          borderRadius: '50px',
          cursor: 'pointer',
          fontSize: '1rem',
          fontWeight: 600,
          zIndex: 100,
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}
        onMouseEnter={(e) => {
          e.target.style.background = 'rgba(255, 255, 255, 0.2)';
          e.target.style.transform = 'translateX(-8px) scale(1.05)';
        }}
        onMouseLeave={(e) => {
          e.target.style.background = 'rgba(255, 255, 255, 0.1)';
          e.target.style.transform = 'translateX(0) scale(1)';
        }}
      >
        ← Back
      </button>

      <div style={{ maxWidth: '1400px', margin: '0 auto', marginTop: '40px' }}>
        <h1 style={{ textAlign: 'center', color: 'white', marginBottom: '40px', fontSize: '2.5rem', fontWeight: 900 }}>
          🌥️ Sample Word Cloud 
        </h1>
        {words.length > 0 ? (
          <WordCloud words={words} />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#aaa', fontSize: '1.2rem' }}>
            No words available yet
          </div>
        )}
      </div>
    </div>
  );
}

export default SampleCloudPageWrapper;
