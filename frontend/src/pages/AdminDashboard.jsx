import { useState, useEffect } from 'react'
import { api } from '../api'
import { timeAgo, statusBadgeClass, confBarClass } from '../utils'
import UrgencyBar from '../components/UrgencyBar'

const ADMIN_PASSWORD = 'admin123'
const STATUS_OPTIONS = ['Submitted', 'In Progress', 'Resolved']
const DEPTS          = ['All', 'Maintenance', 'Mess Committee', 'Academic Office', 'Security', 'Admin']
const URGENCIES      = ['All', 'Critical', 'High', 'Medium', 'Low']

function LoginScreen({ onLogin }) {
  const [pwd, setPwd] = useState('')
  const [error, setError] = useState('')
  function handleLogin(e) {
    e.preventDefault()
    if (pwd === ADMIN_PASSWORD) onLogin()
    else setError('Incorrect password.')
  }
  return (
    <div className="auth-wrapper">
      <div className="auth-split" style={{ maxWidth: 560 }}>
        <div className="auth-brand" style={{ width: 220 }}>
          <div>
            <div className="auth-brand-logo" style={{ fontSize: 18 }}>🏫 Campus<span>Solve</span></div>
            <h2 style={{ fontSize: 20, marginTop: 16 }}>Admin Access</h2>
            <p>Manage and respond to student complaints.</p>
          </div>
          <div className="auth-brand-footer">Restricted access only</div>
        </div>
        <div className="auth-form-panel">
          <h3>Admin Login</h3>
          <p>Enter your admin password to continue.</p>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={pwd}
                onChange={e => { setPwd(e.target.value); setError('') }}
                placeholder="Enter password…" autoFocus />
            </div>
            {error && <div className="alert alert-error">{error}</div>}
            <button type="submit" className="btn btn-primary btn-full">Login →</button>
          </form>
        </div>
      </div>
    </div>
  )
}

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
      setSaved(true); setTimeout(() => setSaved(false), 2500); onUpdated()
    } catch (err) { alert('Update failed: ' + err.message) }
    finally { setSaving(false) }
  }

  const p = problem
  const conf = p.confidence ?? 0
  const imgUrl = api.imageUrl(p.image_path)

  return (
    <div className="problem-card" style={p.urgency === 'Critical' ? { borderLeft: '3px solid #ef4444' } : p.urgency === 'High' ? { borderLeft: '3px solid #f97316' } : {}}>
      <div className="row" style={{ cursor: 'pointer' }} onClick={() => setExpanded(x => !x)}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <code>#{p.id}</code>
          <span className={statusBadgeClass(p.status)}>{p.status}</span>
          <span className="badge badge-other">{p.department}</span>
          {imgUrl && <span className="badge badge-other" title="Has photo">📎</span>}
          {p.duplicate_of && (
            <span className="badge" style={{ background: 'var(--warning-bg)', color: 'var(--warning)', border: '1px solid var(--warning-border)' }}
              title={`Similar to #${p.duplicate_of}`}>⚠ Duplicate of #{p.duplicate_of}</span>
          )}
        </div>
        <div style={{ display: 'flex', gap: 14, alignItems: 'center', fontSize: 11.5, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          <span>{timeAgo(p.updated_at)}</span>
          <span style={{ opacity: 0.5 }}>{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      <p className="desc">{p.description}</p>

      {p.student_name && (
        <div style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: 6 }}>
          👤 {p.student_name} · {p.student_email}
        </div>
      )}

      {imgUrl && (
        <div className="card-photo-wrap">
          <img src={imgUrl} alt="Attached" className="card-photo"
            onClick={() => onLightbox(imgUrl)} title="Click to enlarge" />
          <span className="card-photo-label">📎 Attached photo</span>
        </div>
      )}

      <div className="meta" style={{ marginTop: imgUrl ? 10 : 0 }}>
        <span>{p.category}</span>
        <span>ai: {conf.toFixed(1)}%</span>
        <span>{timeAgo(p.created_at)}</span>
      </div>

      {/* Urgency bar */}
      <UrgencyBar urgency={p.urgency} />

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
            <input type="text" value={response} onChange={e => setResponse(e.target.value)}
              placeholder="Write a response for the student…" />
          </div>
          <div>
            <label>&nbsp;</label>
            <button className="btn btn-primary btn-sm" onClick={handleUpdate} disabled={saving}>
              {saving ? '…' : saved ? '✓ Saved' : '↑ Update'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default function AdminDashboard() {
  const [authed,        setAuthed]        = useState(false)
  const [problems,      setProblems]      = useState([])
  const [stats,         setStats]         = useState(null)
  const [loading,       setLoading]       = useState(true)
  const [error,         setError]         = useState('')
  const [filterStatus,  setFilterStatus]  = useState('All')
  const [filterDept,    setFilterDept]    = useState('All')
  const [filterUrgency, setFilterUrgency] = useState('All')
  const [lightbox,      setLightbox]      = useState(null)

  async function fetchData() {
    setLoading(true); setError('')
    try {
      const [all, s] = await Promise.all([api.getAll(), api.stats()])
      setProblems(all); setStats(s)
    } catch { setError('Could not load data. Is the backend running?') }
    finally { setLoading(false) }
  }

  useEffect(() => { if (authed) fetchData() }, [authed])

  if (!authed) return <LoginScreen onLogin={() => setAuthed(true)} />

  const filtered = problems.filter(p => {
    const okStatus  = filterStatus  === 'All' || p.status    === filterStatus
    const okDept    = filterDept    === 'All' || p.department === filterDept
    const okUrgency = filterUrgency === 'All' || p.urgency   === filterUrgency
    return okStatus && okDept && okUrgency
  })

  // Sort: Critical first, then High, Medium, Low
  const URGENCY_ORDER = { Critical: 0, High: 1, Medium: 2, Low: 3 }
  const sorted = [...filtered].sort((a, b) =>
    (URGENCY_ORDER[a.urgency] ?? 2) - (URGENCY_ORDER[b.urgency] ?? 2)
  )

  return (
    <div>
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
        <div className="metrics-row" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
          <div className="metric-card">
            <span className="label">Total</span>
            <div className="value">{stats.total}</div>
          </div>
          <div className="metric-card">
            <span className="label" style={{ color: '#1d4ed8' }}>Submitted</span>
            <div className="value" style={{ color: '#1d4ed8' }}>{stats.submitted}</div>
          </div>
          <div className="metric-card">
            <span className="label" style={{ color: '#92400e' }}>In Progress</span>
            <div className="value" style={{ color: '#92400e' }}>{stats.in_progress}</div>
          </div>
          <div className="metric-card">
            <span className="label" style={{ color: '#065f46' }}>Resolved</span>
            <div className="value" style={{ color: '#065f46' }}>{stats.resolved}</div>
          </div>
          <div className="metric-card">
            <span className="label" style={{ color: '#d97706' }}>Duplicates</span>
            <div className="value" style={{ color: '#d97706' }}>{stats.duplicates ?? 0}</div>
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
        <select value={filterUrgency} onChange={e => setFilterUrgency(e.target.value)}>
          {URGENCIES.map(u => <option key={u}>{u}</option>)}
        </select>
        <div className="spacer" />
        <span style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {sorted.length} / {problems.length}
        </span>
        <button className="btn btn-outline btn-sm" onClick={fetchData}>↺ Refresh</button>
      </div>

      {error   && <div className="alert alert-error">{error}</div>}
      {loading && <div className="spinner-wrap"><div className="spinner" /> Loading…</div>}

      {!loading && sorted.length === 0 && (
        <div className="empty-state">
          <span className="icon">🎉</span>
          <p>No problems match the current filters.</p>
        </div>
      )}

      {sorted.map(p => (
        <ProblemRow key={p.id} problem={p} onUpdated={fetchData} onLightbox={setLightbox} />
      ))}
    </div>
  )
}
