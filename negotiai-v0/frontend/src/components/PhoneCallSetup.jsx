import React, { useState, useEffect } from 'react';

/**
 * Phone Call Setup Component
 * Manages real phone calls with AI negotiation opponent
 */
export default function PhoneCallSetup({ context, scenario, onComplete }) {
  const [phone, setPhone] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, setup, ready, calling, completed, error
  const [error, setError] = useState(null);
  const [callMessage, setCallMessage] = useState('');

  // Setup call session when component mounts
  useEffect(() => {
    setupCallSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setupCallSession = async () => {
    try {
      setStatus('setup');

      const response = await fetch('http://localhost:8000/api/call/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario,
          context
        })
      });

      if (!response.ok) {
        throw new Error(`Setup failed: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Call session created:', data);

      setSessionId(data.session_id);
      setStatus('ready');

    } catch (err) {
      console.error('❌ Setup error:', err);
      setError(err.message);
      setStatus('error');
    }
  };

  const startCall = async () => {
    if (!phone) {
      setError('Veuillez entrer votre numéro de téléphone');
      return;
    }

    try {
      setStatus('calling');
      setError(null);
      setCallMessage('Appel en cours...');

      const response = await fetch(`http://localhost:8000/api/call/start/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phone
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to start call: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('📞 Call response:', data);

      if (data.status === 'initiated') {
        setCallMessage(data.message || 'Vous allez recevoir l\'appel dans 10 secondes...');

        // Start polling for results
        pollForResults();

      } else if (data.status === 'unavailable') {
        // Phone API not available
        setError(data.message || 'L\'API d\'appel téléphonique n\'est pas encore disponible');
        setCallMessage(data.suggestion || 'Utilisez le mode TEXTE pour le moment');
        setStatus('error');

        // Show alternatives
        if (data.alternatives) {
          console.log('💡 Alternatives:', data.alternatives);
        }
      }

    } catch (err) {
      console.error('❌ Call error:', err);
      setError(err.message);
      setStatus('error');
    }
  };

  const pollForResults = () => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/call/results/${sessionId}`);
        const data = await response.json();

        if (data.status === 'completed') {
          clearInterval(interval);
          setStatus('completed');

          if (onComplete) {
            onComplete(data);
          }
        } else if (data.status === 'in_progress') {
          setCallMessage('Appel en cours... Raccrochez quand vous avez terminé.');
        }
      } catch (err) {
        console.error('Error polling results:', err);
      }
    }, 5000); // Poll every 5 seconds

    // Stop polling after 10 minutes max
    setTimeout(() => {
      clearInterval(interval);
      if (status === 'calling') {
        setError('L\'appel a dépassé le temps maximum');
        setStatus('error');
      }
    }, 600000);
  };

  return (
    <div style={{
      maxWidth: '600px',
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
          📞 Négociation par Téléphone
        </h1>
        <p style={{ margin: 0, opacity: 0.9 }}>
          Recevez un vrai appel pour pratiquer la négociation
        </p>
      </div>

      {/* Status Display */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '20px'
      }}>
        {status === 'setup' && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '48px', marginBottom: '12px' }}>⏳</div>
            <p>Préparation de l'appel...</p>
          </div>
        )}

        {status === 'ready' && (
          <div>
            <h3 style={{ marginTop: 0 }}>Prêt à commencer !</h3>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 'bold'
              }}>
                Votre numéro de téléphone :
              </label>
              <input
                type="tel"
                placeholder="+33 6 12 34 56 78"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '16px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  boxSizing: 'border-box'
                }}
              />
              <p style={{
                fontSize: '12px',
                color: '#666',
                marginTop: '8px'
              }}>
                Format international recommandé (ex: +33612345678)
              </p>
            </div>

            <button
              onClick={startCall}
              disabled={!phone}
              style={{
                width: '100%',
                padding: '16px',
                fontSize: '18px',
                fontWeight: 'bold',
                color: 'white',
                background: phone ? 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)' : '#ccc',
                border: 'none',
                borderRadius: '8px',
                cursor: phone ? 'pointer' : 'not-allowed'
              }}
            >
              📞 Recevoir l'appel
            </button>

            <div style={{
              marginTop: '16px',
              padding: '12px',
              background: '#fff3cd',
              border: '1px solid #ffc107',
              borderRadius: '8px',
              fontSize: '14px'
            }}>
              <strong>💡 Comment ça marche :</strong>
              <ul style={{ marginBottom: 0, marginTop: '8px', paddingLeft: '20px' }}>
                <li>Vous recevrez l'appel dans ~10 secondes</li>
                <li>L'IA opponent commencera la négociation</li>
                <li>Négociez comme dans une vraie situation</li>
                <li>Raccrochez quand vous avez terminé</li>
                <li>Recevez votre analyse de performance</li>
              </ul>
            </div>
          </div>
        )}

        {status === 'calling' && (
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: '64px',
              animation: 'pulse 1.5s ease-in-out infinite',
              marginBottom: '16px'
            }}>
              📞
            </div>
            <h3>{callMessage}</h3>
            <p style={{ color: '#666', fontSize: '14px' }}>
              Raccrochez quand vous avez terminé la négociation
            </p>

            <div style={{
              marginTop: '20px',
              padding: '12px',
              background: '#e3f2fd',
              borderRadius: '8px'
            }}>
              <strong>🎯 Pendant l'appel :</strong>
              <ul style={{ marginBottom: 0, marginTop: '8px', paddingLeft: '20px', textAlign: 'left' }}>
                <li>Restez professionnel</li>
                <li>Écoutez attentivement les tactiques</li>
                <li>Défendez votre position</li>
                <li>Cherchez un accord gagnant-gagnant</li>
              </ul>
            </div>
          </div>
        )}

        {status === 'completed' && (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '64px', marginBottom: '12px' }}>✅</div>
            <h3>Appel terminé !</h3>
            <p>Analyse en cours de votre performance...</p>
          </div>
        )}

        {status === 'error' && error && (
          <div>
            <div style={{ textAlign: 'center', marginBottom: '16px' }}>
              <div style={{ fontSize: '64px', marginBottom: '12px' }}>❌</div>
              <h3>Une erreur est survenue</h3>
            </div>

            <div style={{
              background: '#fee',
              border: '1px solid #f88',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '16px',
              color: '#c00'
            }}>
              {error}
            </div>

            {callMessage && (
              <div style={{
                background: '#fff3cd',
                border: '1px solid #ffc107',
                borderRadius: '8px',
                padding: '12px',
                marginBottom: '16px'
              }}>
                <strong>💡 Solution :</strong> {callMessage}
              </div>
            )}

            <button
              onClick={setupCallSession}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                color: 'white',
                background: '#2196f3',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              🔄 Réessayer
            </button>
          </div>
        )}
      </div>

      {/* Scenario Info */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '16px',
        fontSize: '14px'
      }}>
        <h4 style={{ marginTop: 0 }}>📋 Contexte de la négociation</h4>
        <div style={{ marginBottom: '8px' }}>
          <strong>Produit/Service :</strong> {context.product || 'Non spécifié'}
        </div>
        <div style={{ marginBottom: '8px' }}>
          <strong>Prix cible :</strong> {context.target_price || 'Non spécifié'}
        </div>
        <div style={{ marginBottom: '8px' }}>
          <strong>Prix minimum :</strong> {context.minimum_price || 'Non spécifié'}
        </div>
        {context.red_lines && context.red_lines.length > 0 && (
          <div>
            <strong>Red lines :</strong>
            <ul style={{ marginTop: '4px', marginBottom: 0, paddingLeft: '20px' }}>
              {context.red_lines.map((line, i) => (
                <li key={i}>{line}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            opacity: 1;
          }
          50% {
            transform: scale(1.1);
            opacity: 0.8;
          }
        }
      `}</style>
    </div>
  );
}
