import React, { useMemo } from 'react';

const NODE_COUNT = 22; // keep light for performance
const CONNECT_DISTANCE = 18; // percentage of min(viewBox)

function distance(a, b) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
}

const NodeNetworkBackground = () => {
  const nodes = useMemo(() => {
    // Generate stable pseudo-random nodes in percentage space (0-100)
    const list = Array.from({ length: NODE_COUNT }).map((_, i) => ({
      id: i,
      x: Math.round((Math.sin(i * 12.9898) * 43758.5453) % 100) / 1 + Math.random() * 2,
      y: Math.round((Math.cos(i * 78.233) * 19341.5927) % 100) / 1 + Math.random() * 2,
    }));
    // Normalize to inside bounds 6-94 to avoid edges
    return list.map(n => ({ id: n.id, x: Math.max(6, Math.min(94, Math.abs(n.x))), y: Math.max(6, Math.min(94, Math.abs(n.y))) }));
  }, []);

  const edges = useMemo(() => {
    const conns = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const d = distance(nodes[i], nodes[j]);
        if (d < CONNECT_DISTANCE) {
          conns.push({ id: `${i}-${j}`, a: nodes[i], b: nodes[j], opacity: Math.max(0.06, 0.18 - d / 100) });
        }
      }
    }
    return conns;
  }, [nodes]);

  return (
    <div className="node-network">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" width="100%" height="100%">
        {edges.map(e => (
          <line
            key={e.id}
            x1={e.a.x}
            y1={e.a.y}
            x2={e.b.x}
            y2={e.b.y}
            stroke="rgba(0,0,0,0.10)"
            strokeWidth="0.25"
            opacity={e.opacity}
          />
        ))}
        {nodes.map(n => (
          <circle key={n.id} cx={n.x} cy={n.y} r="0.8" className="node-dot" />
        ))}
      </svg>
    </div>
  );
};

export default NodeNetworkBackground;
