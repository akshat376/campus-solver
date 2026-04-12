import os
import urllib.request
import urllib.error
import json
from datetime import datetime

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL     = os.getenv("FROM_EMAIL", "CampusSolve <onboarding@resend.dev>")

DEPARTMENT_EMAILS = {
    "Maintenance":     os.getenv("EMAIL_MAINTENANCE", "maintenance@yourcollege.edu"),
    "Mess Committee":  os.getenv("EMAIL_MESS",        "mess@yourcollege.edu"),
    "Academic Office": os.getenv("EMAIL_ACADEMIC",    "academic@yourcollege.edu"),
    "Security":        os.getenv("EMAIL_SECURITY",    "security@yourcollege.edu"),
    "Admin":           os.getenv("EMAIL_ADMIN",       "admin@yourcollege.edu"),
}


def send_complaint_email(problem_id: str, description: str, category: str,
                          department: str, confidence: float,
                          student_name: str = "", student_email: str = "") -> bool:
    if not RESEND_API_KEY:
        print("[email] RESEND_API_KEY not set — skipping.")
        return False

    recipient    = DEPARTMENT_EMAILS.get(department, DEPARTMENT_EMAILS["Admin"])
    submitted_at = datetime.now().strftime("%d %b %Y, %I:%M %p")
    display_name = student_name  or "Anonymous"
    reply_email  = student_email or ""

    conf_color      = "#34d399" if confidence >= 75 else "#fbbf24" if confidence >= 50 else "#f87171"
    low_conf_banner = f"""
        <div style="background:#451a03;border-left:4px solid #f97316;padding:10px 14px;border-radius:4px;margin-top:16px;font-size:13px;color:#fed7aa;">
            ⚠ Low AI confidence ({confidence:.1f}%) — please verify the category manually.
        </div>""" if confidence < 50 else ""

    html = f"""<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0f1117;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:580px;margin:32px auto;background:#1a1d27;border-radius:10px;overflow:hidden;border:1px solid #2a2d3a;">
    <div style="background:#2563eb;padding:20px 28px;">
      <div style="font-size:18px;font-weight:700;color:#fff;">🏫 CampusSolve</div>
      <div style="font-size:12px;color:#bfdbfe;margin-top:2px;">Automated Complaint Notification</div>
    </div>
    <div style="padding:24px 28px;">
      <p style="color:#e2e8f0;font-size:15px;margin:0 0 20px;">
        A new complaint has been routed to <strong style="color:#7eaaff;">{department}</strong>.
      </p>
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
        <tr>
          <td style="padding:8px 0;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:.6px;width:140px;">Tracking ID</td>
          <td style="padding:8px 0;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:14px;font-family:monospace;font-weight:700;">#{problem_id}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:.6px;">Submitted By</td>
          <td style="padding:8px 0;border-bottom:1px solid #2a2d3a;font-size:14px;">
            <span style="color:#f1f5f9;">{display_name}</span>
            <a href="mailto:{reply_email}" style="display:block;color:#7eaaff;font-size:12px;font-family:monospace;text-decoration:none;">{reply_email}</a>
          </td>
        </tr>
        <tr>
          <td style="padding:8px 0;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:.6px;">Category</td>
          <td style="padding:8px 0;border-bottom:1px solid #2a2d3a;color:#f1f5f9;font-size:14px;">{category}</td>
        </tr>
        <tr>
          <td style="padding:8px 0;border-bottom:1px solid #2a2d3a;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:.6px;">AI Confidence</td>
          <td style="padding:8px 0;border-bottom:1px solid #2a2d3a;font-size:14px;font-weight:700;color:{conf_color};">{confidence:.1f}%</td>
        </tr>
        <tr>
          <td style="padding:8px 0;color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:.6px;">Submitted At</td>
          <td style="padding:8px 0;color:#f1f5f9;font-size:14px;">{submitted_at}</td>
        </tr>
      </table>
      <div style="margin-top:20px;">
        <div style="color:#94a3b8;font-size:12px;text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px;">Description</div>
        <div style="background:#0f1117;border-left:3px solid #2563eb;padding:12px 16px;border-radius:4px;color:#cbd5e1;font-size:14px;line-height:1.6;">
          {description}
        </div>
      </div>
      {low_conf_banner}
      <div style="margin-top:20px;padding:12px 16px;background:#0f1117;border-radius:6px;border:1px solid #2a2d3a;font-size:13px;color:#94a3b8;">
        💬 <strong style="color:#e2e8f0;">To respond to the student</strong> — reply directly to
        <a href="mailto:{reply_email}" style="color:#7eaaff;">{reply_email}</a>
      </div>
      <div style="margin-top:20px;text-align:center;">
        <a href="https://campus-solver-upzz.vercel.app/admin"
           style="display:inline-block;background:#2563eb;color:#fff;text-decoration:none;padding:11px 28px;border-radius:6px;font-size:14px;font-weight:600;">
          → Open Admin Dashboard
        </a>
      </div>
    </div>
    <div style="padding:14px 28px;border-top:1px solid #2a2d3a;text-align:center;color:#4b5563;font-size:11px;">
      This is an automated message from CampusSolve.
    </div>
  </div>
</body>
</html>"""

    payload = json.dumps({
        "from":     FROM_EMAIL,
        "to":       [recipient],
        "reply_to": [reply_email] if reply_email else [],
        "subject":  f"[CampusSolve] New Complaint #{problem_id} — {category}",
        "html":     html,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            print(f"[email] ✓ Sent to {recipient} for #{problem_id}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[email] ✗ Resend API error for #{problem_id}: {e.code} {body}")
        return False
    except Exception as e:
        print(f"[email] ✗ Failed for #{problem_id}: {e}")
        return False
