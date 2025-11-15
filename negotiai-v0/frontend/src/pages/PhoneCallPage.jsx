import React, { useState, useEffect } from 'react';
import PhoneCallSetup from '../components/PhoneCallSetup';
import CallResults from '../components/CallResults';

/**
 * Phone Call Page
 * Complete flow for phone-based negotiation training
 */
export default function PhoneCallPage() {
  const [currentStep, setCurrentStep] = useState('scenario'); // scenario, context, call, results
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [scenarios, setScenarios] = useState({});
  const [context, setContext] = useState({
    product: '',
    target_price: '',
    minimum_price: '',
    red_lines: []
  });
  const [redLineInput, setRedLineInput] = useState('');
  const [callResults, setCallResults] = useState(null);

  // Load available scenarios
  useEffect(() => {
    fetch('http://localhost:8000/api/call/scenarios')
      .then(res => res.json())
      .then(data => {
        setScenarios(data);
        console.log('✅ Scenarios loaded:', data);
      })
      .catch(err => console.error('❌ Error loading scenarios:', err));
  }, []);

  const handleAddRedLine = () => {
    if (redLineInput.trim()) {
      setContext({
        ...context,
        red_lines: [...context.red_lines, redLineInput.trim()]
      });
      setRedLineInput('');
    }
  };

  const handleRemoveRedLine = (index) => {
    setContext({
      ...context,
      red_lines: context.red_lines.filter((_, i) => i !== index)
    });
  };

  const handleCallComplete = (results) => {
    setCallResults(results);
    setCurrentStep('results');
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      {/* Scenario Selection */}
      {currentStep === 'scenario' && (
        <div style={{
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '32px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
          }}>
            <h1 style={{
              marginTop: 0,
              marginBottom: '24px',
              fontSize: '32px',
              textAlign: 'center'
            }}>
              📞 Entraînement Négociation par Téléphone
            </h1>

            <p style={{
              textAlign: 'center',
              color: '#666',
              marginBottom: '32px'
            }}>
              Choisissez un scénario de négociation pour commencer
            </p>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '16px',
              marginBottom: '24px'
            }}>
              {Object.entries(scenarios).map(([key, scenario]) => (
                <div
                  key={key}
                  onClick={() => setSelectedScenario(key)}
                  style={{
                    background: selectedScenario === key ? '#e3f2fd' : '#f5f5f5',
                    border: `2px solid ${selectedScenario === key ? '#2196f3' : 'transparent'}`,
                    borderRadius: '12px',
                    padding: '20px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedScenario !== key) {
                      e.currentTarget.style.background = '#fafafa';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedScenario !== key) {
                      e.currentTarget.style.background = '#f5f5f5';
                    }
                  }}
                >
                  <h3 style={{ marginTop: 0, marginBottom: '12px' }}>
                    {scenario.name}
                  </h3>
                  <p style={{
                    fontSize: '14px',
                    color: '#666',
                    margin: 0,
                    lineHeight: '1.5'
                  }}>
                    {scenario.description}
                  </p>
                </div>
              ))}
            </div>

            <button
              onClick={() => setCurrentStep('context')}
              disabled={!selectedScenario}
              style={{
                width: '100%',
                padding: '16px',
                fontSize: '18px',
                fontWeight: 'bold',
                color: 'white',
                background: selectedScenario ? 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)' : '#ccc',
                border: 'none',
                borderRadius: '8px',
                cursor: selectedScenario ? 'pointer' : 'not-allowed'
              }}
            >
              Continuer →
            </button>
          </div>
        </div>
      )}

      {/* Context Setup */}
      {currentStep === 'context' && (
        <div style={{
          maxWidth: '700px',
          margin: '0 auto'
        }}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '32px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
          }}>
            <h2 style={{ marginTop: 0, marginBottom: '24px' }}>
              📋 Contexte de Négociation
            </h2>

            <p style={{ color: '#666', marginBottom: '24px' }}>
              Scénario sélectionné : <strong>{scenarios[selectedScenario]?.name}</strong>
            </p>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 'bold'
              }}>
                Produit/Service à négocier :
              </label>
              <input
                type="text"
                value={context.product}
                onChange={(e) => setContext({ ...context, product: e.target.value })}
                placeholder="Ex: Plateforme SaaS Analytics"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '16px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 'bold'
              }}>
                Prix cible :
              </label>
              <input
                type="text"
                value={context.target_price}
                onChange={(e) => setContext({ ...context, target_price: e.target.value })}
                placeholder="Ex: 50000€/an"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '16px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 'bold'
              }}>
                Prix minimum acceptable :
              </label>
              <input
                type="text"
                value={context.minimum_price}
                onChange={(e) => setContext({ ...context, minimum_price: e.target.value })}
                placeholder="Ex: 35000€/an"
                style={{
                  width: '100%',
                  padding: '12px',
                  fontSize: '16px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: 'bold'
              }}>
                Red lines (points non-négociables) :
              </label>

              <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                <input
                  type="text"
                  value={redLineInput}
                  onChange={(e) => setRedLineInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddRedLine()}
                  placeholder="Ex: Pas de paiement à plus de 30 jours"
                  style={{
                    flex: 1,
                    padding: '10px',
                    fontSize: '14px',
                    border: '1px solid #ddd',
                    borderRadius: '8px'
                  }}
                />
                <button
                  onClick={handleAddRedLine}
                  style={{
                    padding: '10px 20px',
                    fontSize: '14px',
                    background: '#2196f3',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  Ajouter
                </button>
              </div>

              {context.red_lines.length > 0 && (
                <div style={{
                  background: '#f5f5f5',
                  borderRadius: '8px',
                  padding: '12px'
                }}>
                  {context.red_lines.map((line, i) => (
                    <div
                      key={i}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '8px',
                        marginBottom: i < context.red_lines.length - 1 ? '8px' : 0,
                        background: 'white',
                        borderRadius: '6px'
                      }}
                    >
                      <span>{line}</span>
                      <button
                        onClick={() => handleRemoveRedLine(i)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#f44336',
                          cursor: 'pointer',
                          fontSize: '18px',
                          padding: '0 8px'
                        }}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setCurrentStep('scenario')}
                style={{
                  flex: 1,
                  padding: '14px',
                  fontSize: '16px',
                  color: '#666',
                  background: '#f5f5f5',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
              >
                ← Retour
              </button>

              <button
                onClick={() => setCurrentStep('call')}
                disabled={!context.product || !context.target_price || !context.minimum_price}
                style={{
                  flex: 2,
                  padding: '14px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: 'white',
                  background: (context.product && context.target_price && context.minimum_price)
                    ? 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)'
                    : '#ccc',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: (context.product && context.target_price && context.minimum_price)
                    ? 'pointer'
                    : 'not-allowed'
                }}
              >
                Démarrer l'appel →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Phone Call */}
      {currentStep === 'call' && (
        <PhoneCallSetup
          context={context}
          scenario={selectedScenario}
          onComplete={handleCallComplete}
        />
      )}

      {/* Results */}
      {currentStep === 'results' && callResults && (
        <CallResults results={callResults} />
      )}
    </div>
  );
}
