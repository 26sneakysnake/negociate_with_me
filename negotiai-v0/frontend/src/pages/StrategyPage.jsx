// frontend/src/pages/StrategyPage.jsx
import React, { useState, useEffect } from 'react';
import { generateStrategy } from '../services/api';

function StrategyPage({ context, onStrategyGenerated, onAnalyze, strategy }) {
  const [isLoading, setIsLoading] = useState(false);
  const [localStrategy, setLocalStrategy] = useState(strategy);

  useEffect(() => {
    if (!localStrategy && context) {
      loadStrategy();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadStrategy = async () => {
    setIsLoading(true);
    try {
      const result = await generateStrategy(context);
      setLocalStrategy(result);
      onStrategyGenerated(result);
    } catch (error) {
      alert('Error generating strategy: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>🧠 Analyzing context and generating strategy...</p>
      </div>
    );
  }

  if (!localStrategy) {
    return <div>No strategy generated yet</div>;
  }

  return (
    <div className="strategy-page">
      <h2>🎯 Your Negotiation Strategy</h2>

      <div className="strategy-card">
        <h3>📊 Summary</h3>
        <p>{localStrategy.summary}</p>
      </div>

      <div className="strategy-card">
        <h3>🎬 Opening Position</h3>
        <p className="highlight">{localStrategy.opening_position}</p>
      </div>

      <div className="strategy-card">
        <h3>💪 Key Arguments</h3>
        <ul>
          {localStrategy.key_arguments.map((arg, i) => (
            <li key={i}>{arg}</li>
          ))}
        </ul>
      </div>

      <div className="strategy-card">
        <h3>🔄 Concession Plan</h3>
        <ol>
          {localStrategy.concession_plan.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </div>

      <div className="strategy-card warning">
        <h3>🚫 Red Lines (DO NOT CROSS)</h3>
        <ul>
          {localStrategy.red_lines.map((line, i) => (
            <li key={i} className="red-line">{line}</li>
          ))}
        </ul>
      </div>

      <div className="strategy-card">
        <h3>🛡️ Expected Objections & Counters</h3>
        {localStrategy.expected_objections.map((obj, i) => (
          <div key={i} className="objection-item">
            <p className="objection"><strong>Objection:</strong> "{obj.objection}"</p>
            <p className="counter"><strong>Counter:</strong> {obj.counter_argument}</p>
            <span className="confidence">Confidence: {(obj.confidence * 100).toFixed(0)}%</span>
          </div>
        ))}
      </div>

      <div className="strategy-card">
        <h3>🏃 BATNA (Best Alternative)</h3>
        <p>{localStrategy.batna}</p>
      </div>

      <div className="action-buttons">
        <button className="secondary-button" onClick={loadStrategy}>
          🔄 Regenerate Strategy
        </button>
        <button className="primary-button" onClick={onAnalyze}>
          Analyze My Negotiation →
        </button>
      </div>
    </div>
  );
}

export default StrategyPage;
