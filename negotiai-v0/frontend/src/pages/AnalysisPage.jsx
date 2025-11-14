// frontend/src/pages/AnalysisPage.jsx
import React, { useState } from 'react';
import { analyzeNegotiation, downloadAnalysisPdf } from '../services/api';

function AnalysisPage({ strategy, onAnalysisComplete, analysis }) {
  const [transcript, setTranscript] = useState('');
  const [outcome, setOutcome] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [localAnalysis, setLocalAnalysis] = useState(analysis);

  const handleAnalyze = async () => {
    if (!transcript || !outcome) {
      alert('Please provide both transcript and outcome');
      return;
    }

    setIsAnalyzing(true);
    try {
      const result = await analyzeNegotiation({
        session_id: strategy.session_id,
        transcript,
        actual_outcome: outcome
      });
      setLocalAnalysis(result);
      onAnalysisComplete(result);
    } catch (error) {
      const errorMessage = error.message || 'Unknown error';

      // Check if it's a rate limit error
      if (errorMessage.includes('rate limit') || errorMessage.includes('429')) {
        alert(
          '⚠️ Rate Limit Exceeded\n\n' +
          'Mistral AI has strict rate limits. Please wait 30 seconds and try again.\n\n' +
          'Tip: The free tier has low limits. Consider upgrading your Mistral AI plan for production use.'
        );
      } else {
        alert('Error analyzing negotiation: ' + errorMessage);
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadPdf = async () => {
    try {
      await downloadAnalysisPdf(strategy.session_id);
    } catch (error) {
      alert('Error downloading PDF: ' + error.message);
    }
  };

  if (isAnalyzing) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>🔍 Analyzing your performance...</p>
      </div>
    );
  }

  if (!localAnalysis) {
    return (
      <div className="analysis-page">
        <h2>📝 Post-Negotiation Analysis</h2>
        <p className="subtitle">Paste your negotiation transcript and outcome</p>

        <div className="form-section">
          <label>
            <strong>1. Full Transcript *</strong>
            <textarea
              rows={12}
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste the complete conversation transcript here...

Example format:
Me: Hello, I'd like to discuss the contract terms
Them: Sure, we're proposing 40K for the annual license
Me: Based on the value we provide, I think 55K is more appropriate
..."
            />
          </label>

          <label>
            <strong>2. Actual Outcome *</strong>
            <input
              type="text"
              value={outcome}
              onChange={(e) => setOutcome(e.target.value)}
              placeholder="e.g., Closed at 48K€ with 3-month trial"
            />
          </label>

          <button
            className="primary-button"
            onClick={handleAnalyze}
            disabled={!transcript || !outcome}
          >
            Analyze Performance
          </button>
        </div>
      </div>
    );
  }

  const { performance, tactics_used, strengths, weaknesses, key_recommendations } = localAnalysis;

  return (
    <div className="analysis-page results">
      <h2>📊 Performance Analysis</h2>

      {/* Score Cards */}
      <div className="score-grid">
        <div className="score-card overall">
          <h3>Overall</h3>
          <div className="score">{performance.overall_score}</div>
          <div className="score-bar">
            <div
              className="score-fill"
              style={{width: `${performance.overall_score}%`}}
            ></div>
          </div>
        </div>
        <div className="score-card">
          <h4>Preparation</h4>
          <div className="score-small">{performance.preparation_score}</div>
        </div>
        <div className="score-card">
          <h4>Tactics</h4>
          <div className="score-small">{performance.tactics_score}</div>
        </div>
        <div className="score-card">
          <h4>Outcome</h4>
          <div className="score-small">{performance.outcome_score}</div>
        </div>
      </div>

      {/* Audio Feedback */}
      {localAnalysis.audio_url && (
        <div className="audio-feedback">
          <h3>🎧 Audio Feedback</h3>
          <audio controls src={`http://localhost:8000${localAnalysis.audio_url}`}>
            Your browser does not support audio
          </audio>
        </div>
      )}

      {/* Tactics Detected */}
      <div className="analysis-card">
        <h3>🎯 Tactics Detected</h3>
        <div className="tactics-grid">
          {tactics_used.map((tactic, i) => (
            <div key={i} className={`tactic-card ${tactic.effectiveness}`}>
              <h4>{tactic.tactic_name}</h4>
              <span className="tactic-type">{tactic.tactic_type}</span>
              <p className="quote">"{tactic.quote}"</p>
              <p className="explanation">{tactic.explanation}</p>
              <span className={`effectiveness-badge ${tactic.effectiveness}`}>
                {tactic.effectiveness}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths */}
      <div className="analysis-card positive">
        <h3>✅ Strengths</h3>
        <ul>
          {strengths.map((strength, i) => (
            <li key={i}>{strength}</li>
          ))}
        </ul>
      </div>

      {/* Weaknesses */}
      <div className="analysis-card negative">
        <h3>⚠️ Areas for Improvement</h3>
        <ul>
          {weaknesses.map((weakness, i) => (
            <li key={i}>{weakness}</li>
          ))}
        </ul>
      </div>

      {/* Recommendations */}
      <div className="analysis-card">
        <h3>💡 Key Recommendations</h3>
        <ol className="recommendations">
          {key_recommendations.map((rec, i) => (
            <li key={i}>{rec}</li>
          ))}
        </ol>
      </div>

      <div className="action-buttons">
        <button className="secondary-button" onClick={handleDownloadPdf}>
          📄 Download PDF Report
        </button>
        <button
          className="secondary-button"
          onClick={() => window.location.reload()}
        >
          Start New Negotiation
        </button>
      </div>
    </div>
  );
}

export default AnalysisPage;
