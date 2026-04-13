import { useState, useEffect } from 'react'
import { api } from '../api'
import { timeAgo, statusBadgeClass, confBarClass } from '../utils'
import UrgencyBar from '../components/UrgencyBar'

export default function MyProblems() {
  const [problems, setProblems] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState('')
  const [search,   setSearch]   = useState('')
  const [lightbox, setLightbox] = useState(null)

  const myIds = JSON.parse(localStorage.getItem('my_ids') || '[]')

  async function fetchProblems() {
    setLoading(true); setError('')
    try {
      const all = await api.getAll()
      setProblems(all.filter(p => myIds.includes(p.id)))
    } catch { setError('Could not load problems. Is the backend running?') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchProblems() }, [])

  const filtered = problems.filter(p =>
    p.id.toLowerCase().includes(search.toLowerCase()) ||
    p.description.toLowerCase().includes(search.toLowerCase())
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
        <h1>My Problems</h1>
        <p>Track complaints you've submitted this session.</p>
      </div>

      <div className="filters">
        <input type="text" placeholder="Search by ID or description…"
          value={search} onChange={e => setSearch(e.target.value)} style={{ maxWidth: 280 }} />
        <div className="spacer" />
        <span style={{ fontSize: 12, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          {filtered.length} / {problems.length}
        </span>
        <button className="btn btn-outline btn-sm" onClick={fetchProblems}>↺ Refresh</button>
      </div>

      {loading && <div className="spinner-wrap"><div className="spinner" /> Loading your problems…</div>}
      {error   && <div className="alert alert-error">{error}</div>}

      {!loading && myIds.length === 0 && (
        <div className="empty-state">
          <span className="icon">📭</span>
          <p>No problems submitted yet.<br />Head to <strong>Submit Problem</strong> to get started.</p>
        </div>
      )}

      {!loading && myIds.length > 0 && filtered.length === 0 && (
        <div className="empty-state"><span className="icon">🔍</span><p>No problems match your search.</p></div>
      )}

      {filtered.map(p => {
        const imgUrl = api.imageUrl(p.image_path)
        return (
          <div className="problem-card" key={p.id}>
            <div className="row">
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                <code>#{p.id}</code>
                <span className={statusBadgeClass(p.status)}>{p.status}</span>
                <span className="badge badge-other">{p.department}</span>
                {p.duplicate_of && (
                  <span className="badge" style={{ background: 'var(--warning-bg)', color: 'var(--warning)', border: '1px solid var(--warning-border)' }}
                    title={`Similar to #${p.duplicate_of}`}>⚠ Duplicate</span>
                )}
              </div>
              <span style={{ fontSize: 11.5, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                {timeAgo(p.updated_at)}
              </span>
            </div>

            <p className="desc">{p.description}</p>

            {imgUrl && (
              <div className="card-photo-wrap">
                <img src={imgUrl} alt="Attached" className="card-photo"
                  onClick={() => setLightbox(imgUrl)} title="Click to enlarge" />
                <span className="card-photo-label">📎 Attached photo</span>
              </div>
            )}

            <div className="meta" style={{ marginTop: imgUrl ? 10 : 0 }}>
              <span>{p.category}</span>
              <span>submitted {timeAgo(p.created_at)}</span>
            </div>

            {/* Urgency bar */}
            <UrgencyBar urgency={p.urgency} />

            <div style={{ marginTop: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11.5, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: 4 }}>
                <span>AI Confidence</span><span>{(p.confidence ?? 0).toFixed(1)}%</span>
              </div>
              <div className="conf-bar-track">
                <div className={confBarClass(p.confidence ?? 0)} style={{ width: `${Math.min(p.confidence ?? 0, 100)}%` }} />
              </div>
            </div>

            {p.response && (
              <div className="response-box">💬 <strong>Department response:</strong> {p.response}</div>
            )}
          </div>
        )
      })}
    </div>
  )
}
