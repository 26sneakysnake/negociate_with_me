import React from 'react';

export default function SuggestionPanel({ suggestions, onAutoPilot }) {
  if (!suggestions || suggestions.length === 0) {
    return (
      <div className="suggestion-panel empty">
        <p>💭 En attente de suggestions tactiques...</p>
      </div>
    );
  }

  const latest = suggestions[suggestions.length - 1];

  const priorityConfig = {
    critical: {
      color: 'red',
      bg: '#fee',
      border: '#f88'
    },
    high: {
      color: 'orange',
      bg: '#fff3e0',
      border: '#ffb74d'
    },
    medium: {
      color: 'blue',
      bg: '#e3f2fd',
      border: '#64b5f6'
    },
    info: {
      color: 'gray',
      bg: '#f5f5f5',
      border: '#bdbdbd'
    }
  };

  const config = priorityConfig[latest.priority] || priorityConfig.info;

  const typeEmojis = {
    counter: '🛡️',
    warning: '⚠️',
    opportunity: '✅',
    info: '💬'
  };

  return (
    <div
      className="suggestion-panel"
      style={{
        backgroundColor: config.bg,
        borderLeft: `4px solid ${config.border}`,
        padding: '16px',
        borderRadius: '8px',
        marginBottom: '16px',
        animation: 'slideIn 0.3s ease-out'
      }}
    >
      <div className="suggestion-header" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '8px'
      }}>
        <span className="type-badge" style={{ fontSize: '14px', opacity: 0.7 }}>
          {typeEmojis[latest.type] || '💡'} {latest.type.toUpperCase()}
        </span>
        <span className="priority-badge" style={{
          fontSize: '11px',
          fontWeight: 'bold',
          color: config.color,
          textTransform: 'uppercase'
        }}>
          {latest.priority}
        </span>
      </div>

      <div className="suggestion-text" style={{
        fontSize: '18px',
        fontWeight: '600',
        color: '#333',
        marginBottom: '12px',
        lineHeight: '1.4'
      }}>
        {latest.suggestion}
      </div>

      {latest.reasoning && (
        <div className="suggestion-reasoning" style={{
          fontSize: '13px',
          color: '#666',
          fontStyle: 'italic',
          marginBottom: '12px'
        }}>
          {latest.reasoning}
        </div>
      )}

      {latest.autopilot_available && latest.tactic && (
        <div className="autopilot-hint" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          marginTop: '12px',
          paddingTop: '12px',
          borderTop: '1px solid rgba(0,0,0,0.1)'
        }}>
          <span style={{ fontSize: '13px', color: '#666' }}>
            ⚡ Auto-pilot disponible
          </span>
          <button
            onClick={() => onAutoPilot(latest.tactic)}
            className="autopilot-activate-btn"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '600',
              transition: 'transform 0.2s',
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            🤖 Activer
          </button>
        </div>
      )}

      {latest.pattern_matched && (
        <div style={{ fontSize: '11px', color: '#999', marginTop: '8px' }}>
          Pattern détecté: {latest.pattern_matched} ({Math.round((latest.confidence || 0) * 100)}% confiance)
        </div>
      )}
    </div>
  );
}
