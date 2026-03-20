function normalizeBase(url) {
  return (url || '').trim().replace(/\/$/, '')
}

export function getApiBase() {
  const fromEnv = normalizeBase(import.meta.env.VITE_BACKEND_URL || '')
  if (fromEnv) return fromEnv

  // Fallback to empty (local origin) if not provided
  return ''
}
