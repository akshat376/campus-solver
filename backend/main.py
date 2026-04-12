from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid, os, shutil
from dotenv import load_dotenv

load_dotenv()

from model import load_model, predict
from database import SessionLocal, Problem

app = FastAPI(title="Campus Problem Solver API")

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://campus-solver-upzz.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

model, vectorizer = load_model()

DEPARTMENT_MAP = {
    "Bathroom & Hygiene":         "Maintenance",
    "Infrastructure/Maintenance": "Maintenance",
    "Mess & Food Quality":        "Mess Committee",
    "Academic Issues":            "Academic Office",
    "Anti-Ragging & Safety":      "Security",
    "Other":                      "Admin",
}

ALLOWED_DOMAIN = "iiitranchi.ac.in"

def route(category: str) -> str:
    return DEPARTMENT_MAP.get(category, "Admin")

class UpdateRequest(BaseModel):
    status: str
    response: str


@app.post("/submit")
async def submit_problem(
    description:   str               = Form(...),
    student_name:  str               = Form(default=""),
    student_email: str               = Form(default=""),
    image:         UploadFile | None = File(default=None),
):
    if not description or len(description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Description too short.")

    if not student_email.strip().lower().endswith(f"@{ALLOWED_DOMAIN}"):
        raise HTTPException(status_code=400, detail=f"Only @{ALLOWED_DOMAIN} email addresses are allowed.")

    category, confidence = predict(description.strip(), model, vectorizer)
    department  = route(category)
    tracking_id = str(uuid.uuid4())[:8].upper()

    image_path = ""
    if image and image.filename:
        ext = os.path.splitext(image.filename)[-1].lower()
        filename = f"{tracking_id}{ext}"
        with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
            shutil.copyfileobj(image.file, f)
        image_path = filename

    db = SessionLocal()
    problem = Problem(
        id=tracking_id,
        description=description.strip(),
        category=category,
        confidence=confidence,
        department=department,
        status="Submitted",
        response="",
        image_path=image_path,
        student_name=student_name.strip(),
        student_email=student_email.strip().lower(),
        created_at=datetime.now(timezone.utc).isoformat(),
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(problem)
    db.commit()
    db.close()

    return {
        "id":         tracking_id,
        "category":   category,
        "confidence": confidence,
        "department": department,
        "status":     "Submitted",
        "image_path": image_path,
    }


@app.get("/problems")
def get_all_problems():
    db = SessionLocal()
    problems = db.query(Problem).order_by(Problem.created_at.desc()).all()
    db.close()
    return [
        {
            "id":            p.id,
            "description":   p.description,
            "category":      p.category,
            "confidence":    p.confidence,
            "department":    p.department,
            "status":        p.status,
            "response":      p.response,
            "image_path":    p.image_path    or "",
            "student_name":  p.student_name  or "",
            "student_email": p.student_email or "",
            "created_at":    p.created_at,
            "updated_at":    p.updated_at,
        }
        for p in problems
    ]


@app.get("/problems/{problem_id}")
def get_problem(problem_id: str):
    db = SessionLocal()
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    db.close()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found.")
    return problem


@app.post("/update/{problem_id}")
def update_problem(problem_id: str, data: UpdateRequest):
    db = SessionLocal()
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        db.close()
        raise HTTPException(status_code=404, detail="Problem not found.")
    problem.status     = data.status
    problem.response   = data.response
    problem.updated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.close()
    return {"message": "Updated successfully."}


@app.get("/stats")
def get_stats():
    db = SessionLocal()
    problems = db.query(Problem).all()
    db.close()
    total       = len(problems)
    submitted   = sum(1 for p in problems if p.status == "Submitted")
    in_progress = sum(1 for p in problems if p.status == "In Progress")
    resolved    = sum(1 for p in problems if p.status == "Resolved")
    by_dept = {}
    for p in problems:
        by_dept[p.department] = by_dept.get(p.department, 0) + 1
    return {
        "total": total, "submitted": submitted,
        "in_progress": in_progress, "resolved": resolved,
        "by_department": by_dept,
    }
