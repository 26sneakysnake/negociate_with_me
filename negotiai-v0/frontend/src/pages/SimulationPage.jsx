import React, { useState } from 'react';
import VoiceSimulator from '../components/VoiceSimulator';
import ElevenLabsVoiceChat from '../components/ElevenLabsVoiceChat';

export default function SimulationPage({ onBack }) {
  const [currentStep, setCurrentStep] = useState('setup'); // setup, research, simulation
  const [scenarioType, setScenarioType] = useState('saas');
  const [simulationMode, setSimulationMode] = useState('text'); // 'voice' or 'text' - default to text for stability

  // Research fields
  const [productName, setProductName] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [researchData, setResearchData] = useState(null);
  const [isResearching, setIsResearching] = useState(false);
  const [researchError, setResearchError] = useState(null);

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

  // Helper function to safely render values (handle objects from Mistral AI)
  const renderValue = (value) => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'object' && !Array.isArray(value)) {
      // If it's an object, try to extract meaningful info or stringify it
      if (value.range && value.basis) {
        return `${value.range} (${value.basis})`;
      }
      return JSON.stringify(value);
    }
    return value;
  };

  // Handle research
  const handleResearch = async () => {
    if (!productName.trim()) {
      setResearchError('Le nom du produit est requis');
      return;
    }

    setIsResearching(true);
    setResearchError(null);

    try {
      const response = await fetch('http://localhost:8000/api/simulation/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: productName,
          company_name: companyName || null,
          industry: industry || null
        })
      });

      if (!response.ok) {
        throw new Error(`Research failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResearchData(data);
      setCurrentStep('research');
    } catch (error) {
      console.error('Research error:', error);
      setResearchError(error.message || 'Erreur lors de la recherche');
    } finally {
      setIsResearching(false);
    }
  };

  // Handle start simulation with research data
  const handleStartSimulation = () => {
    setCurrentStep('simulation');
  };

  if (currentStep === 'simulation') {
    // Pass research data to simulator
    const enrichedContext = {
      ...currentScenario,
      research_data: researchData,
      product: productName || currentScenario.product
    };

    // Use ElevenLabs voice chat for voice mode, text simulator for text mode
    if (simulationMode === 'voice') {
      return <ElevenLabsVoiceChat context={enrichedContext} onClose={() => setCurrentStep('setup')} />;
    } else {
      return <VoiceSimulator context={enrichedContext} />;
    }
  }

  if (currentStep === 'research') {
    // Display research results
    return (
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '40px 20px'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
          color: 'white',
          padding: '32px',
          borderRadius: '12px',
          marginBottom: '32px',
          textAlign: 'center'
        }}>
          <h1 style={{ margin: '0 0 12px 0', fontSize: '36px' }}>
            ✅ Recherche Terminée
          </h1>
          <p style={{ margin: '0', fontSize: '16px', opacity: 0.9 }}>
            Voici les informations collectées par Mistral AI
          </p>
        </div>

        {/* Research Results */}
        <div style={{
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px'
        }}>
          <h2 style={{ marginTop: 0 }}>📦 Produit: {researchData.product.name}</h2>

          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>💎 Caractéristiques clés</h3>
            <ul style={{ margin: 0 }}>
              {researchData.product.features.map((feature, i) => (
                <li key={i}>{feature}</li>
              ))}
            </ul>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>💰 Prix marché typique</h3>
            <p style={{ margin: 0, color: '#666' }}>{renderValue(researchData.product.typical_pricing)}</p>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>🏆 Concurrents principaux</h3>
            <p style={{ margin: 0, color: '#666' }}>
              {Array.isArray(researchData.product.competitors)
                ? researchData.product.competitors.join(', ')
                : renderValue(researchData.product.competitors)}
            </p>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>📊 Position marché</h3>
            <p style={{ margin: 0, color: '#666' }}>{renderValue(researchData.product.market_position)}</p>
          </div>

          <div>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>⭐ Bénéfices principaux</h3>
            <ul style={{ margin: 0 }}>
              {researchData.product.key_benefits.map((benefit, i) => (
                <li key={i}>{benefit}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Client Info if available */}
        {researchData.client && (
          <div style={{
            background: 'white',
            border: '1px solid #ddd',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '24px'
          }}>
            <h2 style={{ marginTop: 0 }}>🏢 Client: {renderValue(researchData.client.name)}</h2>

            <div style={{ marginBottom: '12px' }}>
              <strong>Taille:</strong> {renderValue(researchData.client.company_size)}
            </div>

            <div style={{ marginBottom: '12px' }}>
              <strong>Secteur:</strong> {renderValue(researchData.client.industry)}
            </div>

            <div style={{ marginBottom: '12px' }}>
              <strong>Budget estimé:</strong> {renderValue(researchData.client.budget_range)}
            </div>

            <div style={{ marginBottom: '12px' }}>
              <strong>Points de douleur:</strong>
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                {researchData.client.pain_points.map((point, i) => (
                  <li key={i}>{point}</li>
                ))}
              </ul>
            </div>

            <div>
              <strong>Facteurs de décision:</strong>
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                {researchData.client.decision_factors.map((factor, i) => (
                  <li key={i}>{factor}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Simulation Mode Selection */}
        <div style={{
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px' }}>🎯 Choisissez le mode de simulation</h3>

          {/* Warning about voice mode */}
          <div style={{
            background: '#fff3cd',
            border: '1px solid #ffc107',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '16px',
            fontSize: '14px'
          }}>
            ⚠️ <strong>Note:</strong> Le mode Voice-to-Voice nécessite l'API ElevenLabs Conversational AI qui pourrait ne pas être disponible.
            Le <strong>mode Texte</strong> est recommandé pour une expérience stable.
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <button
              onClick={() => setSimulationMode('voice')}
              style={{
                padding: '20px',
                border: simulationMode === 'voice' ? '3px solid #667eea' : '2px solid #ddd',
                borderRadius: '12px',
                background: simulationMode === 'voice' ? '#f0f4ff' : 'white',
                cursor: 'pointer',
                textAlign: 'left',
                opacity: 0.7
              }}
            >
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>🎤</div>
              <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Voice-to-Voice (Beta)</div>
              <div style={{ fontSize: '13px', color: '#666' }}>
                Conversation vocale en temps réel - Peut nécessiter configuration
              </div>
            </button>

            <button
              onClick={() => setSimulationMode('text')}
              style={{
                padding: '20px',
                border: simulationMode === 'text' ? '3px solid #667eea' : '2px solid #ddd',
                borderRadius: '12px',
                background: simulationMode === 'text' ? '#f0f4ff' : 'white',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>⌨️</div>
              <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Texte (Demo)</div>
              <div style={{ fontSize: '13px', color: '#666' }}>
                Simulation textuelle avec suggestions tactiques
              </div>
            </button>
          </div>
        </div>

        {/* Start Simulation Buttons */}
        <div style={{ textAlign: 'center' }}>
          <button
            onClick={handleStartSimulation}
            style={{
              padding: '20px 60px',
              fontSize: '20px',
              fontWeight: 'bold',
              color: 'white',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              borderRadius: '12px',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              transition: 'transform 0.2s',
              marginRight: '12px'
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            {simulationMode === 'voice' ? '🎤 Démarrer la Conversation Vocale' : '⌨️ Démarrer en Mode Texte'}
          </button>

          <button
            onClick={() => {
              setCurrentStep('setup');
              setResearchData(null);
            }}
            style={{
              background: 'none',
              border: '1px solid #667eea',
              color: '#667eea',
              padding: '20px 40px',
              borderRadius: '12px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            ← Refaire la recherche
          </button>
        </div>
      </div>
    );
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

      {/* Research Form */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{ marginTop: 0 }}>🔍 Recherche Pré-Négociation (Mistral AI)</h2>
        <p style={{ color: '#666', marginBottom: '20px' }}>
          Mistral AI va rechercher des informations sur votre produit et votre client pour enrichir la simulation.
        </p>

        <div style={{ display: 'grid', gap: '16px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Nom du produit/solution <span style={{ color: 'red' }}>*</span>
            </label>
            <input
              type="text"
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="Ex: Plateforme SaaS Analytics, Développement web React..."
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Nom de l'entreprise cliente (optionnel)
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Ex: Acme Corp, TechStartup Inc..."
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
              Secteur d'activité (optionnel)
            </label>
            <input
              type="text"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              placeholder="Ex: E-commerce, Finance, Santé..."
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '8px',
                fontSize: '14px'
              }}
            />
          </div>
        </div>

        {researchError && (
          <div style={{
            background: '#fee',
            border: '1px solid #f88',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '16px',
            color: '#c00'
          }}>
            ❌ {researchError}
          </div>
        )}

        <button
          onClick={handleResearch}
          disabled={isResearching || !productName.trim()}
          style={{
            padding: '16px 32px',
            fontSize: '16px',
            fontWeight: 'bold',
            color: 'white',
            background: isResearching || !productName.trim()
              ? '#ccc'
              : 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
            border: 'none',
            borderRadius: '8px',
            cursor: isResearching || !productName.trim() ? 'not-allowed' : 'pointer',
            width: '100%'
          }}
        >
          {isResearching ? '🔍 Recherche en cours...' : '🚀 Lancer la recherche'}
        </button>

        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: '#e3f2fd',
          border: '1px solid #2196f3',
          borderRadius: '8px',
          fontSize: '14px'
        }}>
          💡 <strong>Astuce:</strong> Plus vous donnez d'informations (entreprise, secteur),
          plus l'agent IA sera réaliste et adapté à votre contexte.
        </div>
      </div>

      {/* Quick Demo (Option to skip research) */}
      <div style={{
        background: 'white',
        border: '1px solid #ddd',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h2 style={{ marginTop: 0 }}>⚡ OU: Scénarios Demo Rapide (sans recherche)</h2>

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

      {/* Start Button - Demo without research */}
      <div style={{ textAlign: 'center' }}>
        <button
          onClick={() => setCurrentStep('simulation')}
          style={{
            padding: '20px 60px',
            fontSize: '20px',
            fontWeight: 'bold',
            color: 'white',
            background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            transition: 'transform 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
          ▶️ Démarrer Sans Recherche (Demo)
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
