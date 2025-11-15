import React, { useState, useRef, useEffect } from 'react';
import SuggestionPanel from './SuggestionPanel';
import AutoPilotButton from './AutoPilotButton';

export default function VoiceSimulator({ context }) {
  const [isActive, setIsActive] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [autoPilotEnabled, setAutoPilotEnabled] = useState(false);
  const [status, setStatus] = useState('ready');
  const [userInput, setUserInput] = useState('');
  const [currentTactic, setCurrentTactic] = useState(null);

  const wsRef = useRef(null);
  const audioRef = useRef(null);
  const transcriptEndRef = useRef(null);

  // Auto-scroll to bottom of transcript
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8000/ws/simulation`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log('✅ WebSocket connected');
      // Send initial context
      wsRef.current.send(JSON.stringify({
        type: 'start',
        context: context
      }));
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    wsRef.current.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setStatus('error');
    };

    wsRef.current.onclose = () => {
      console.log('👋 WebSocket closed');
      setIsActive(false);
      setStatus('disconnected');
    };
  };

  const handleWebSocketMessage = (data) => {
    console.log('📨 Received:', data.type, data);

    switch (data.type) {
      case 'status':
        setStatus(data.message);
        break;

      case 'transcript':
        setTranscript(prev => [...prev, {
          turn: data.turn,
          speaker: data.speaker,
          text: data.text,
          tactic: data.tactic
        }]);
        break;

      case 'opponent_audio':
        playAudio(data.audio);
        break;

      case 'suggestion':
        setSuggestions(prev => [...prev, data]);
        setCurrentTactic(data.tactic);
        break;

      case 'autopilot_audio':
        playAudio(data.audio);
        setStatus(`🤖 Auto-pilot activé: ${data.tactic}`);
        break;

      case 'summary':
        console.log('📊 Session summary:', data);
        setStatus('Simulation terminée');
        break;

      case 'error':
        console.error('Error:', data.message);
        setStatus(`Erreur: ${data.message}`);
        break;

      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const playAudio = (audioBase64) => {
    try {
      const audioBlob = base64ToBlob(audioBase64, 'audio/mpeg');
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
      }
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const base64ToBlob = (base64, type) => {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type });
  };

  const startSimulation = () => {
    setIsActive(true);
    setTranscript([]);
    setSuggestions([]);
    setStatus('Connexion...');
    connectWebSocket();
  };

  const stopSimulation = () => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: 'stop' }));
      wsRef.current.close();
    }
    setIsActive(false);
    setStatus('stopped');
  };

  const sendUserResponse = () => {
    if (!userInput.trim() || !wsRef.current) return;

    // Send user transcript
    wsRef.current.send(JSON.stringify({
      type: 'transcript',
      text: userInput
    }));

    setUserInput('');
  };

  const activateAutoPilot = (tactic) => {
    if (!wsRef.current) return;

    setStatus(`🤖 Activation auto-pilot...`);

    wsRef.current.send(JSON.stringify({
      type: 'autopilot_activate',
      tactic: tactic || currentTactic
    }));
  };

  const getSpeakerLabel = (speaker) => {
    if (speaker === 'user') return '👤 Vous';
    if (speaker === 'user_autopilot') return '🤖 Vous (Auto-Pilot)';
    if (speaker === 'opponent') return '🤝 Client';
    return speaker;
  };

  const getSpeakerClass = (speaker) => {
    if (speaker === 'user' || speaker === 'user_autopilot') return 'user-turn';
    return 'opponent-turn';
  };

  return (
    <div className="voice-simulator" style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '20px'
    }}>
      {/* Header */}
      <div className="simulator-header" style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '24px',
        borderRadius: '12px',
        marginBottom: '24px'
      }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: '28px' }}>
          🎤 Simulation Vocale Temps Réel
        </h1>
        <p style={{ margin: '0', opacity: 0.9, fontSize: '14px' }}>
          Négociez avec une IA et recevez des suggestions tactiques en direct
        </p>
      </div>

      {/* Status Bar */}
      <div className="status-bar" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px',
        background: '#f5f5f5',
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <div className={`indicator ${isActive ? 'live' : ''}`} style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontWeight: 'bold'
        }}>
          <span style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: isActive ? '#4caf50' : '#bbb',
            animation: isActive ? 'pulse 2s infinite' : 'none'
          }}></span>
          {isActive ? '🔴 LIVE' : 'Ready'}
        </div>

        <div style={{ fontSize: '14px', color: '#666' }}>
          {status}
        </div>

        <AutoPilotButton
          active={autoPilotEnabled}
          available={currentTactic !== null}
          onToggle={() => {
            if (currentTactic) {
              setAutoPilotEnabled(!autoPilotEnabled);
              if (!autoPilotEnabled) {
                activateAutoPilot();
              }
            }
          }}
        />
      </div>

      {/* Main Content */}
      <div className="main-content" style={{
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: '20px',
        marginBottom: '20px'
      }}>
        {/* Transcript */}
        <div className="transcript-container" style={{
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '12px',
          padding: '20px',
          height: '500px',
          overflowY: 'auto'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px' }}>💬 Conversation</h3>

          {transcript.length === 0 && !isActive && (
            <div style={{ textAlign: 'center', color: '#999', padding: '40px 20px' }}>
              <p>Cliquez sur "Démarrer" pour commencer la simulation</p>
            </div>
          )}

          {transcript.map((t, i) => (
            <div
              key={i}
              className={`turn ${getSpeakerClass(t.speaker)}`}
              style={{
                marginBottom: '16px',
                padding: '12px',
                borderRadius: '8px',
                background: t.speaker === 'opponent' ? '#f0f0f0' : '#e3f2fd',
                borderLeft: t.speaker === 'opponent' ? '4px solid #ff9800' : '4px solid #2196f3'
              }}
            >
              <div style={{
                fontWeight: 'bold',
                marginBottom: '6px',
                fontSize: '13px',
                color: '#666'
              }}>
                {getSpeakerLabel(t.speaker)}
                {t.tactic && (
                  <span style={{
                    marginLeft: '8px',
                    fontSize: '11px',
                    background: '#764ba2',
                    color: 'white',
                    padding: '2px 8px',
                    borderRadius: '4px'
                  }}>
                    {t.tactic}
                  </span>
                )}
              </div>
              <div style={{ fontSize: '15px', lineHeight: '1.5' }}>
                {t.text}
              </div>
            </div>
          ))}

          <div ref={transcriptEndRef} />
        </div>

        {/* Suggestions Panel */}
        <div className="suggestions-container">
          <h3 style={{ marginTop: 0, marginBottom: '16px' }}>💡 Suggestions Tactiques</h3>
          <SuggestionPanel
            suggestions={suggestions}
            onAutoPilot={activateAutoPilot}
          />

          {suggestions.length > 1 && (
            <details style={{
              marginTop: '16px',
              padding: '12px',
              background: '#f9f9f9',
              borderRadius: '8px',
              fontSize: '13px'
            }}>
              <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                📚 Historique suggestions ({suggestions.length})
              </summary>
              <div style={{ marginTop: '12px', maxHeight: '200px', overflowY: 'auto' }}>
                {suggestions.slice(0, -1).reverse().map((s, i) => (
                  <div key={i} style={{
                    padding: '8px',
                    marginBottom: '8px',
                    background: 'white',
                    borderRadius: '4px',
                    borderLeft: `3px solid ${s.priority === 'critical' ? '#f44336' : '#2196f3'}`
                  }}>
                    {s.suggestion}
                  </div>
                ))}
              </div>
            </details>
          )}
        </div>
      </div>

      {/* User Input */}
      {isActive && (
        <div className="user-input-container" style={{
          background: 'white',
          border: '2px solid #667eea',
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '20px'
        }}>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: 'bold',
            color: '#333'
          }}>
            Votre réponse:
          </label>
          <div style={{ display: 'flex', gap: '12px' }}>
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendUserResponse()}
              placeholder="Tapez votre réponse et appuyez sur Entrée..."
              style={{
                flex: 1,
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                fontSize: '15px'
              }}
            />
            <button
              onClick={sendUserResponse}
              disabled={!userInput.trim()}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: userInput.trim() ? 'pointer' : 'not-allowed',
                fontWeight: 'bold',
                opacity: userInput.trim() ? 1 : 0.5
              }}
            >
              Envoyer
            </button>
          </div>
        </div>
      )}

      {/* Control Buttons */}
      <div style={{ textAlign: 'center' }}>
        <button
          onClick={isActive ? stopSimulation : startSimulation}
          className="control-button"
          style={{
            padding: '16px 48px',
            fontSize: '18px',
            fontWeight: 'bold',
            color: 'white',
            background: isActive
              ? 'linear-gradient(135deg, #f44336 0%, #e91e63 100%)'
              : 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            transition: 'transform 0.2s',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          {isActive ? '⏹️ Arrêter' : '▶️ Démarrer'} la Simulation
        </button>
      </div>

      {/* Hidden audio element */}
      <audio ref={audioRef} style={{ display: 'none' }} />

      {/* CSS Animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .autopilot-toggle {
          padding: 10px 20px;
          border: 2px solid #764ba2;
          background: white;
          border-radius: 8px;
          cursor: pointer;
          font-weight: bold;
          transition: all 0.3s;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .autopilot-toggle:hover:not(.disabled) {
          background: #764ba2;
          color: white;
          transform: scale(1.05);
        }

        .autopilot-toggle.active {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          animation: pulse 2s infinite;
        }

        .autopilot-toggle.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .autopilot-toggle .icon {
          font-size: 20px;
        }
      `}</style>
    </div>
  );
}
