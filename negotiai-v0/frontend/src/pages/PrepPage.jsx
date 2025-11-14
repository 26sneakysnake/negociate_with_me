// frontend/src/pages/PrepPage.jsx
import React, { useState } from 'react';
import { uploadContext } from '../services/api';

function PrepPage({ onReady }) {
  const [contextText, setContextText] = useState('');
  const [objective, setObjective] = useState('');
  const [minimum, setMinimum] = useState('');
  const [counterparty, setCounterparty] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const result = await uploadContext(file);
      setContextText(result.text);
    } catch (error) {
      alert('Error uploading file: ' + error.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSubmit = () => {
    if (!contextText || !objective || !minimum) {
      alert('Please fill in all required fields');
      return;
    }

    onReady({
      context_text: contextText,
      objective,
      minimum_acceptable: minimum,
      counterparty_name: counterparty
    });
  };

  return (
    <div className="prep-page">
      <h2>📋 Preparation Phase</h2>
      <p className="subtitle">Upload your context and define your objectives</p>

      <div className="form-section">
        <label>
          <strong>1. Upload Context (PDF or Text)</strong>
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileUpload}
            disabled={isUploading}
          />
          {isUploading && <span className="loading">Uploading...</span>}
        </label>

        <label>
          <strong>2. Or Paste Context Directly</strong>
          <textarea
            rows={6}
            value={contextText}
            onChange={(e) => setContextText(e.target.value)}
            placeholder="Paste contract, brief, or negotiation context here..."
          />
        </label>

        <label>
          <strong>3. Your Main Objective *</strong>
          <input
            type="text"
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            placeholder="e.g., Secure 50K€ annual contract"
          />
        </label>

        <label>
          <strong>4. Minimum Acceptable *</strong>
          <input
            type="text"
            value={minimum}
            onChange={(e) => setMinimum(e.target.value)}
            placeholder="e.g., Not below 35K€"
          />
        </label>

        <label>
          <strong>5. Counterparty Name (Optional)</strong>
          <input
            type="text"
            value={counterparty}
            onChange={(e) => setCounterparty(e.target.value)}
            placeholder="e.g., Acme Corp"
          />
        </label>

        <button
          className="primary-button"
          onClick={handleSubmit}
          disabled={!contextText || !objective || !minimum}
        >
          Generate Strategy →
        </button>
      </div>
    </div>
  );
}

export default PrepPage;
