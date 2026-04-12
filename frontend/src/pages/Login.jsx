import { useState } from 'react'

const ALLOWED_DOMAIN = 'iiitranchi.ac.in'

export default function Login({ onLogin }) {
  const [name,  setName]  = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')

  // Warn if user accidentally types their email in the name field
  const nameHasEmail = name.includes('@')

  function handleSubmit(e) {
    e.preventDefault()
    if (!name.trim()) {
      setError('Please enter your full name.')
      return
    }
    if (nameHasEmail) {
      setError('That looks like an email address — please enter your name above and your email below.')
      return
    }
    if (!email.trim()) {
      setError('Please enter your institute email address.')
      return
    }
    if (!email.trim().toLowerCase().endsWith(`@${ALLOWED_DOMAIN}`)) {
      setError(`Only @${ALLOWED_DOMAIN} email addresses are allowed.`)
      return
    }
    onLogin({ name: name.trim(), email: email.trim().toLowerCase() })
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>🏫</div>
          <h2 style={{ margin: 0 }}>Welcome to CampusSolve</h2>
          <p style={{ color: 'var(--text-muted)', marginTop: 6, fontSize: 14 }}>
            Sign in with your IIIT Ranchi email to continue.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Name field */}
          <div className="form-group">
            <label>Full Name</label>
            <input
              type="text"
              value={name}
              onChange={e => { setName(e.target.value); setError('') }}
              placeholder="e.g. Akshay Kumar"
              autoComplete="name"
              autoFocus
              style={nameHasEmail ? { borderColor: '#f97316' } : {}}
            />
            {nameHasEmail && (
              <div style={{ fontSize: 12, color: '#f97316', marginTop: 4 }}>
                ⚠ This looks like an email — please enter your name here and your email below.
              </div>
            )}
          </div>

          {/* Email field */}
          <div className="form-group">
            <label>Institute Email</label>
            <input
              type="email"
              value={email}
              onChange={e => { setEmail(e.target.value); setError('') }}
              placeholder={`e.g. akshay@${ALLOWED_DOMAIN}`}
              autoComplete="email"
            />
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 4 }}>
              Only <code>@{ALLOWED_DOMAIN}</code> addresses are accepted.
            </div>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <button type="submit" className="btn btn-primary btn-full">
            → Continue
          </button>
        </form>
      </div>
    </div>
  )
}