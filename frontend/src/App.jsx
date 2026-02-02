import React, { useState, useEffect } from 'react';
import Home from './pages/Home';
import Session from './pages/Session';

function App() {
  const [userId, setUserId] = useState(null);
  const [sessionSize, setSessionSize] = useState(10);

  useEffect(() => {
    const storedUserId = localStorage.getItem('srs_user_id');
    if (storedUserId) {
      setUserId(storedUserId);
    }
  }, []);

  const handleLogin = (newUserId, newSessionSize) => {
    setUserId(newUserId);
    setSessionSize(newSessionSize);
    localStorage.setItem('srs_user_id', newUserId);
  };

  if (!userId) {
    return <Home onLogin={handleLogin} />;
  }

  return <Session userId={userId} sessionSize={sessionSize} />;
}

export default App;
