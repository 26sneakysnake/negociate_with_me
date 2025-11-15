import React, { useState, useEffect, useRef } from 'react';

/**
 * ElevenLabs Voice Chat Component
 * Handles direct WebSocket connection to ElevenLabs Conversational AI
 * for bidirectional voice conversation
 */
export default function ElevenLabsVoiceChat({ context, onClose }) {
  const [status, setStatus] = useState('initializing'); // initializing, ready, connecting, connected, speaking, listening, error
  const [agentId, setAgentId] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [error, setError] = useState(null);
  const [isMuted, setIsMuted] = useState(false);

  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const audioQueueRef = useRef([]);
  const isPlayingRef = useRef(false);

  // Initialize agent and setup
  useEffect(() => {
    const setupAgent = async () => {
      try {
        setStatus('initializing');

        // Create ElevenLabs Conversational AI agent
        const response = await fetch('http://localhost:8000/api/simulation/setup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(context)
        });

        if (!response.ok) {
          throw new Error(`Failed to setup agent: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('✅ Agent created:', data);

        setAgentId(data.agent_id);
        setStatus('ready');

      } catch (err) {
        console.error('❌ Setup error:', err);
        setError(err.message);
        setStatus('error');
      }
    };

    setupAgent();
    return () => {
      cleanup();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const startConversation = async () => {
    try {
      setStatus('connecting');

      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      mediaStreamRef.current = stream;

      // Initialize audio context
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000
      });

      // Connect to ElevenLabs WebSocket
      const wsUrl = `wss://api.elevenlabs.io/v1/convai/conversation?agent_id=${agentId}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('✅ Connected to ElevenLabs');
        setStatus('connected');

        // Start sending audio
        startAudioStreaming(stream);
      };

      wsRef.current.onmessage = async (event) => {
        try {
          const message = JSON.parse(event.data);
          handleElevenLabsMessage(message);
        } catch (err) {
          // Binary audio data
          if (event.data instanceof Blob) {
            await handleAudioChunk(event.data);
          }
        }
      };

      wsRef.current.onerror = (err) => {
        console.error('❌ WebSocket error:', err);
        setError('Connection error with ElevenLabs');
        setStatus('error');
      };

      wsRef.current.onclose = () => {
        console.log('🔌 Disconnected from ElevenLabs');
        setStatus('ready');
      };

    } catch (err) {
      console.error('❌ Error starting conversation:', err);
      setError(err.message);
      setStatus('error');
    }
  };

  const startAudioStreaming = (stream) => {
    const audioContext = audioContextRef.current;
    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(4096, 1, 1);

    source.connect(processor);
    processor.connect(audioContext.destination);

    processor.onaudioprocess = (e) => {
      if (wsRef.current?.readyState === WebSocket.OPEN && !isMuted) {
        const inputData = e.inputBuffer.getChannelData(0);

        // Convert float32 to int16 PCM
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        // Send to ElevenLabs
        wsRef.current.send(pcmData.buffer);
      }
    };
  };

  const handleElevenLabsMessage = (message) => {
    console.log('📨 Message from ElevenLabs:', message);

    switch (message.type) {
      case 'conversation_initiation_metadata':
        console.log('✅ Conversation initiated');
        addTranscript('system', 'Conversation démarrée. Vous pouvez parler...');
        break;

      case 'agent_response':
        // Agent is speaking
        setStatus('speaking');
        if (message.transcript) {
          addTranscript('agent', message.transcript);
        }
        break;

      case 'user_transcript':
        // User speech recognized
        setStatus('listening');
        if (message.transcript) {
          addTranscript('user', message.transcript);
        }
        break;

      case 'interruption':
        console.log('🔇 Agent interrupted');
        setStatus('listening');
        break;

      case 'ping':
        // Send pong
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'pong' }));
        }
        break;

      default:
        console.log('🔔 Unknown message type:', message.type);
    }
  };

  const handleAudioChunk = async (audioBlob) => {
    // Queue audio chunk for playback
    audioQueueRef.current.push(audioBlob);

    if (!isPlayingRef.current) {
      playNextAudioChunk();
    }
  };

  const playNextAudioChunk = async () => {
    if (audioQueueRef.current.length === 0) {
      isPlayingRef.current = false;
      setStatus('listening');
      return;
    }

    isPlayingRef.current = true;
    setStatus('speaking');

    const audioBlob = audioQueueRef.current.shift();
    const arrayBuffer = await audioBlob.arrayBuffer();

    const audioContext = audioContextRef.current;
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);

    source.onended = () => {
      playNextAudioChunk();
    };

    source.start(0);
  };

  const addTranscript = (speaker, text) => {
    setTranscript(prev => [...prev, {
      speaker,
      text,
      timestamp: new Date().toISOString()
    }]);
  };

  const toggleMute = () => {
    setIsMuted(prev => !prev);
  };

  const endConversation = () => {
    cleanup();
    if (onClose) onClose();
  };

  const cleanup = () => {
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Stop media stream
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Clear audio queue
    audioQueueRef.current = [];
    isPlayingRef.current = false;
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
          🎤 Conversation Vocale en Direct
        </h1>
        <p style={{ margin: 0, opacity: 0.9 }}>
          {context.product}
        </p>
      </div>

      {/* Status Display */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '20px',
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '48px',
          marginBottom: '12px'
        }}>
          {status === 'initializing' && '⏳'}
          {status === 'ready' && '▶️'}
          {status === 'connecting' && '🔌'}
          {status === 'connected' && '✅'}
          {status === 'speaking' && '🗣️'}
          {status === 'listening' && '👂'}
          {status === 'error' && '❌'}
        </div>

        <div style={{
          fontSize: '18px',
          fontWeight: 'bold',
          marginBottom: '8px'
        }}>
          {status === 'initializing' && 'Création de l\'agent IA...'}
          {status === 'ready' && 'Prêt à démarrer'}
          {status === 'connecting' && 'Connexion en cours...'}
          {status === 'connected' && 'Connecté - Parlez !'}
          {status === 'speaking' && 'L\'agent parle...'}
          {status === 'listening' && 'À votre tour...'}
          {status === 'error' && 'Erreur'}
        </div>

        {error && (
          <div style={{
            background: '#fee',
            border: '1px solid #f88',
            borderRadius: '8px',
            padding: '12px',
            marginTop: '12px',
            color: '#c00'
          }}>
            {error}
          </div>
        )}

        {/* Control Buttons */}
        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'center',
          marginTop: '20px'
        }}>
          {status === 'ready' && (
            <button
              onClick={startConversation}
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
              🎤 Démarrer la Conversation
            </button>
          )}

          {(status === 'connected' || status === 'listening' || status === 'speaking') && (
            <>
              <button
                onClick={toggleMute}
                style={{
                  padding: '16px 32px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: 'white',
                  background: isMuted ? '#f44336' : '#2196f3',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
              >
                {isMuted ? '🔇 Réactiver micro' : '🎤 Couper micro'}
              </button>

              <button
                onClick={endConversation}
                style={{
                  padding: '16px 32px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: 'white',
                  background: '#f44336',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
              >
                ⏹️ Terminer
              </button>
            </>
          )}
        </div>
      </div>

      {/* Transcript */}
      {transcript.length > 0 && (
        <div style={{
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '12px',
          padding: '20px',
          maxHeight: '400px',
          overflowY: 'auto'
        }}>
          <h3 style={{ marginTop: 0 }}>📝 Transcription</h3>

          {transcript.map((entry, i) => (
            <div
              key={i}
              style={{
                marginBottom: '16px',
                padding: '12px',
                background: entry.speaker === 'user' ? '#e3f2fd' : entry.speaker === 'agent' ? '#f3e5f5' : '#f5f5f5',
                borderRadius: '8px',
                borderLeft: `4px solid ${entry.speaker === 'user' ? '#2196f3' : entry.speaker === 'agent' ? '#9c27b0' : '#999'}`
              }}
            >
              <div style={{
                fontWeight: 'bold',
                marginBottom: '4px',
                fontSize: '14px'
              }}>
                {entry.speaker === 'user' && '👤 Vous'}
                {entry.speaker === 'agent' && '🤝 Client IA'}
                {entry.speaker === 'system' && '⚙️ Système'}
              </div>
              <div style={{ fontSize: '15px' }}>
                {entry.text}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div style={{
        marginTop: '20px',
        padding: '16px',
        background: '#fff3cd',
        border: '1px solid #ffc107',
        borderRadius: '8px',
        fontSize: '14px'
      }}>
        <strong>💡 Comment ça marche:</strong>
        <ul style={{ marginBottom: 0, marginTop: '8px' }}>
          <li>Cliquez sur "Démarrer la Conversation" et autorisez l'accès au microphone</li>
          <li>Parlez naturellement - l'IA vous entend et répond en temps réel</li>
          <li>L'IA utilise les informations de recherche pour adapter ses réponses</li>
          <li>Vous pouvez couper le micro temporairement si besoin</li>
        </ul>
      </div>
    </div>
  );
}
