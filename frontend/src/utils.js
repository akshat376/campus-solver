export function timeAgo(isoStr) {
  if (!isoStr) return 'unknown'
  const diff = (Date.now() - new Date(isoStr).getTime()) / 1000
  if (diff < 60)     return 'just now'
  if (diff < 3600)   return `${Math.floor(diff / 60)} min ago`
  if (diff < 86400)  return `${Math.floor(diff / 3600)} hr ago`
  return `${Math.floor(diff / 86400)} days ago`
}

export function statusBadgeClass(status) {
  const map = {
    'Submitted':   'badge-submitted',
    'In Progress': 'badge-inprogress',
    'Resolved':    'badge-resolved',
  }
  return `badge ${map[status] || 'badge-other'}`
}

export function confBarClass(conf) {
  // conf is 0-100
  if (conf >= 75) return 'conf-bar-fill'
  if (conf >= 50) return 'conf-bar-fill mid'
  return 'conf-bar-fill low'
}