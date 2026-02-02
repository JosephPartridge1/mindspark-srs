import React from 'react';

function Flashcard({ item, showMeaning, onToggleMeaning, onHint }) {
  const displayMeaning = showMeaning || item.hintUsed;
  const truncatedExample = item.example ? item.example.substring(0, 50) + '...' : '';

  return (
    <article role="article" aria-live="polite">
      <h2>{item.word}</h2>
      {displayMeaning && <p>Meaning: {item.meaning}</p>}
      {item.hintUsed && <p>Example: {truncatedExample}</p>}
      <button onClick={onToggleMeaning}>Show Meaning</button>
      <button onClick={onHint}>Hint</button>
    </article>
  );
}

export default Flashcard;
