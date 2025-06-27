import React from 'react';
export default function SudokuGrid({ grid }) {
  return (
    <div className="grid">
      {grid.flat().map((n,i) => (
        <div key={i} className="cell">{n}</div>
      ))}
    </div>
  );
}
