import React, { useState } from 'react';
import VoiceSimulator from '../components/VoiceSimulator';

export default function SimulationPage({ onBack }) {
  const [simulationStarted, setSimulationStarted] = useState(false);
  const [scenarioType, setScenarioType] = useState('saas');

  // Demo scenarios
  const scenarios = {
    saas: {
      product: "SaaS B2B Analytics Platform",
      target_price: "50000€/an",
      minimum_price: "35000€/an",
      proposed_price: "45000€/an",
      value_props: [
        "ROI 3x en 6 mois",
        "Support 24/7 dédié",
        "Intégration custom incluse",
        "Formation complète équipe"
      ],
      opponent_goal: "obtenir le meilleur prix possible, idéalement 30K€ maximum",
      opponent_script: [
        "Bonjour, merci de me recevoir. J'ai regardé votre solution et elle m'intéresse, mais franchement 50 000 euros par an, c'est vraiment trop cher pour nous.",
        "J'ai reçu trois autres propositions, et vos concurrents proposent des solutions similaires entre 25 et 35 000 euros. Comment vous justifiez cette différence de prix ?",
        "Écoutez, je dois prendre une décision cette semaine. Mon budget maximum est vraiment 32 000 euros, c'est tout ce que j'ai.",
        "Et puis, votre solution ne propose pas l'intégration native avec Salesforce, alors que c'est crucial pour nous.",
        "Bon, soyons honnêtes. 35 000 euros, c'est absolument mon maximum. Au-delà, c'est hors de question.",
        "D'accord, si j'accepte 38 000 euros, qu'est-ce que vous pouvez m'offrir en plus ? Formation, support ?",
        "OK, 40 000 euros avec la formation premium et 6 mois de support dédié, ça pourrait marcher."
      ]
    },
    freelance: {
      product: "Développement web React/Node.js",
      target_price: "800€/jour",
      minimum_price: "650€/jour",
      proposed_price: "750€/jour",
      value_props: [
        "8 ans d'expérience React",
        "Portfolio startups à succès",
        "Disponible immédiatement"
      ],
      opponent_goal: "payer le moins cher possible",
      opponent_script: [
        "Bonjour, notre budget est de 500 euros par jour maximum.",
        "On a d'autres développeurs à 450-550 euros, pourquoi vous valez plus cher ?",
        "Il faut commencer lundi, vous pouvez faire 550 euros ?",
        "OK, 600 euros c'est vraiment mon max. Vous acceptez ?"
      ]
    },
    real_estate: {
      product: "Appartement 85m² Paris 11ème",
      target_price: "340000€",
      minimum_price: "365000€",
      proposed_price: "355000€",
      value_props: [
        "Achat comptant sans prêt",
        "Signature rapide (3 semaines)",
        "Prise en charge diagnostics"
      ],
      opponent_goal: "vendre au meilleur prix",
      opponent_script: [
        "Le propriétaire demande 380 000 euros pour cet appartement.",
        "340 000, c'est vraiment trop bas. Le marché est tendu ici.",
        "OK, je transmets votre offre. Le vendeur accepte 365 000 euros.",
        "C'est son dernier prix, il ne descendra pas plus bas."
      ]
    }
  };

  const currentScenario = scenarios[scenarioType];

  if (simulationStarted) {
    return <VoiceSimulator context={currentScenario} />;
  }

  return (
    <div style={{
      maxWidth: '900px',
      margin: '0 auto',
      padding: '40px 20px'
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '32px',
        borderRadius: '12px',
        marginBottom: '32px',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: '0 0 12px 0', fontSize: '36px' }}>
          🎤 Simulation Vocale Temps Réel
        </h1>
        <p style={{ margin: '0', fontSize: '16px', opacity: 0.9 }}>
          Entraînez-vous à négocier avec une IA et recevez des suggestions tactiques instantanées
        </p>
      </div>

      {/* Scenario Selection */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{ marginTop: 0 }}>📋 Choisissez votre scénario</h2>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '16px',
          marginBottom: '20px'
        }}>
          <button
            onClick={() => setScenarioType('saas')}
            style={{
              padding: '20px',
              border: scenarioType === 'saas' ? '3px solid #667eea' : '2px solid #ddd',
              borderRadius: '12px',
              background: scenarioType === 'saas' ? '#f0f4ff' : 'white',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.3s'
            }}
          >
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>💼</div>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>SaaS B2B</div>
            <div style={{ fontSize: '13px', color: '#666' }}>
              Vendez une plateforme analytics à 50K€/an
            </div>
          </button>

          <button
            onClick={() => setScenarioType('freelance')}
            style={{
              padding: '20px',
              border: scenarioType === 'freelance' ? '3px solid #667eea' : '2px solid #ddd',
              borderRadius: '12px',
              background: scenarioType === 'freelance' ? '#f0f4ff' : 'white',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.3s'
            }}
          >
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>💻</div>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Freelance Dev</div>
            <div style={{ fontSize: '13px', color: '#666' }}>
              Négociez votre TJM (800€/jour)
            </div>
          </button>

          <button
            onClick={() => setScenarioType('real_estate')}
            style={{
              padding: '20px',
              border: scenarioType === 'real_estate' ? '3px solid #667eea' : '2px solid #ddd',
              borderRadius: '12px',
              background: scenarioType === 'real_estate' ? '#f0f4ff' : 'white',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.3s'
            }}
          >
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>🏠</div>
            <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Immobilier</div>
            <div style={{ fontSize: '13px', color: '#666' }}>
              Achetez un appartement à Paris
            </div>
          </button>
        </div>

        {/* Scenario Details */}
        <div style={{
          background: '#f9f9f9',
          padding: '20px',
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '12px' }}>
            Détails du scénario: {currentScenario.product}
          </h3>

          <div style={{ marginBottom: '12px' }}>
            <strong>🎯 Prix cible:</strong> {currentScenario.target_price}
          </div>

          <div style={{ marginBottom: '12px' }}>
            <strong>🔻 Prix minimum:</strong> {currentScenario.minimum_price}
          </div>

          <div style={{ marginBottom: '12px' }}>
            <strong>💎 Propositions de valeur:</strong>
            <ul style={{ marginTop: '8px', marginBottom: 0 }}>
              {currentScenario.value_props.map((prop, i) => (
                <li key={i}>{prop}</li>
              ))}
            </ul>
          </div>

          <div style={{
            marginTop: '16px',
            padding: '12px',
            background: '#fff3cd',
            border: '1px solid #ffc107',
            borderRadius: '6px',
            fontSize: '14px'
          }}>
            ⚡ <strong>Nombre de tours:</strong> {currentScenario.opponent_script.length} interventions du client
          </div>
        </div>
      </div>

      {/* How it Works */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{ marginTop: 0 }}>🔧 Comment ça marche ?</h2>

        <div style={{ display: 'grid', gap: '16px' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{
              fontSize: '24px',
              width: '40px',
              height: '40px',
              background: '#e3f2fd',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              1️⃣
            </div>
            <div>
              <strong>Le client IA parle en premier</strong>
              <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '14px' }}>
                L'IA joue un client difficile avec des tactiques de négociation réalistes
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{
              fontSize: '24px',
              width: '40px',
              height: '40px',
              background: '#fff3e0',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              2️⃣
            </div>
            <div>
              <strong>Recevez des suggestions tactiques instantanées</strong>
              <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '14px' }}>
                L'IA détecte les patterns (lowball, urgence...) et suggère des contre-tactiques
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{
              fontSize: '24px',
              width: '40px',
              height: '40px',
              background: '#f3e5f5',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              3️⃣
            </div>
            <div>
              <strong>Tapez votre réponse OU activez l'auto-pilot</strong>
              <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '14px' }}>
                Mode auto-pilot : l'IA répond à votre place avec la tactique recommandée
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <div style={{
              fontSize: '24px',
              width: '40px',
              height: '40px',
              background: '#e8f5e9',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              4️⃣
            </div>
            <div>
              <strong>Apprenez de chaque tour</strong>
              <p style={{ margin: '4px 0 0 0', color: '#666', fontSize: '14px' }}>
                Voyez quelles tactiques fonctionnent et améliorez vos compétences
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Start Button */}
      <div style={{ textAlign: 'center' }}>
        <button
          onClick={() => setSimulationStarted(true)}
          style={{
            padding: '20px 60px',
            fontSize: '20px',
            fontWeight: 'bold',
            color: 'white',
            background: 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            transition: 'transform 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          ▶️ Démarrer la Simulation
        </button>

        <div style={{ marginTop: '20px' }}>
          <button
            onClick={() => onBack && onBack()}
            style={{
              background: 'none',
              border: 'none',
              color: '#667eea',
              cursor: 'pointer',
              fontSize: '14px',
              textDecoration: 'underline'
            }}
          >
            ← Retour au mode classique
          </button>
        </div>
      </div>
    </div>
  );
}
