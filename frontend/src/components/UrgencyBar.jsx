import { urgencyKey } from '../utils'

export default function UrgencyBar({ urgency }) {
  const key = urgencyKey(urgency)
  return (
    <div className="urgency-bar">
      <div className="urgency-track">
        <div className={`urgency-fill ${key}`} />
      </div>
      <span className={`urgency-label ${key}`}>{urgency || 'Medium'}</span>
    </div>
  )
}
