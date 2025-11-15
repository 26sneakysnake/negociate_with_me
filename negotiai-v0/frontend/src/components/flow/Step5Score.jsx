import React from 'react';
import './Step5Score.css';

function Step5Score({ sessionData, goToStep }) {
  const { analysis } = sessionData;

  if (!analysis) {
    return (
      <div className="step5-score">
        <p>Aucune analyse disponible</p>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FF9800';
    return '#f44336';
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excellent !';
    if (score >= 70) return 'Très bien !';
    if (score >= 50) return 'Correct';
    if (score >= 30) return 'Peut mieux faire';
    return 'À améliorer';
  };

  return (
    <div className="step5-score">
      <div className="step-header">
        <h1>⭐ Votre Score de Négociation</h1>
        <p>Analyse détaillée de votre performance</p>
      </div>

      {/* Score principal */}
      <div className="score-hero" style={{ borderColor: getScoreColor(analysis.score) }}>
        <div className="score-circle" style={{ borderColor: getScoreColor(analysis.score) }}>
          <div className="score-value" style={{ color: getScoreColor(analysis.score) }}>
            {analysis.score}
          </div>
          <div className="score-max">/100</div>
        </div>
        <div className="score-label">{getScoreLabel(analysis.score)}</div>
        <div className="outcome-badge" style={{ background: getScoreColor(analysis.score) }}>
          {analysis.outcome === 'success' ? '✅ Succès' :
           analysis.outcome === 'partial' ? '🤝 Compromis' : '❌ Échec'}
        </div>
      </div>

      {/* Forces */}
      <div className="analysis-section">
        <h2>💪 Points forts</h2>
        <div className="analysis-grid">
          {analysis.strengths && analysis.strengths.map((strength, index) => (
            <div key={index} className="analysis-card strength">
              <span className="card-icon">✅</span>
              <span className="card-text">{strength}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Faiblesses */}
      <div className="analysis-section">
        <h2>⚠️ Points à améliorer</h2>
        <div className="analysis-grid">
          {analysis.weaknesses && analysis.weaknesses.map((weakness, index) => (
            <div key={index} className="analysis-card weakness">
              <span className="card-icon">❌</span>
              <span className="card-text">{weakness}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tactiques utilisées */}
      {analysis.tactics_used && analysis.tactics_used.length > 0 && (
        <div className="analysis-section">
          <h2>🎪 Tactiques utilisées</h2>
          <div className="tactics-list">
            {analysis.tactics_used.map((tactic, index) => (
              <span key={index} className="tactic-badge">{tactic}</span>
            ))}
          </div>
        </div>
      )}

      {/* Recommandations */}
      <div className="analysis-section">
        <h2>💡 Recommandations pour progresser</h2>
        <div className="recommendations-list">
          {analysis.recommendations && analysis.recommendations.map((rec, index) => (
            <div key={index} className="recommendation-item">
              <span className="rec-number">{index + 1}</span>
              <span className="rec-text">{rec}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Actions finales */}
      <div className="final-actions">
        <button onClick={() => goToStep(1)} className="restart-btn">
          🔄 Nouvelle négociation
        </button>
        <button onClick={() => goToStep(4)} className="review-btn">
          📝 Revoir le briefing
        </button>
      </div>
    </div>
  );
}

export default Step5Score;
