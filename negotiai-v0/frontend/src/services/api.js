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
