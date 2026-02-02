import React from 'react';

function ResultsModal({ stats, onRestart, onDownload }) {
  const handleDownload = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/admin/export?format=csv');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'export.csv';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      alert('Failed to download CSV');
    }
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <h2>Session Results</h2>
        <p>Correct: {stats.correct}</p>
        <p>Partial: {stats.partial}</p>
        <p>Wrong: {stats.wrong}</p>
        <button onClick={onRestart}>Restart</button>
        <button onClick={handleDownload}>Download CSV</button>
      </div>
    </div>
  );
}

export default ResultsModal;
