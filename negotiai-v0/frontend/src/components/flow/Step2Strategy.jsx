import React from 'react';
import './Step2Strategy.css';

function Step2Strategy({ sessionData, goToStep }) {
  const { research_data, context } = sessionData;

  return (
    <div className="step2-strategy">
      <div className="step-header">
        <h1>🎯 Stratégie de négociation</h1>
        <p>Voici les informations collectées et la stratégie recommandée</p>
      </div>

      <div className="strategy-content">
        {/* Recherche Mistral */}
        {research_data && (
          <div className="research-section">
            <h2>🔍 Recherche Mistral AI</h2>
            <div className="research-card">
              <div className="research-header">
                <span className="company-name">{context.company_name}</span>
                <span className="badge">{research_data.company_info.industry}</span>
              </div>

              <div className="research-details">
                <div className="detail-item">
                  <span className="label">Taille :</span>
                  <span className="value">{research_data.company_info.size}</span>
                </div>

                <div className="detail-item">
                  <span className="label">Contexte :</span>
                  <span className="value">{research_data.company_info.context}</span>
                </div>

                {research_data.company_info.pain_points && research_data.company_info.pain_points.length > 0 && (
                  <div className="pain-points">
                    <span className="label">Points de douleur identifiés :</span>
                    <ul>
                      {research_data.company_info.pain_points.map((point, index) => (
                        <li key={index}>{point}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Contexte de négociation */}
        <div className="context-section">
          <h2>📋 Votre contexte</h2>
          <div className="context-grid">
            <div className="context-card">
              <div className="card-icon">💼</div>
              <div className="card-content">
                <div className="card-label">Produit/Service</div>
                <div className="card-value">{context.product}</div>
              </div>
            </div>

            <div className="context-card">
              <div className="card-icon">💰</div>
              <div className="card-content">
                <div className="card-label">Prix demandé</div>
                <div className="card-value">{context.target_price}</div>
              </div>
            </div>

            <div className="context-card">
              <div className="card-icon">⚠️</div>
              <div className="card-content">
                <div className="card-label">Prix minimum</div>
                <div className="card-value">{context.minimum_price}</div>
              </div>
            </div>

            {context.red_lines && context.red_lines.length > 0 && (
              <div className="context-card full-width">
                <div className="card-icon">🚫</div>
                <div className="card-content">
                  <div className="card-label">Red lines</div>
                  <div className="card-value">
                    {context.red_lines.map((line, index) => (
                      <span key={index} className="red-line-tag">{line}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Tactiques recommandées */}
        <div className="tactics-section">
          <h2>🎪 Tactiques à utiliser pendant la négociation</h2>
          <div className="tactics-grid">
            <div className="tactic-card">
              <div className="tactic-emoji">⚓</div>
              <div className="tactic-name">Ancrage</div>
              <div className="tactic-desc">Donnez un prix de référence bas dès le début</div>
            </div>

            <div className="tactic-card">
              <div className="tactic-emoji">🤐</div>
              <div className="tactic-name">Silence</div>
              <div className="tactic-desc">Restez silencieux après une offre pour créer la pression</div>
            </div>

            <div className="tactic-card">
              <div className="tactic-emoji">📊</div>
              <div className="tactic-name">Comparaison</div>
              <div className="tactic-desc">Mentionnez des alternatives moins chères</div>
            </div>

            <div className="tactic-card">
              <div className="tactic-emoji">⏰</div>
              <div className="tactic-name">Deadline</div>
              <div className="tactic-desc">Créez une urgence pour accélérer la décision</div>
            </div>

            <div className="tactic-card">
              <div className="tactic-emoji">📦</div>
              <div className="tactic-name">Lot</div>
              <div className="tactic-desc">Proposez d'acheter plusieurs produits/services</div>
            </div>

            <div className="tactic-card">
              <div className="tactic-emoji">🔄</div>
              <div className="tactic-name">Concession réciproque</div>
              <div className="tactic-desc">Si vous acceptez X, pouvez-vous faire Y?</div>
            </div>
          </div>
        </div>

        {/* Objectif */}
        <div className="objective-section">
          <h2>🏁 Objectif de la négociation</h2>
          <div className="objective-card">
            <p className="objective-text">
              Votre objectif est d'obtenir <strong>un prix au moins 20-30% inférieur</strong> au prix demandé ({context.target_price}),
              tout en restant au-dessus de votre prix minimum ({context.minimum_price}).
            </p>
            <p className="objective-text">
              L'agent IA utilisera diverses tactiques pour vous pousser à négocier. Restez ferme, utilisez les tactiques ci-dessus,
              et trouvez un <strong>compromis gagnant-gagnant</strong>.
            </p>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="step-actions">
        <button onClick={() => goToStep(1)} className="back-btn">
          ← Modifier le contexte
        </button>
        <button onClick={() => goToStep(3)} className="next-btn">
          Lancer l'appel →
        </button>
      </div>
    </div>
  );
}

export default Step2Strategy;
