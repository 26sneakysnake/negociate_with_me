// frontend/src/services/api.js
const API_BASE = 'http://localhost:8000/api';

export async function uploadContext(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload-context`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  return response.json();
}

export async function generateStrategy(context) {
  const response = await fetch(`${API_BASE}/generate-strategy`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(context)
  });

  if (!response.ok) {
    throw new Error('Strategy generation failed');
  }

  return response.json();
}

export async function analyzeNegotiation(data) {
  const response = await fetch(`${API_BASE}/analyze-negotiation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  return response.json();
}

// V1 Features - Templates
export async function getTemplates() {
  const response = await fetch(`${API_BASE}/templates/`);

  if (!response.ok) {
    throw new Error('Failed to fetch templates');
  }

  return response.json();
}

export async function getTemplate(templateId) {
  const response = await fetch(`${API_BASE}/templates/${templateId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch template');
  }

  return response.json();
}

// V1 Features - Sessions
export async function getSessions() {
  const response = await fetch(`${API_BASE}/sessions/`);

  if (!response.ok) {
    throw new Error('Failed to fetch sessions');
  }

  return response.json();
}

export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch session');
  }

  return response.json();
}

export async function getPerformanceHistory() {
  const response = await fetch(`${API_BASE}/sessions/performance/history`);

  if (!response.ok) {
    throw new Error('Failed to fetch performance history');
  }

  return response.json();
}

// V1 Features - PDF Exports
export function getStrategyPdfUrl(sessionId) {
  return `${API_BASE}/sessions/${sessionId}/export/strategy`;
}

export function getAnalysisPdfUrl(sessionId) {
  return `${API_BASE}/sessions/${sessionId}/export/analysis`;
}

export async function downloadStrategyPdf(sessionId) {
  const response = await fetch(getStrategyPdfUrl(sessionId));

  if (!response.ok) {
    throw new Error('Failed to download strategy PDF');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `strategy-${sessionId}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export async function downloadAnalysisPdf(sessionId) {
  const response = await fetch(getAnalysisPdfUrl(sessionId));

  if (!response.ok) {
    throw new Error('Failed to download analysis PDF');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `analysis-${sessionId}.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
}
