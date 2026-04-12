import { useState, useRef, useCallback } from 'react'
import { api } from '../api'
import { confBarClass } from '../utils'

const MIN_LEN = 10
const MAX_LEN = 500
const MAX_MB  = 5
const ALLOWED = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']

export default function SubmitForm({ user }) {
  const [desc,      setDesc]      = useState('')
  const [imageFile, setImageFile] = useState(null)
  const [preview,   setPreview]   = useState(null)
  const [dragging,  setDragging]  = useState(false)
  const [loading,   setLoading]   = useState(false)
  const [result,    setResult]    = useState(null)
  const [error,     setError]     = useState('')
  const fileRef = useRef()

  function saveId(id) {
    const existing = JSON.parse(localStorage.getItem('my_ids') || '[]')
    localStorage.setItem('my_ids', JSON.stringify([...existing, id]))
  }

  function handleFile(file) {
    if (!file) return
    if (!ALLOWED.includes(file.type)) {
      setError('Only JPEG, PNG, WEBP or GIF images are allowed.')
      return
    }
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`Image must be under ${MAX_MB} MB.`)
      return
    }
    setError('')
    setImageFile(file)
    setPreview(URL.createObjectURL(file))
  }

  function removeImage() {
    setImageFile(null)
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    if (fileRef.current) fileRef.current.value = ''
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files?.[0]
    if (file) handleFile(file)
  }, [])

  const onDragOver  = (e) => { e.preventDefault(); setDragging(true) }
  const onDragLeave = ()  => setDragging(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setResult(null)
    if (desc.trim().length < MIN_LEN) {
      setError(`Please describe the problem in at least ${MIN_LEN} characters.`)
      return
    }
    setLoading(true)
    try {
      // Pass user name + email with the submission
      const data = await api.submit(desc.trim(), imageFile, user.name, user.email)
      setResult(data)
      saveId(data.id)
      setDesc('')
      removeImage()
    } catch (err) {
      setError(err.message || 'Failed to submit. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const conf = result?.confidence ?? 0

  return (
    <div>
      <div className="page-header">
        <h1>Submit a Problem</h1>
        <p>
          Submitting as <strong style={{ color: 'var(--accent, #7eaaff)' }}>{user.name}</strong>
          <span style={{ color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: 12, marginLeft: 6 }}>
            ({user.email})
          </span>
        </p>
      </div>

      <div className="card">
        <div className="card-title">New complaint</div>
        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="desc">Problem Description</label>
            <textarea
              id="desc"
              value={desc}
              onChange={e => setDesc(e.target.value)}
              placeholder="e.g. The bathroom on the 3rd floor of Block A has had no water since yesterday morning..."
              maxLength={MAX_LEN}
              disabled={loading}
            />
            <div className="char-count">{desc.length} / {MAX_LEN}</div>
          </div>

          <div className="form-group">
            <label>Photo (optional)</label>
            {!preview ? (
              <div
                className={`upload-zone${dragging ? ' dragging' : ''}`}
                onClick={() => fileRef.current?.click()}
                onDrop={onDrop}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
              >
                <div className="upload-icon">📷</div>
                <div className="upload-text">
                  Drop an image here or <span className="upload-link">browse</span>
                </div>
                <div className="upload-hint">JPEG · PNG · WEBP · GIF &nbsp;·&nbsp; max {MAX_MB} MB</div>
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp,image/gif"
                  style={{ display: 'none' }}
                  onChange={e => handleFile(e.target.files?.[0])}
                />
              </div>
            ) : (
              <div className="image-preview-wrap">
                <img src={preview} alt="Attached" className="image-preview" />
                <button
                  type="button"
                  className="image-remove-btn"
                  onClick={removeImage}
                  title="Remove photo"
                >✕</button>
                <div className="image-filename">{imageFile?.name}</div>
              </div>
            )}
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading || desc.trim().length < MIN_LEN}
            style={{ marginTop: 4 }}
          >
            {loading
              ? <><span className="spinner" style={{ borderTopColor: '#fff' }} /> Submitting…</>
              : '→ Submit Problem'
            }
          </button>
        </form>
      </div>

      {result && (
        <div className="result-card">
          <div className="alert alert-success" style={{ marginBottom: 20 }}>
            ✓ Problem submitted — routed automatically.
          </div>

          <div className="result-grid">
            <div className="result-item">
              <div className="rlabel">Tracking ID</div>
              <div className="rvalue tracking-id">{result.id}</div>
            </div>
            <div className="result-item">
              <div className="rlabel">Category</div>
              <div className="rvalue" style={{ fontSize: 14, fontWeight: 600 }}>{result.category}</div>
            </div>
            <div className="result-item">
              <div className="rlabel">Routed To</div>
              <div className="rvalue" style={{ fontSize: 14, fontWeight: 600 }}>{result.department}</div>
            </div>
          </div>

          <div className="divider" />

          <div style={{ marginBottom: 6 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--text-muted)', marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.6px' }}>
              <span>AI Confidence</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>{conf.toFixed(1)}%</span>
            </div>
            <div className="conf-bar-track" style={{ height: 6 }}>
              <div className={confBarClass(conf)} style={{ width: `${Math.min(conf, 100)}%` }} />
            </div>
          </div>

          {conf < 50 && (
            <div className="alert alert-warning" style={{ marginTop: 14, marginBottom: 0 }}>
              ⚠ Low confidence — sent to Admin for manual review.
            </div>
          )}

          <div className="alert alert-info" style={{ marginTop: 14, marginBottom: 0 }}>
            A notification email has been sent to the <strong>{result.department}</strong> department.
            They can reply directly to <strong style={{ fontFamily: 'monospace' }}>{user.email}</strong>.
          </div>
        </div>
      )}
    </div>
  )
}