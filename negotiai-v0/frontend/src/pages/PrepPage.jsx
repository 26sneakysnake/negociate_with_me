// frontend/src/pages/PrepPage.jsx
import React, { useState, useEffect } from 'react';
import { uploadContext, getTemplates } from '../services/api';

function PrepPage({ onReady }) {
  const [contextText, setContextText] = useState('');
  const [objective, setObjective] = useState('');
  const [minimum, setMinimum] = useState('');
  const [counterparty, setCounterparty] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');

  // Load templates on mount
  useEffect(() => {
    async function loadTemplates() {
      try {
        const data = await getTemplates();
        setTemplates(data);
      } catch (error) {
        console.error('Failed to load templates:', error);
      }
    }
    loadTemplates();
  }, []);

  const handleTemplateSelect = (e) => {
    const templateId = e.target.value;
    setSelectedTemplate(templateId);

    if (templateId) {
      const template = templates.find(t => t.id === templateId);
      if (template) {
        setContextText(template.context_template);
        setObjective(template.objective_template);
        setMinimum(template.minimum_template);
      }
    }
  };

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
        {templates.length > 0 && (
          <label>
            <strong>💡 Quick Start - Use a Template</strong>
            <select value={selectedTemplate} onChange={handleTemplateSelect}>
              <option value="">-- Select a template (optional) --</option>
              {templates.map(template => (
                <option key={template.id} value={template.id}>
                  {template.icon} {template.name} - {template.description}
                </option>
              ))}
            </select>
          </label>
        )}

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
