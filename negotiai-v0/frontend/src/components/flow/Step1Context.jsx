import React, { useState } from 'react';
import axios from 'axios';
import './Step1Context.css';

function Step1Context({ sessionData, updateSessionData, goToStep }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    scenario: sessionData.scenario || 'saas',
    product: sessionData.context.product || '',
    company_name: sessionData.context.company_name || '',
    target_price: sessionData.context.target_price || '',
    minimum_price: sessionData.context.minimum_price || '',
    red_lines: sessionData.context.red_lines || []
  });
  const [newRedLine, setNewRedLine] = useState('');

  const scenarios = {
    saas: '💼 Négociation SaaS B2B',
    freelance: '💰 Négociation Tarif Freelance',
    salary: '🤝 Négociation Salariale',
    partnership: '🤜🤛 Négociation Partenariat',
    real_estate: '🏢 Négociation Immobilière'
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addRedLine = () => {
    if (newRedLine.trim()) {
      setFormData(prev => ({
        ...prev,
        red_lines: [...prev.red_lines, newRedLine.trim()]
      }));
      setNewRedLine('');
    }
  };

  const removeRedLine = (index) => {
    setFormData(prev => ({
      ...prev,
      red_lines: prev.red_lines.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Appel backend pour créer la session + recherche Mistral
      const response = await axios.post('http://localhost:8000/api/call/setup', {
        scenario: formData.scenario,
        context: {
          product: formData.product,
          company_name: formData.company_name,
          target_price: formData.target_price,
          minimum_price: formData.minimum_price,
          red_lines: formData.red_lines
        }
      });

      // Mise à jour des données de session
      updateSessionData({
        scenario: formData.scenario,
        context: {
          product: formData.product,
          company_name: formData.company_name,
          target_price: formData.target_price,
          minimum_price: formData.minimum_price,
          red_lines: formData.red_lines
        },
        session_id: response.data.session_id,
        research_data: response.data.research_data || null
      });

      // Passer à l'étape 2 (Stratégie)
      goToStep(2);

    } catch (error) {
      console.error('Setup error:', error);
      alert('Erreur lors de la configuration. Vérifiez vos données.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step1-context">
      <div className="step-header">
        <h1>📋 Préparez votre négociation</h1>
        <p>Renseignez le contexte. Si vous indiquez une entreprise, Mistral AI effectuera une recherche automatique.</p>
      </div>

      <form onSubmit={handleSubmit} className="context-form">
        {/* Scénario */}
        <div className="form-group">
          <label>Type de négociation *</label>
          <select
            name="scenario"
            value={formData.scenario}
            onChange={handleChange}
            required
          >
            {Object.entries(scenarios).map(([key, label]) => (
              <option key={key} value={key}>{label}</option>
            ))}
          </select>
        </div>

        {/* Produit/Service */}
        <div className="form-group">
          <label>Produit ou Service à négocier *</label>
          <input
            type="text"
            name="product"
            value={formData.product}
            onChange={handleChange}
            placeholder="Ex: Plateforme SaaS Analytics"
            required
          />
        </div>

        {/* Entreprise (optionnel - déclenche recherche) */}
        <div className="form-group">
          <label>
            Nom de l'entreprise cliente
            <span className="optional"> (optionnel - déclenche recherche Mistral)</span>
          </label>
          <input
            type="text"
            name="company_name"
            value={formData.company_name}
            onChange={handleChange}
            placeholder="Ex: Tesla, Airbnb, Shopify..."
          />
          {formData.company_name && (
            <div className="info-box">
              🔍 Mistral AI recherchera des informations sur cette entreprise pour personnaliser la négociation
            </div>
          )}
        </div>

        {/* Prix */}
        <div className="form-row">
          <div className="form-group">
            <label>Prix demandé *</label>
            <input
              type="text"
              name="target_price"
              value={formData.target_price}
              onChange={handleChange}
              placeholder="Ex: 50000€/an"
              required
            />
          </div>

          <div className="form-group">
            <label>Prix minimum acceptable *</label>
            <input
              type="text"
              name="minimum_price"
              value={formData.minimum_price}
              onChange={handleChange}
              placeholder="Ex: 35000€/an"
              required
            />
          </div>
        </div>

        {/* Red lines */}
        <div className="form-group">
          <label>Red lines (limites non négociables)</label>
          <div className="red-lines-input">
            <input
              type="text"
              value={newRedLine}
              onChange={(e) => setNewRedLine(e.target.value)}
              placeholder="Ex: Pas de paiement > 30 jours"
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addRedLine())}
            />
            <button type="button" onClick={addRedLine} className="add-btn">
              Ajouter
            </button>
          </div>

          {formData.red_lines.length > 0 && (
            <div className="red-lines-list">
              {formData.red_lines.map((line, index) => (
                <div key={index} className="red-line-item">
                  <span>{line}</span>
                  <button type="button" onClick={() => removeRedLine(index)}>×</button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit */}
        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner"></span>
              Recherche en cours...
            </>
          ) : (
            <>
              Valider et continuer
              <span className="arrow">→</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}

export default Step1Context;
