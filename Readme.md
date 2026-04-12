# 🏫 CampusSolve

An AI-powered campus complaint management system that automatically classifies and routes student complaints to the right department.

---

## Features

- 🤖 AI-based complaint classification and department routing
- 📋 Student login with institute email (`@iiitranchi.ac.in` only)
- 📷 Optional photo attachment with complaints
- 🔍 Track complaint status with a unique tracking ID
- 🛡️ Admin dashboard with password protection, filters, and status updates

---

## Project Structure

```
campus-solver/
├── backend/
│   ├── main.py           # FastAPI app & API routes
│   ├── database.py       # SQLAlchemy models & DB setup
│   ├── model.py          # ML model loading & prediction
│   ├── model.pkl         # Trained classifier
│   ├── vectorizer.pkl    # Trained TF-IDF vectorizer
│   ├── requirements.txt  # Python dependencies
│   └── problems.db       # SQLite database (auto-created)
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── SubmitForm.jsx
    │   │   ├── MyProblems.jsx
    │   │   └── AdminDashboard.jsx
    │   ├── components/
    │   │   └── Sidebar.jsx
    │   ├── api.js
    │   ├── utils.js
    │   ├── App.jsx
    │   └── main.jsx
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

---

### 1. Clone the repository

```bash
git clone https://github.com/your-username/campus-solver.git
cd campus-solver
```

---

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

If this is your first run or the database is missing columns, run the migration:

```bash
python migrate.py
```

Start the backend server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

---

### 3. Frontend setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## Usage

### Students

1. Open the app and log in with your IIIT Ranchi email (`@iiitranchi.ac.in`)
2. Go to **Submit Problem** — describe your issue and optionally attach a photo
3. The AI will classify your complaint and route it to the correct department instantly
4. Save your **Tracking ID** shown after submission
5. Go to **My Problems** to track the status and see any department response

### Admins

1. Go to **Admin Dashboard** and enter the admin password (`admin123`)
2. View all complaints filtered by status or department
3. Update the status (`Submitted` → `In Progress` → `Resolved`) and add a response
4. Changes are reflected immediately on the student's tracking page

---

## Complaint Categories & Routing

| Category | Routed To |
|---|---|
| Bathroom & Hygiene | Maintenance |
| Infrastructure / Maintenance | Maintenance |
| Mess & Food Quality | Mess Committee |
| Academic Issues | Academic Office |
| Anti-Ragging & Safety | Security |
| Other / Low confidence | Admin |

---

## Deployment

### Backend — Render

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port 8000` |

### Frontend — Vercel

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Framework | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |

Add this environment variable in Vercel:

```
VITE_API_URL = https://your-render-app.onrender.com
```

And update the CORS origin in `backend/main.py` to match your Vercel URL:

```python
allow_origins=[
    "http://localhost:5173",
    "https://your-app.vercel.app",
]
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/submit` | Submit a new complaint |
| `GET` | `/problems` | Get all complaints |
| `GET` | `/problems/{id}` | Get a single complaint |
| `POST` | `/update/{id}` | Update status and response |
| `GET` | `/stats` | Get dashboard statistics |
| `GET` | `/images/{filename}` | Serve uploaded images |

---

## Tech Stack

**Frontend** — React 18, React Router, Vite

**Backend** — FastAPI, SQLAlchemy, SQLite, scikit-learn

**Deployment** — Vercel (frontend), Render (backend)

---

## Notes

- The SQLite database and uploaded images are stored on Render's disk. On the **free tier**, this resets on every redeploy. For persistent storage, upgrade to Render's paid tier or migrate to PostgreSQL.
- Render's free tier **spins down after 15 minutes of inactivity**. The first request after sleep may take ~30 seconds.
- The admin password is hardcoded as `admin123` in `AdminDashboard.jsx` — change this before going to production.
