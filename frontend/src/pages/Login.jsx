import { useState } from 'react'

const ALLOWED_DOMAIN = 'iiitranchi.ac.in'

export default function Login({ onLogin }) {
  const [name,  setName]  = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')

  const nameHasEmail = name.includes('@')

  function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim()) { setError('Please enter your full name.'); return }
    if (nameHasEmail) { setError('That looks like an email — enter your name above and email below.'); return }
    if (!email.trim()) { setError('Please enter your institute email.'); return }
    if (!email.trim().toLowerCase().endsWith(`@${ALLOWED_DOMAIN}`)) {
      setError(`Only @${ALLOWED_DOMAIN} addresses are accepted.`)
      return
    }
    onLogin({ name: name.trim(), email: email.trim().toLowerCase() })
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-split">

        {/* Brand panel */}
        <div className="auth-brand">
          <div>
            <div className="auth-brand-logo">🏫 Campus<span>Solve</span></div>
            <h2>Your voice, routed to the right people.</h2>
            <p>Submit complaints, track their status, and hold your campus accountable — all in one place.</p>
          </div>
          <div className="auth-brand-footer">
            AI-powered routing · v2.0 · IIIT Ranchi
          </div>
        </div>

        {/* Form panel */}
        <div className="auth-form-panel">
          <h3>Sign in to continue</h3>
          <p>Use your institute credentials to access the portal.</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                value={name}
                onChange={e => { setName(e.target.value); setError('') }}
                placeholder="e.g. Akshay Kumar"
                autoFocus
                autoComplete="name"
                style={nameHasEmail ? { borderColor: '#f59e0b' } : {}}
              />
              {nameHasEmail && (
                <div className="field-hint" style={{ color: '#b45309' }}>
                  ⚠ Looks like an email — enter your name here, email below.
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Institute Email</label>
              <input
                type="email"
                value={email}
                onChange={e => { setEmail(e.target.value); setError('') }}
                placeholder={`e.g. you@${ALLOWED_DOMAIN}`}
                autoComplete="email"
              />
              <div className="field-hint">Only <code>@{ALLOWED_DOMAIN}</code> addresses accepted.</div>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <button type="submit" className="btn btn-primary btn-full" style={{ marginTop: 4 }}>
              Continue →
            </button>
          </form>
        </div>

      </div>
    </div>
  )
}
