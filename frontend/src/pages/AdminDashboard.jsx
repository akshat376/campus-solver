import { useState, useEffect } from 'react'
import { api } from '../api'
import { timeAgo, statusBadgeClass, confBarClass } from '../utils'

const ADMIN_PASSWORD = 'admin123'
const STATUS_OPTIONS = ['Submitted', 'In Progress', 'Resolved']
const DEPTS          = ['All', 'Maintenance', 'Mess Committee', 'Academic Office', 'Security', 'Admin']

// ── Login ────────────────────────────────────────────────────────────────────
function LoginScreen({ onLogin }) {
  const [pwd,   setPwd]   = useState('')
  const [error, setError] = useState('')

  function handleLogin(e) {
    e.preventDefault()
    if (pwd === ADMIN_PASSWORD) onLogin()
    else setError('Incorrect password.')
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h2>Admin Login</h2>
        <p>Enter your admin password to access the dashboard.</p>
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={pwd}
              onChange={e => { setPwd(e.target.value); setError('') }}
              placeholder="Enter password…"
              autoFocus
            />
          </div>
          {error && <div className="alert alert-error">{error}</div>}
          <button type="submit" className="btn btn-primary btn-full">→ Login</button>
        </form>
      </div>
    </div>
  )
}

// ── Problem Row ──────────────────────────────────────────────────────────────
function ProblemRow({ problem, onUpdated, onLightbox }) {
  const [expanded, setExpanded] = useState(problem.status === 'Submitted')
  const [status,   setStatus]   = useState(problem.status)
  const [response, setResponse] = useState(problem.response || '')
  const [saving,   setSaving]   = useState(false)
  const [saved,    setSaved]    = useState(false)

  async function handleUpdate() {
    setSaving(true)
    try {
      await api.update(problem.id, status, response)
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
      onUpdated()
    } catch (err) {
      alert('Update failed: ' + err.message)
    } finally {
      setSaving(false)
    }
  }

  const p      = problem
  const conf   = p.confidence ?? 0
  const imgUrl = api.imageUrl(p.image_path)

  return (
    <div className="problem-card">
      <div className="row" style={{ cursor: 'pointer' }} onClick={() => setExpanded(x => !x)}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <code>#{p.id}</code>
          <span className={statusBadgeClass(p.status)}>{p.status}</span>
          <span className="badge badge-other">{p.department}</span>
          {imgUrl && <span className="badge badge-other" title="Has photo">📎</span>}
        </div>
        <div style={{ display: 'flex', gap: 14, alignItems: 'center', fontSize: 11.5, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          <span>{timeAgo(p.updated_at)}</span>
          <span style={{ opacity: 0.5 }}>{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      <p className="desc">{p.description}</p>

      {/* Attached photo */}
      {imgUrl && (
        <div className="card-photo-wrap">
          <img
            src={imgUrl}
            alt="Attached"
            className="card-photo"
            onClick={() => onLightbox(imgUrl)}
            title="Click to enlarge"
          />
          <span className="card-photo-label">📎 Attached photo</span>
        </div>
      )}

      <div className="meta" style={{ marginTop: imgUrl ? 10 : 0 }}>
        <span>{p.category}</span>
        <span>ai: {conf.toFixed(1)}%</span>
        <span>{timeAgo(p.created_at)}</span>
      </div>

      <div style={{ marginTop: 10 }}>
        <div className="conf-bar-track">
          <div className={confBarClass(conf)} style={{ width: `${Math.min(conf, 100)}%` }} />
        </div>
      </div>

      {conf < 50 && (
        <div className="alert alert-warning" style={{ marginTop: 10, marginBottom: 0, padding: '7px 12px', fontSize: 12 }}>
          ⚠ Low AI confidence — verify category manually.
        </div>
      )}

      {expanded && (
        <div className="admin-actions">
          <div>
            <label>Status</label>
            <select value={status} onChange={e => setStatus(e.target.value)}>
              {STATUS_OPTIONS.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label>Response</label>
            <input
              type="text"
              value={response}
              onChange={e => setResponse(e.target.value)}
              placeholder="Add a response for the student…"
            />
          </div>
          <div>
            <label>&nbsp;</label>
            <button className="btn btn-primary" onClick={handleUpdate} disabled={saving}>
              {saving ? '…' : saved ? '✓ Saved' : '↑ Update'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main Dashboard ───────────────────────────────────────────────────────────
export default function AdminDashboard() {
  const [authed,       setAuthed]       = useState(false)
  const [problems,     setProblems]     = useState([])
  const [stats,        setStats]        = useState(null)
  const [loading,      setLoading]      = useState(true)
  const [error,        setError]        = useState('')
  const [filterStatus, setFilterStatus] = useState('All')
  const [filterDept,   setFilterDept]   = useState('All')
  const [lightbox,     setLightbox]     = useState(null)

  async function fetchData() {
    setLoading(true)
    setError('')
    try {
      const [all, s] = await Promise.all([api.getAll(), api.stats()])
      setProblems(all)
      setStats(s)
    } catch (err) {
      setError('Could not load data. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (authed) fetchData() }, [authed])

  if (!authed) return <LoginScreen onLogin={() => setAuthed(true)} />

  const filtered = problems.filter(p => {
    const okStatus = filterStatus === 'All' || p.status === filterStatus
    const okDept   = filterDept   === 'All' || p.department === filterDept
    return okStatus && okDept
  })

  return (
    <div>
      {/* Lightbox */}
      {lightbox && (
        <div className="lightbox-overlay" onClick={() => setLightbox(null)}>
          <img src={lightbox} alt="Full size" className="lightbox-img" onClick={e => e.stopPropagation()} />
          <button className="lightbox-close" onClick={() => setLightbox(null)}>✕</button>
        </div>
      )}

      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>Admin Dashboard</h1>
            <p>Manage and resolve student complaints.</p>
          </div>
          <button className="btn btn-outline btn-sm" onClick={() => setAuthed(false)}>← Logout</button>
        </div>
      </div>

      {stats && (
        <div className="metrics-row">
          <div className="metric-card">
            <span className="label">Total</span>
            <div className="value">{stats.total}</div>
          </div>
          <div className="metric-card">
            <span className="label" style={{ color: '#7eaaff' }}>Submitted</span>
            <div className="value" style={{ color: '#7eaaff' }}>{stats.submitted}</div>
          </div>
          <div className="metric-card">
            <span className="label" style={{ color: '#fbbf24' }}>In Progress</span>
            <div className="value" style={{ color: '#fbbf24' }}>{stats.in_progress}</div>
          </div>
          <div className="metric-card">
            <span className="label" style={{ color: '#34d399' }}>Resolved</span>
            <div className="value" style={{ color: '#34d399' }}>{stats.resolved}</div>
          </div>
        </div>
      )}

      <div className="filters">
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
          {['All', ...STATUS_OPTIONS].map(s => <option key={s}>{s}</option>)}
        </select>
        <select value={filterDept} onChange={e => setFilterDept(e.target.value)}>
          {DEPTS.map(d => <option key={d}>{d}</option>)}
        </select>
        <div className="spacer" />
        <span style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {filtered.length} / {problems.length}
        </span>
        <button className="btn btn-outline btn-sm" onClick={fetchData}>↺ Refresh</button>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {loading && <div className="spinner-wrap"><div className="spinner" /> Loading…</div>}

      {!loading && filtered.length === 0 && (
        <div className="empty-state">
          <span className="icon">🎉</span>
          <p>No problems match the current filters.</p>
        </div>
      )}

      {filtered.map(p => (
        <ProblemRow key={p.id} problem={p} onUpdated={fetchData} onLightbox={setLightbox} />
      ))}
    </div>
  )
}