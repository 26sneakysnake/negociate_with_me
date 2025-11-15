import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Step4Briefing.css';

function Step4Briefing({ sessionData, updateSessionData, goToStep }) {
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [transcript, setTranscript] = useState(null);

  useEffect(() => {
    // Poll pour récupérer l'analyse
    const fetchAnalysis = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/call/analysis/${sessionData.session_id}`
        );

        if (response.data.status === 'completed') {
          setAnalysis(response.data.analysis);
          setTranscript(response.data.transcript);
          updateSessionData({
            analysis: response.data.analysis,
            transcript: response.data.transcript,
            duration: response.data.duration
          });
          setLoading(false);
        } else if (response.data.status === 'analyzing') {
          // Retry après 2 secondes
          setTimeout(fetchAnalysis, 2000);
        }
      } catch (error) {
        console.error('Analysis fetch error:', error);
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [sessionData.session_id]);

  if (loading) {
    return (
      <div className="step4-briefing">
        <div className="loading-container">
          <div className="spinner-large"></div>
          <h2>🎯 Analyse de votre négociation en cours...</h2>
          <p>Mistral AI analyse votre performance. Quelques secondes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="step4-briefing">
      <div className="step-header">
        <h1>📝 Briefing de la négociation</h1>
        <p>Voici la transcription et un aperçu de votre performance</p>
      </div>

      {transcript && (
        <div className="transcript-section">
          <h2>💬 Transcription de la conversation</h2>
          <div className="transcript-box">
            <pre>{transcript}</pre>
          </div>
        </div>
      )}

      {analysis && (
        <div className="quick-stats">
          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            <div className="stat-value">{analysis.score}/100</div>
            <div className="stat-label">Score global</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              {analysis.outcome === 'success' ? '✅' :
               analysis.outcome === 'partial' ? '🤝' : '❌'}
            </div>
            <div className="stat-value">
              {analysis.outcome === 'success' ? 'Succès' :
               analysis.outcome === 'partial' ? 'Partiel' : 'Échec'}
            </div>
            <div className="stat-label">Résultat</div>
          </div>

          {analysis.price_negotiated && (
            <div className="stat-card">
              <div className="stat-icon">💰</div>
              <div className="stat-value">{analysis.price_negotiated}</div>
              <div className="stat-label">Prix final</div>
            </div>
          )}

          <div className="stat-card">
            <div className="stat-icon">🎪</div>
            <div className="stat-value">{analysis.tactics_used?.length || 0}</div>
            <div className="stat-label">Tactiques utilisées</div>
          </div>
        </div>
      )}

      <div className="step-actions">
        <button onClick={() => goToStep(3)} className="back-btn">
          ← Retour
        </button>
        <button onClick={() => goToStep(5)} className="next-btn">
          Voir le score détaillé →
        </button>
      </div>
    </div>
  );
}

export default Step4Briefing;
