import React from 'react';

export default function AutoPilotButton({ active, onToggle, available }) {
  return (
    <button
      onClick={onToggle}
      disabled={!available}
      className={`autopilot-toggle ${active ? 'active' : ''} ${!available ? 'disabled' : ''}`}
      title={available ? "Activer l'auto-pilot pour répondre automatiquement" : "Auto-pilot non disponible pour le moment"}
    >
      <span className="icon">{active ? '🤖✨' : '🤖'}</span>
      <span className="label">
        Auto-Pilot {active ? 'ON' : 'OFF'}
      </span>
      {!available && <span className="badge">⏳</span>}
    </button>
  );
}
