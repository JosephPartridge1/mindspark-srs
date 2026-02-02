import React, { useState, useEffect } from 'react';
import { get, post } from '../api/apiClient';
import Flashcard from '../components/Flashcard';
import ProgressRing from '../components/ProgressRing';
import ResultsModal from '../components/ResultsModal';

function Session({ userId, sessionSize }) {
  const [items, setItems] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showMeaning, setShowMeaning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hintUsed, setHintUsed] = useState(false);
  const [stats, setStats] = useState({ correct: 0, partial: 0, wrong: 0 });
  const [sessionEnded, setSessionEnded] = useState(false);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = await get(`/session/start?user_id=${userId}&size=${sessionSize}`);
        setItems(data.items);
      } catch (error) {
        alert('Failed to start session');
      }
    };
    fetchSession();
  }, [userId, sessionSize]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (loading) return;
      switch (e.key) {
        case '1':
          handleAnswer('correct');
          break;
        case '2':
          handleAnswer('partial');
          break;
        case '3':
          handleAnswer('wrong');
          break;
        case ' ':
        case 'Enter':
          e.preventDefault();
          setShowMeaning(!showMeaning);
          break;
        case 'ArrowLeft':
          setCurrentIndex(Math.max(0, currentIndex - 1));
          break;
        case 'ArrowRight':
          setCurrentIndex(Math.min(items.length - 1, currentIndex + 1));
          break;
        default:
          break;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [loading, showMeaning, currentIndex, items.length]);

  const handleAnswer = async (quality) => {
    if (loading) return;
    setLoading(true);
    try {
      const payload = {
        user_id: userId,
        item_id: items[currentIndex].id,
        quality,
        hint_used: hintUsed
      };
      const response = await post('/session/answer', payload);
      alert(`Next review: ${response.next_review}`);
      setStats(prev => ({ ...prev, [quality]: prev[quality] + 1 }));
      if (currentIndex < items.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setShowMeaning(false);
        setHintUsed(false);
      } else {
        setSessionEnded(true);
      }
    } catch (error) {
      alert('Failed to submit answer');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleMeaning = () => {
    setShowMeaning(!showMeaning);
  };

  const handleHint = () => {
    setHintUsed(true);
  };

  const handleRestart = () => {
    setSessionEnded(false);
    setCurrentIndex(0);
    setShowMeaning(false);
    setHintUsed(false);
    setStats({ correct: 0, partial: 0, wrong: 0 });
    // Refetch session or reset
  };

  if (items.length === 0) return <div>Loading...</div>;

  if (sessionEnded) {
    return <ResultsModal stats={stats} onRestart={handleRestart} onDownload={() => {}} />;
  }

  const progressPercent = ((currentIndex + 1) / items.length) * 100;

  return (
    <div>
      <ProgressRing percent={progressPercent} />
      <Flashcard
        item={items[currentIndex]}
        showMeaning={showMeaning}
        onToggleMeaning={handleToggleMeaning}
        onHint={handleHint}
      />
      <button onClick={() => handleAnswer('correct')} disabled={loading}>Correct</button>
      <button onClick={() => handleAnswer('partial')} disabled={loading}>Partial</button>
      <button onClick={() => handleAnswer('wrong')} disabled={loading}>Wrong</button>
    </div>
  );
}

export default Session;
