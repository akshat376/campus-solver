const BASE = import.meta.env.VITE_API_URL || '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  // Sends description + optional image + student name/email
  submit: (description, imageFile, studentName, studentEmail) => {
    const form = new FormData()
    form.append('description',   description)
    form.append('student_name',  studentName  || '')
    form.append('student_email', studentEmail || '')
    if (imageFile) form.append('image', imageFile)

    return fetch(`${BASE}/submit`, { method: 'POST', body: form }).then(async res => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(err.detail || `HTTP ${res.status}`)
      }
      return res.json()
    })
  },

  getAll:   ()                       => request('/problems'),
  getOne:   (id)                     => request(`/problems/${id}`),
  update:   (id, status, response)   => request(`/update/${id}`, { method: 'POST', body: JSON.stringify({ status, response }) }),
  stats:    ()                       => request('/stats'),
  imageUrl: (imagePath)              => imagePath ? `${BASE}/images/${imagePath}` : null,
}
