import React, { useState } from 'react';
import { post } from '../api/apiClient';

function Home({ onLogin }) {
  const [anonCode, setAnonCode] = useState('');
  const [className, setClassName] = useState('');
  const [sessionSize, setSessionSize] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!anonCode.trim()) {
      setError('anon_code is required');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await post('/auth/login', { anon_code: anonCode, class_name: className || undefined });
      const { user_id } = response;
      onLogin(user_id, sessionSize);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Login to SRS</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="anonCode">Anon Code:</label>
          <input
            id="anonCode"
            type="text"
            value={anonCode}
            onChange={(e) => setAnonCode(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="className">Class Name (optional):</label>
          <input
            id="className"
            type="text"
            value={className}
            onChange={(e) => setClassName(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="sessionSize">Session Size:</label>
          <select
            id="sessionSize"
            value={sessionSize}
            onChange={(e) => setSessionSize(Number(e.target.value))}
          >
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={15}>15</option>
          </select>
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
}

export default Home;
