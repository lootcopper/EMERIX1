import React, { useState, useEffect } from 'react';

const PulseBackground = () => {
  const [elements, setElements] = useState([]);

  useEffect(() => {
    // Generate elements once on mount - 20x15 = 300 cells
    const newElements = Array.from({ length: 300 }, (_, i) => {
      const cellElements = [];
      
      // 20% chance of having elements in each cell (reduced from 50%)
      if (Math.random() > 0.8) {
        const shapeTypes = ['dot', 'circle', 'square']; // Reduced shape variety
        
        // Only 1-2 elements per cell (reduced from 1-3)
        const numElements = Math.floor(Math.random() * 2) + 1;
        
        for (let j = 0; j < numElements; j++) {
          const randomType = shapeTypes[Math.floor(Math.random() * shapeTypes.length)];
          const isRotating = ['diamond', 'cross', 'star'].includes(randomType) && Math.random() > 0.7;
          
          cellElements.push({
            type: randomType,
            id: `${i}-${randomType}-${j}`,
            delay: Math.random() * 6,
            top: Math.random() * 80 + 10,
            left: Math.random() * 80 + 10,
            rotating: isRotating
          });
        }
      }
      
      return { cellId: i, elements: cellElements };
    });
    
    setElements(newElements);
  }, []);

  return (
    <div className="pulse-background">
      <div className="pulse-grid">
        {elements.map(({ cellId, elements: cellElements }) => (
          <div key={cellId} className="pulse-cell">
            {cellElements.map((element) => (
              <div
                key={element.id}
                className={`pulse-${element.type}${element.rotating ? ' rotating' : ''}`}
                style={{
                  animationDelay: `${element.delay}s`,
                  top: `${element.top}%`,
                  left: `${element.left}%`
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PulseBackground;
