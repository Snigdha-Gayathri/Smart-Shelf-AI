const DEFAULT_PROD_API_BASE = 'https://smart-shelf-ai-backend-2.onrender.com'

function normalizeBase(url) {
  return (url || '').trim().replace(/\/$/, '')
}

export function getApiBase() {
  const fromEnv = normalizeBase(import.meta.env.VITE_BACKEND_URL || '')
  if (fromEnv) return fromEnv

  // Fallback for split Render deploys when env injection is missing.
  if (import.meta.env.PROD) return DEFAULT_PROD_API_BASE

  return ''
}
