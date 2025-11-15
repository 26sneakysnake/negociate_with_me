import React from 'react';

/**
 * Call Results Component
 * Displays analysis of completed phone negotiation
 */
export default function CallResults({ results }) {
  if (!results || !results.analysis) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
        <p>Chargement des résultats...</p>
      </div>
    );
  }

  const analysis = results.analysis;
  const scores = analysis.scores || {};
  const outcome = analysis.outcome || {};
  const performance = analysis.user_performance || { good: [], bad: [] };

  // Calculate score color
  const getScoreColor = (score) => {
    if (score >= 8) return '#4caf50'; // Green
    if (score >= 6) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  // Get winner emoji
  const getWinnerEmoji = (winner) => {
    if (winner === 'user') return '🏆';
    if (winner === 'opponent') return '😔';
    return '🤝';
  };

  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '24px',
        borderRadius: '12px',
        marginBottom: '24px',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: '0 0 12px 0', fontSize: '28px' }}>
          📊 Résultats de votre Négociation
        </h1>
        <p style={{ margin: 0, opacity: 0.9 }}>
          Durée: {Math.floor((results.duration || 0) / 60)}:{String((results.duration || 0) % 60).padStart(2, '0')}
        </p>
      </div>

      {/* Global Score */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '32px',
        marginBottom: '24px',
        textAlign: 'center'
      }}>
        <h2 style={{ marginTop: 0, marginBottom: '16px' }}>Score Global</h2>
        <div style={{
          fontSize: '72px',
          fontWeight: 'bold',
          color: getScoreColor(scores.global),
          marginBottom: '16px'
        }}>
          {scores.global || 0}/10
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '16px',
          marginTop: '24px'
        }}>
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
              Préparation
            </div>
            <div style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: getScoreColor(scores.preparation)
            }}>
              {scores.preparation || 0}/10
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
              Argumentation
            </div>
            <div style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: getScoreColor(scores.argumentation)
            }}>
              {scores.argumentation || 0}/10
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
              Gestion objections
            </div>
            <div style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: getScoreColor(scores.objection_handling)
            }}>
              {scores.objection_handling || 0}/10
            </div>
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
              Résultat
            </div>
            <div style={{
              fontSize: '24px',
              fontWeight: 'bold',
              color: getScoreColor(scores.outcome)
            }}>
              {scores.outcome || 0}/10
            </div>
          </div>
        </div>
      </div>

      {/* Outcome */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
          {getWinnerEmoji(outcome.winner)} Résultat de la négociation
        </h3>

        <div style={{
          background: '#f5f5f5',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '12px'
        }}>
          <strong>Accord final :</strong> {outcome.final_deal || 'Non spécifié'}
        </div>

        <div style={{
          background: '#e3f2fd',
          borderRadius: '8px',
          padding: '16px'
        }}>
          <strong>Analyse :</strong> {outcome.reason || 'Non disponible'}
        </div>
      </div>

      {/* Patterns Detected */}
      {analysis.patterns_detected && analysis.patterns_detected.length > 0 && (
        <div style={{
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px'
        }}>
          <h3 style={{ marginTop: 0 }}>🎯 Tactiques détectées</h3>
          <p style={{ color: '#666', fontSize: '14px', marginTop: '-8px' }}>
            Voici les tactiques utilisées par votre opponent :
          </p>

          <ul style={{
            listStyle: 'none',
            padding: 0,
            margin: 0
          }}>
            {analysis.patterns_detected.map((pattern, i) => (
              <li key={i} style={{
                background: '#f5f5f5',
                borderRadius: '8px',
                padding: '12px 12px 12px 40px',
                marginBottom: '8px',
                position: 'relative'
              }}>
                <span style={{
                  position: 'absolute',
                  left: '12px',
                  top: '12px'
                }}>
                  🎪
                </span>
                {pattern}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* User Performance */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h3 style={{ marginTop: 0 }}>📈 Votre Performance</h3>

        {/* Good responses */}
        {performance.good && performance.good.length > 0 && (
          <div style={{ marginBottom: '24px' }}>
            <h4 style={{
              color: '#4caf50',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              ✅ Bonnes réponses
            </h4>

            {performance.good.map((item, i) => (
              <div key={i} style={{
                background: '#e8f5e9',
                borderLeft: '4px solid #4caf50',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '12px'
              }}>
                <div style={{
                  fontStyle: 'italic',
                  marginBottom: '8px',
                  color: '#333'
                }}>
                  "{item.quote}"
                </div>
                <div style={{
                  fontSize: '14px',
                  color: '#2e7d32'
                }}>
                  👍 {item.analysis}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Bad responses */}
        {performance.bad && performance.bad.length > 0 && (
          <div>
            <h4 style={{
              color: '#f44336',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              ❌ À améliorer
            </h4>

            {performance.bad.map((item, i) => (
              <div key={i} style={{
                background: '#ffebee',
                borderLeft: '4px solid #f44336',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '12px'
              }}>
                <div style={{
                  fontStyle: 'italic',
                  marginBottom: '8px',
                  color: '#333'
                }}>
                  "{item.quote}"
                </div>
                <div style={{
                  fontSize: '14px',
                  color: '#c62828'
                }}>
                  👎 {item.analysis}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Improvements */}
      {analysis.improvements && analysis.improvements.length > 0 && (
        <div style={{
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px'
        }}>
          <h3 style={{ marginTop: 0 }}>💡 Recommandations</h3>
          <p style={{ color: '#666', fontSize: '14px', marginTop: '-8px' }}>
            Pour votre prochaine négociation :
          </p>

          <ol style={{
            paddingLeft: '24px',
            margin: 0
          }}>
            {analysis.improvements.map((improvement, i) => (
              <li key={i} style={{
                background: '#fff3cd',
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '12px',
                listStylePosition: 'inside'
              }}>
                {improvement}
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Transcript */}
      {results.transcript && (
        <div style={{
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '12px',
          padding: '24px'
        }}>
          <h3 style={{ marginTop: 0 }}>📝 Transcript complet</h3>

          <div style={{
            background: '#f5f5f5',
            borderRadius: '8px',
            padding: '16px',
            maxHeight: '400px',
            overflowY: 'auto',
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace',
            fontSize: '13px',
            lineHeight: '1.6'
          }}>
            {results.transcript}
          </div>

          {results.recording_url && (
            <div style={{ marginTop: '16px' }}>
              <a
                href={results.recording_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-block',
                  padding: '12px 24px',
                  background: '#2196f3',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '8px',
                  fontWeight: 'bold'
                }}
              >
                🎧 Écouter l'enregistrement
              </a>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{
        marginTop: '32px',
        display: 'flex',
        gap: '12px',
        justifyContent: 'center'
      }}>
        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '16px 32px',
            fontSize: '16px',
            fontWeight: 'bold',
            color: 'white',
            background: 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          🔄 Nouvel entraînement
        </button>

        <button
          onClick={() => window.print()}
          style={{
            padding: '16px 32px',
            fontSize: '16px',
            fontWeight: 'bold',
            color: 'white',
            background: '#2196f3',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          🖨️ Imprimer le rapport
        </button>
      </div>
    </div>
  );
}
