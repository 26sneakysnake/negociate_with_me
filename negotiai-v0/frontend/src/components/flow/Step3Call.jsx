import React, { useState } from 'react';
import axios from 'axios';
import './Step3Call.css';

function Step3Call({ sessionData, updateSessionData, goToStep }) {
  const [phoneNumber, setPhoneNumber] = useState(sessionData.phone_number || '');
  const [loading, setLoading] = useState(false);
  const [callStatus, setCallStatus] = useState(sessionData.call_status || 'idle');

  const handleLaunchCall = async () => {
    if (!phoneNumber) {
      alert('Veuillez entrer votre numéro de téléphone');
      return;
    }

    setLoading(true);
    setCallStatus('launching');

    try {
      const response = await axios.post(
        `http://localhost:8000/api/call/start/${sessionData.session_id}`,
        { phone_number: phoneNumber }
      );

      if (response.data.status === 'initiated') {
        setCallStatus('calling');
        updateSessionData({
          phone_number: phoneNumber,
          call_status: 'calling'
        });

        // Message de confirmation
        setTimeout(() => {
          setCallStatus('in_progress');
          alert('📞 Appel lancé ! Vous allez recevoir l\'appel dans 10-15 secondes. Bonne négociation !');
        }, 1000);
      } else {
        setCallStatus('error');
        alert('Erreur lors du lancement de l\'appel');
      }
    } catch (error) {
      console.error('Call error:', error);
      setCallStatus('error');
      alert('Erreur: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCallEnded = () => {
    setCallStatus('ended');
    updateSessionData({
      call_status: 'ended'
    });
    goToStep(4);
  };

  return (
    <div className="step3-call">
      <div className="step-header">
        <h1>📞 Lancement de l'appel</h1>
        <p>Préparez-vous à négocier avec l'agent IA par téléphone</p>
      </div>

      {callStatus === 'idle' && (
        <div className="call-setup">
          <div className="phone-input-section">
            <label>Votre numéro de téléphone</label>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="+33695990832"
              className="phone-input"
            />
            <p className="input-hint">Format international (ex: +33 pour la France)</p>
          </div>

          <div className="preparation-tips">
            <h3>💡 Conseils avant de commencer</h3>
            <ul>
              <li>Ayez un papier et un stylo pour prendre des notes</li>
              <li>Soyez dans un endroit calme</li>
              <li>Restez ferme sur vos objectifs</li>
              <li>Utilisez les tactiques que vous avez vues</li>
              <li>L'appel durera environ 5-7 minutes</li>
            </ul>
          </div>

          <button
            onClick={handleLaunchCall}
            className="launch-btn"
            disabled={loading || !phoneNumber}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Lancement en cours...
              </>
            ) : (
              <>
                📞 Recevoir l'appel maintenant
              </>
            )}
          </button>
        </div>
      )}

      {(callStatus === 'launching' || callStatus === 'calling') && (
        <div className="call-status-container">
          <div className="call-status-card">
            <div className="pulse-animation">
              <div className="pulse-circle"></div>
              <div className="pulse-circle delay-1"></div>
              <div className="pulse-circle delay-2"></div>
              <span className="phone-icon">📞</span>
            </div>
            <h2>Appel en cours de lancement...</h2>
            <p>Vous allez recevoir l'appel dans quelques secondes</p>
            <p className="phone-number">Appel vers : {phoneNumber}</p>
          </div>
        </div>
      )}

      {callStatus === 'in_progress' && (
        <div className="call-status-container">
          <div className="call-status-card active">
            <div className="pulse-animation">
              <div className="pulse-circle green"></div>
              <div className="pulse-circle green delay-1"></div>
              <div className="pulse-circle green delay-2"></div>
              <span className="phone-icon">📞</span>
            </div>
            <h2>🎙️ Conversation en cours</h2>
            <p>Négociez avec l'agent IA. Utilisez vos tactiques !</p>

            <div className="live-tips">
              <h4>🎯 Rappels pendant la négociation :</h4>
              <div className="tip-tags">
                <span className="tip-tag">⚓ Ancrez bas</span>
                <span className="tip-tag">🤐 Utilisez le silence</span>
                <span className="tip-tag">⏰ Créez l'urgence</span>
                <span className="tip-tag">💰 Restez ferme</span>
              </div>
            </div>

            <button onClick={handleCallEnded} className="end-call-btn">
              Appel terminé - Voir le briefing →
            </button>
          </div>
        </div>
      )}

      {callStatus === 'error' && (
        <div className="call-status-container">
          <div className="call-status-card error">
            <span className="error-icon">❌</span>
            <h2>Erreur lors du lancement</h2>
            <p>Une erreur est survenue. Vérifiez votre numéro et réessayez.</p>
            <button onClick={() => setCallStatus('idle')} className="retry-btn">
              Réessayer
            </button>
          </div>
        </div>
      )}

      <div className="step-actions">
        <button onClick={() => goToStep(2)} className="back-btn">
          ← Retour à la stratégie
        </button>
      </div>
    </div>
  );
}

export default Step3Call;
