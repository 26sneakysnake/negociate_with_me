// frontend/src/pages/HistoryPage.jsx
import React, { useState, useEffect } from 'react';
import { getSessions, getPerformanceHistory } from '../services/api';

function HistoryPage({ onNewNegotiation }) {
  const [sessions, setSessions] = useState([]);
  const [performanceData, setPerformanceData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState(null);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const [sessionsData, perfData] = await Promise.all([
          getSessions(),
          getPerformanceHistory()
        ]);
        setSessions(sessionsData);
        setPerformanceData(perfData);
      } catch (error) {
        console.error('Failed to load history:', error);
        alert('Failed to load negotiation history: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading your negotiation history...</p>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#4CAF50';
    if (score >= 60) return '#FFC107';
    return '#FF5722';
  };

  // Calculate average improvement
  const getAverageScore = () => {
    if (!performanceData || !performanceData.sessions || performanceData.sessions.length === 0) return 0;
    const total = performanceData.sessions.reduce((sum, s) => sum + s.score, 0);
    return Math.round(total / performanceData.sessions.length);
  };

  const getImprovement = () => {
    if (!performanceData || !performanceData.sessions || performanceData.sessions.length < 2) return null;
    const sessions = performanceData.sessions;
    const firstScore = sessions[0].score;
    const lastScore = sessions[sessions.length - 1].score;
    const diff = lastScore - firstScore;
    return diff;
  };

  const improvement = getImprovement();

  return (
    <div className="history-page">
      <div className="history-header">
        <h2>📊 Negotiation History</h2>
        <button className="primary-button" onClick={onNewNegotiation}>
          + New Negotiation
        </button>
      </div>

      {/* Performance Summary */}
      {performanceData && performanceData.sessions && performanceData.sessions.length > 0 && (
        <div className="performance-summary">
          <div className="stat-card">
            <h3>Total Negotiations</h3>
            <div className="stat-value">{sessions.length}</div>
          </div>
          <div className="stat-card">
            <h3>Average Score</h3>
            <div className="stat-value">{getAverageScore()}/100</div>
          </div>
          {improvement !== null && (
            <div className="stat-card">
              <h3>Progress</h3>
              <div className="stat-value" style={{ color: improvement >= 0 ? '#4CAF50' : '#FF5722' }}>
                {improvement >= 0 ? '+' : ''}{improvement} points
              </div>
              <p className="stat-subtitle">
                {improvement >= 0
                  ? `You've improved by ${improvement} points!`
                  : `Room for improvement: ${Math.abs(improvement)} points`}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Performance Chart */}
      {performanceData && performanceData.sessions && performanceData.sessions.length > 1 && (
        <div className="performance-chart-container">
          <h3>📈 Performance Over Time</h3>
          <div className="simple-chart">
            {performanceData.sessions.map((session, i) => (
              <div key={i} className="chart-bar-container">
                <div
                  className="chart-bar"
                  style={{
                    height: `${session.score}%`,
                    backgroundColor: getScoreColor(session.score)
                  }}
                >
                  <span className="chart-label">{session.score}</span>
                </div>
                <div className="chart-date">{formatDate(session.date)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sessions List */}
      <div className="sessions-list">
        <h3>All Negotiations</h3>
        {sessions.length === 0 ? (
          <div className="empty-state">
            <p>No negotiations yet. Start your first one!</p>
            <button className="primary-button" onClick={onNewNegotiation}>
              Start First Negotiation
            </button>
          </div>
        ) : (
          <div className="sessions-grid">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="session-card"
                onClick={() => setSelectedSession(selectedSession === session.id ? null : session.id)}
              >
                <div className="session-header">
                  <div className="session-date">{formatDate(session.created_at)}</div>
                  {session.overall_score && (
                    <div
                      className="session-score"
                      style={{ backgroundColor: getScoreColor(session.overall_score) }}
                    >
                      {session.overall_score}/100
                    </div>
                  )}
                </div>
                <div className="session-objective">
                  <strong>Objective:</strong> {session.objective}
                </div>
                {session.actual_outcome && (
                  <div className="session-outcome">
                    <strong>Outcome:</strong> {session.actual_outcome}
                  </div>
                )}
                {selectedSession === session.id && (
                  <div className="session-details">
                    <div className="session-context">
                      <strong>Context:</strong>
                      <p>{session.context_text.substring(0, 200)}...</p>
                    </div>
                    <div className="session-scores">
                      {session.preparation_score && (
                        <span className="mini-score">
                          Prep: {session.preparation_score}
                        </span>
                      )}
                      {session.tactics_score && (
                        <span className="mini-score">
                          Tactics: {session.tactics_score}
                        </span>
                      )}
                      {session.outcome_score && (
                        <span className="mini-score">
                          Outcome: {session.outcome_score}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default HistoryPage;
