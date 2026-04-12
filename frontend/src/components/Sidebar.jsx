import { NavLink } from 'react-router-dom'

const links = [
  { to: '/',      icon: '✦', label: 'Submit Problem'  },
  { to: '/track', icon: '◎', label: 'My Problems'     },
  { to: '/admin', icon: '⬡', label: 'Admin Dashboard' },
]

function initials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

export default function Sidebar({ user, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        🏫 Campus<span>Solve</span>
      </div>

      <nav className="nav-section">
        {links.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <span style={{ fontSize: 13, width: 18, textAlign: 'center', flexShrink: 0 }}>{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {user && (
        <div className="sidebar-user">
          <div className="sidebar-user-info">
            <div className="sidebar-avatar">{initials(user.name)}</div>
            <div>
              <div className="sidebar-user-name">{user.name}</div>
              <div className="sidebar-user-email">{user.email}</div>
            </div>
          </div>
          <button className="sidebar-logout" onClick={onLogout}>Sign out</button>
        </div>
      )}

      <div className="sidebar-footer">
        AI-powered routing<br />v2.0 · 2025
      </div>
    </aside>
  )
}
