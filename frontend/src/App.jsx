import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar        from './components/Sidebar'
import SubmitForm     from './pages/SubmitForm'
import MyProblems     from './pages/MyProblems'
import AdminDashboard from './pages/AdminDashboard'
import Login          from './pages/Login'

export default function App() {
  const [user, setUser] = useState(null)   // { name, email }

  // Load user from localStorage on first render
  useEffect(() => {
    const stored = localStorage.getItem('campus_user')
    if (stored) setUser(JSON.parse(stored))
  }, [])

  function handleLogin(userData) {
    localStorage.setItem('campus_user', JSON.stringify(userData))
    setUser(userData)
  }

  function handleLogout() {
    localStorage.removeItem('campus_user')
    setUser(null)
  }

  if (!user) return <Login onLogin={handleLogin} />

  return (
    <div className="layout">
      <Sidebar user={user} onLogout={handleLogout} />
      <main className="main-content">
        <Routes>
          <Route path="/"      element={<SubmitForm user={user} />}     />
          <Route path="/track" element={<MyProblems />}                 />
          <Route path="/admin" element={<AdminDashboard />}             />
        </Routes>
      </main>
    </div>
  )
}