import React from 'react';

export default function WordCloud({ words = [] }) {
  const [isMobile, setIsMobile] = React.useState(window.innerWidth < 768);
  
  React.useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!words || words.length === 0) {
    return (
      <div style={cloudStyle}>
        <p style={{ color: "#aaa", textAlign: "center", fontSize: isMobile ? "14px" : "16px", padding: "20px" }}>
          No words yet. Submit your first answer!
        </p>
      </div>
    )
  }

  // === WORLD MAP STRUCTURE WITH COLLISION DETECTION ===
  
  // 1. Configuration - Responsive dimensions
  const CONTAINER_WIDTH = isMobile ? Math.min(window.innerWidth - 40, 500) : 1400;
  const CONTAINER_HEIGHT = isMobile ? Math.min(window.innerHeight * 0.5, 400) : 700;
  const MIN_PADDING = isMobile ? 2 : 4;
  
  // 2. Grid Configuration
  const COLS = isMobile ? 40 : 80; 
  const ROWS = isMobile ? 30 : 40;
  
  // 3. Define Land Masses (World Map Coordinates)
  const isLand = (c, r) => {
    // Americas (Left Side)
    if (c >= 4 && c <= 16 && r >= 3 && r <= 8) return true; // Alaska/North Canada
    if (c >= 8 && c <= 25 && r >= 8 && r <= 17) return true; // Canada/USA
    if (c >= 13 && c <= 20 && r >= 17 && r <= 21) return true; // Central America
    if (c >= 24 && c <= 33 && r >= 22 && r <= 29) return true; // Upper South America
    if (c >= 26 && c <= 31 && r >= 29 && r <= 36) return true; // Lower South America

    // Europe / Africa (Center)
    if (c >= 41 && c <= 51 && r >= 5 && r <= 13) return true; // Europe
    if (c >= 39 && c <= 40 && r >= 8 && r <= 11) return true; // UK
    if (c >= 43 && c <= 46 && r >= 2 && r <= 7) return true; // Scandinavia
    if (c >= 38 && c <= 53 && r >= 14 && r <= 24) return true; // North Africa
    if (c >= 42 && c <= 52 && r >= 24 && r <= 33) return true; // South Africa
    if (c >= 54 && c <= 56 && r >= 29 && r <= 32) return true; // Madagascar

    // Asia (Right Side)
    if (c >= 53 && c <= 77 && r >= 4 && r <= 12) return true; // Russia/North Asia
    if (c >= 48 && c <= 55 && r >= 14 && r <= 17) return true; // Middle East
    if (c >= 56 && c <= 61 && r >= 18 && r <= 24) return true; // India
    if (c >= 60 && c <= 73 && r >= 13 && r <= 21) return true; // China/East Asia
    if (c >= 64 && c <= 74 && r >= 23 && r <= 28) return true; // SE Asia Islands
    if (c >= 76 && c <= 79 && r >= 13 && r <= 17) return true; // Japan

    // Oceania
    if (c >= 66 && c <= 76 && r >= 30 && r <= 36) return true; // Australia
    if (c >= 77 && c <= 79 && r >= 36 && r <= 39) return true; // New Zealand

    return false;
  };

  // 4. Generate Land Positions
  const landPositions = [];
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if (isLand(c, r)) {
        landPositions.push({ 
          x: (c / COLS) * CONTAINER_WIDTH, 
          y: (r / ROWS) * CONTAINER_HEIGHT
        });
      }
    }
  }

  // 5. Font Size Mapping - Responsive and Dynamic
  const getMaxFrequency = () => {
    return sortedWords.length > 0 ? (sortedWords[0].value || sortedWords[0].frequency || 1) : 1;
  };

  const getFontSize = (freq) => {
    const maxFreq = getMaxFrequency();
    const val = freq || 1;
    const scale = isMobile ? 0.5 : 1;
    
    // Dynamic scaling based on actual max frequency
    const percentage = (val / maxFreq) * 100;
    
    if (percentage >= 100) return 56 * scale;
    if (percentage >= 80) return 44 * scale;
    if (percentage >= 60) return 34 * scale;
    if (percentage >= 40) return 26 * scale;
    if (percentage >= 20) return 18 * scale;
    if (percentage >= 10) return 14 * scale;
    return 11 * scale;
  };

  // 6. Collision Detection
  const calculateBounds = (x, y, text, fontSize, rotation = 0) => {
    const charWidth = fontSize * 0.6;
    const textWidth = text.length * charWidth;
    const textHeight = fontSize;

    if (rotation === -90 || rotation === 90) {
      return {
        left: x - textHeight / 2 - MIN_PADDING,
        right: x + textHeight / 2 + MIN_PADDING,
        top: y - textWidth / 2 - MIN_PADDING,
        bottom: y + textWidth / 2 + MIN_PADDING
      };
    } else {
      return {
        left: x - textWidth / 2 - MIN_PADDING,
        right: x + textWidth / 2 + MIN_PADDING,
        top: y - textHeight / 2 - MIN_PADDING,
        bottom: y + textHeight / 2 + MIN_PADDING
      };
    }
  };

  const hasCollision = (bounds1, bounds2) => {
    return !(
      bounds1.right < bounds2.left ||
      bounds1.left > bounds2.right ||
      bounds1.bottom < bounds2.top ||
      bounds1.top > bounds2.bottom
    );
  };

  // 7. Sort and Place Words - Limit words on mobile
  const sortedWords = [...words]
    .sort((a, b) => (b.value || b.frequency || 0) - (a.value || a.frequency || 0))
    .slice(0, isMobile ? 100 : 600);

  const shuffledPositions = [...landPositions].sort(() => Math.random() - 0.5);
  const placedWords = [];

  for (let i = 0; i < sortedWords.length; i++) {
    const word = sortedWords[i];
    const text = word.text || word.word || '';
    const fontSize = getFontSize(word.value || word.frequency || 1);
    const rotation = text.length <= 7 && Math.random() > 0.75 ? 90 : 0;
    
    let placed = false;

    // Try positions until we find one without collision
    for (let j = i; j < shuffledPositions.length && !placed; j++) {
      const pos = shuffledPositions[j];
      const bounds = calculateBounds(pos.x, pos.y, text, fontSize, rotation);

      // Check container bounds
      if (bounds.left < 0 || bounds.right > CONTAINER_WIDTH ||
          bounds.top < 0 || bounds.bottom > CONTAINER_HEIGHT) {
        continue;
      }

      // Check collision with placed words
      let collisionDetected = false;
      for (const placedWord of placedWords) {
        if (hasCollision(bounds, placedWord.bounds)) {
          collisionDetected = true;
          break;
        }
      }

      if (!collisionDetected) {
        placedWords.push({
          text,
          x: pos.x,
          y: pos.y,
          fontSize,
          rotation,
          bounds,
          frequency: word.value || word.frequency || 1
        });
        placed = true;
      }
    }
  }

  // 8. Modern Color Palette - vibrant gradient colors
  const colorPalette = [
    "#6366f1", "#8b5cf6", "#a855f7", "#d946ef", "#ec4899", "#f43f5e",
    "#06b6d4", "#14b8a6", "#10b981", "#84cc16", "#eab308", "#f97316"
  ];

  // 9. Render
  return (
    <div style={cloudStyle}>
      <div style={{ 
        position: 'relative', 
        width: '100%',
        maxWidth: `${CONTAINER_WIDTH}px`,
        height: `${CONTAINER_HEIGHT}px`,
        margin: '0 auto',
        background: 'transparent',
        overflow: 'hidden'
      }}>
        {placedWords.map((w, i) => {
          const color = colorPalette[i % colorPalette.length];
          
          if (w.rotation === 90) {
            // Render vertical text with stacked letters
            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: `${w.x}px`,
                  top: `${w.y}px`,
                  fontSize: `${w.fontSize}px`,
                  fontFamily: "'Inter', 'Arial', sans-serif",
                  color: color,
                  fontWeight: 800,
                  lineHeight: 1,
                  transform: 'translate(-50%, -50%)',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  textTransform: 'lowercase',
                  letterSpacing: '-0.02em',
                  filter: `drop-shadow(0 2px 4px ${color}40)`,
                  writingMode: 'vertical-rl',
                  textOrientation: 'upright'
                }}
                title={`${w.text} (${w.frequency})`}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translate(-50%, -50%) scale(1.3)';
                  e.currentTarget.style.color = '#ffffff';
                  e.currentTarget.style.filter = `drop-shadow(0 4px 12px ${color})`;
                  e.currentTarget.style.zIndex = 100;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translate(-50%, -50%)';
                  e.currentTarget.style.color = color;
                  e.currentTarget.style.filter = `drop-shadow(0 2px 4px ${color}40)`;
                  e.currentTarget.style.zIndex = 10;
                }}
              >
                {w.text}
              </div>
            );
          }
          
          // Render horizontal text in SVG
          return (
            <svg
              key={i}
              style={{
                position: 'absolute',
                left: `${w.x}px`,
                top: `${w.y}px`,
                overflow: 'visible',
                pointerEvents: 'none'
              }}
            >
              <text
                x={0}
                y={0}
                fontSize={w.fontSize}
                fontFamily="'Inter', 'Arial', sans-serif"
                fill={color}
                fontWeight="800"
                textAnchor="middle"
                dominantBaseline="middle"
                style={{
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  textTransform: 'lowercase',
                  letterSpacing: '-0.02em',
                  filter: `drop-shadow(0 2px 4px ${color}40)`,
                  pointerEvents: 'auto'
                }}
                onMouseEnter={(e) => {
                  e.target.style.fontSize = `${w.fontSize * 1.3}px`;
                  e.target.style.fill = '#ffffff';
                  e.target.style.filter = `drop-shadow(0 4px 12px ${color})`;
                }}
                onMouseLeave={(e) => {
                  e.target.style.fontSize = `${w.fontSize}px`;
                  e.target.style.fill = color;
                  e.target.style.filter = `drop-shadow(0 2px 4px ${color}40)`;
                }}
              >
                <title>{`${w.text} (${w.frequency})`}</title>
                {w.text}
              </text>
            </svg>
          );
        })}
      </div>
    </div>
  )
}

const cloudStyle = {
  width: "100%",
  minHeight: "300px", 
  height: "100%",
  background: "transparent",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  position: "relative",
  overflow: "hidden"
}