export default function WordCloud({ words = [] }) {
  if (!words || words.length === 0) {
    return (
      <div style={cloudStyle}>
        <p style={{ color: "#999", textAlign: "center", fontSize: "16px", paddingTop: "40px" }}>
          No words yet. Submit your first answer!
        </p>
      </div>
    )
  }

  // Calculate min and max frequencies for normalization
  const frequencies = words.map(w => w.value || w.frequency || 1);
  const minFreq = Math.min(...frequencies);
  const maxFreq = Math.max(...frequencies);
  
  // Function to calculate font size based on frequency
  const getFontSize = (freq) => {
    const normalized = (freq - minFreq) / (maxFreq - minFreq || 1);
    // Size ranges from 16px to 64px
    return Math.max(16, Math.min(64, 16 + normalized * 48));
  };

  // Extended vibrant color palette with distinct colors
  const colorPalette = [
    "#FF1493", // Deep Pink
    "#FF69B4", // Hot Pink
    "#FF00FF", // Magenta
    "#8B008B", // Dark Magenta
    "#8B0000", // Dark Red
    "#DC143C", // Crimson
    "#FF4500", // Orange Red
    "#FF6347", // Tomato
    "#CD5C5C", // Indian Red
    "#800080", // Purple
    "#4B0082", // Indigo
    "#6A0DAD", // Blue Violet
    "#1E90FF", // Dodger Blue
    "#00008B", // Dark Blue
    "#0000CD", // Medium Blue
    "#4169E1", // Royal Blue
    "#008000", // Green
    "#32CD32", // Lime Green
    "#00CED1", // Dark Turquoise
    "#20B2AA", // Light Sea Green
    "#008B8B", // Dark Cyan
    "#2F4F4F", // Dark Slate Gray
    "#FF8C00", // Dark Orange
    "#FFD700", // Gold
    "#FFA500", // Orange
    "#FF69B4", // Hot Pink
    "#FF1493", // Deep Pink
    "#C71585", // Medium Violet Red
    "#DB7093", // Pale Violet Red
    "#FF00FF", // Magenta
  ];

  // Function to generate distinct colors using HSL
  const generateDistinctColor = (index, total) => {
    if (words[index]?.color) {
      return words[index].color;
    }
    
    // If we have pre-assigned colors from backend, use them
    if (colorPalette[index % colorPalette.length]) {
      return colorPalette[index % colorPalette.length];
    }
    
    // Otherwise generate a new color based on index
    const hue = (index / Math.max(total, 1)) * 360;
    const saturation = 70 + (index % 3) * 10; // 70-90%
    const lightness = 45 + (index % 2) * 10; // 45-55%
    return `hsl(${Math.floor(hue)}, ${saturation}%, ${lightness}%)`;
  };

  return (
    <div style={cloudStyle}>
      <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "12px" }}>
        {words.map((w, index) => {
          const fontSize = w.size ? w.size : getFontSize(w.value || w.frequency || 1);
          const color = generateDistinctColor(index, words.length);
          
          return (
            <span
              key={index}
              style={{
                fontSize: `${fontSize}px`,
                fontWeight: fontSize > 40 ? "bold" : fontSize > 28 ? "600" : "500",
                color: color,
                display: "inline-block",
                padding: "4px 8px",
                margin: "4px",
                cursor: "default",
                transition: "all 0.3s ease",
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                textShadow: "1px 1px 2px rgba(0,0,0,0.1)",
                userSelect: "none"
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = "scale(1.1)";
                e.target.style.filter = "brightness(0.85)";
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = "scale(1)";
                e.target.style.filter = "brightness(1)";
              }}
            >
              {w.text || w.word}
            </span>
          );
        })}
      </div>
    </div>
  )
}

const cloudStyle = {
  border: "2px solid #e0e0e0",
  padding: "24px",
  minHeight: "200px",
  borderRadius: "12px",
  background: "linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%)",
  textAlign: "center",
  boxShadow: "0 4px 6px rgba(0, 0, 0, 0.07)"
}