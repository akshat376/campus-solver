import { NavLink } from 'react-router-dom'

const links = [
  { to: '/',      icon: '✦', label: 'Submit Problem'  },
  { to: '/track', icon: '◎', label: 'My Problems'     },
  { to: '/admin', icon: '⬡', label: 'Admin Dashboard' },
]

export default function Sidebar({ user, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        🏫 Campus<span>Solve</span>
      </div>

      {/* Logged-in user info */}
      {user && (
        <div style={{
          margin: '0 0 16px',
          padding: '10px 14px',
          background: 'var(--surface-2, #1e2130)',
          borderRadius: 8,
          border: '1px solid var(--border, #2a2d3a)',
        }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)', marginBottom: 2 }}>
            {user.name}
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', wordBreak: 'break-all' }}>
            {user.email}
          </div>
          <button
            onClick={onLogout}
            style={{
              marginTop: 8,
              fontSize: 11,
              color: 'var(--text-muted)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 0,
              textDecoration: 'underline',
            }}
          >
            Sign out
          </button>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <span className="icon" style={{ fontStyle: 'normal', fontSize: 13 }}>{icon}</span>
            {label}
          </NavLink>
        ))}
      </div>

      <div className="sidebar-footer">
        AI-powered routing<br />
        v2.0 · 2025
      </div>
    </aside>
  )
}