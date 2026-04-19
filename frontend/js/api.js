const API_BASE = '/api/v1';

async function apiGet(path) {
  try {
    const response = await fetch(`${API_BASE}${path}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error?.message || `HTTP ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error('API GET error:', error);
    throw error;
  }
}

async function apiPost(path, body) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      const error = new Error(data.error?.message || `HTTP ${response.status}`);
      error.code = data.error?.code;
      error.field = data.error?.field;
      throw error;
    }

    return data;
  } catch (error) {
    console.error('API POST error:', error);
    throw error;
  }
}
