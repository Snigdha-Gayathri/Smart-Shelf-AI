import React from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider, AuthenticateWithRedirectCallback } from '@clerk/clerk-react'
import App from './App'
import ClerkApp from './ClerkApp'
import './index.css'

class RootErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    console.error('Root render error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: '100vh', display: 'grid', placeItems: 'center', background: '#FAF7F2', color: '#1f2937', padding: '24px', textAlign: 'center' }}>
          <div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.75rem' }}>SmartShelf UI failed to load</h1>
            <p style={{ margin: 0 }}>Please refresh once. If this continues, check Render logs and browser console.</p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

const rawClerkKey = (import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || '').trim()
const isPlaceholder = /your_|placeholder/i.test(rawClerkKey)
const isLikelyClerkKey = rawClerkKey.startsWith('pk_test_') || rawClerkKey.startsWith('pk_live_')
const clerkPublishableKey = isLikelyClerkKey && !isPlaceholder ? rawClerkKey : ''
const isCallbackRoute = window.location.pathname === '/sso-callback'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RootErrorBoundary>
      {clerkPublishableKey ? (
        <ClerkProvider publishableKey={clerkPublishableKey} afterSignOutUrl="/">
          {isCallbackRoute ? <AuthenticateWithRedirectCallback /> : <ClerkApp />}
        </ClerkProvider>
      ) : (
        <App />
      )}
    </RootErrorBoundary>
  </React.StrictMode>
)
