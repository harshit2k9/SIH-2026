import logging
import os
import secrets
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

import jwt
from config import settings
from database import Base, SessionLocal, close_db_pool, engine, get_pool, init_db_pool
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from routers.documents import router as documents_router
from services.face_match import compare_faces
from services.liveness import analyze_blink
from services.mfa import (
    create_provisioning_uri,
    create_qr_code_base64,
    generate_mfa_secret,
    verify_totp,
)
from sqlalchemy import text
from sqlalchemy.orm import Session

# Import all models to ensure they are registered with Base.metadata
from models import (
    User,
    UserMapping,
    Role,
    Department,
    UserDepartment,
    RevokedToken,
    Case,
    CaseStageHistory,
    CourtBench,
    CourtHearing,
    CourtOrder,
    OrderSheet,
    WarrantAndSummon,
    Document,
    DocumentVersion,
    DocumentAIMetadata,
    DigitalSignature,
    EvidenceProvider,
    EvidenceItem,
    EvidenceCustodyTransfer,
    ChainOfCustodyLog,
    InterDepartmentShare,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

# In-memory stores
LIVENESS_SESSIONS = {}
LOGIN_CHALLENGES = {}


# Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    # Create tables on startup - ensure all models are imported before this
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Could not create database tables: {e}")
    yield
    await close_db_pool()


# App
app = FastAPI(title="SIH26 SecureDocs", version="1.0.0", lifespan=lifespan)

# CORS - Must be added before routers and routes
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://sih-2026-mer1.onrender.com,https://*.app.github.dev,http://localhost:5173,http://127.0.0.1:5173",
)
# Parse origins, strip whitespace, and filter empty strings
allowed_origins = []
for origin in CORS_ORIGINS.split(","):
    stripped = origin.strip()
    if stripped:
        allowed_origins.append(stripped)

# Add wildcard pattern support for Render subdomains if needed
if not any("*" in o for o in allowed_origins):
    # Ensure the specific frontend URL is included
    frontend_url = "https://sih-2026-mer1.onrender.com"
    if frontend_url not in allowed_origins:
        allowed_origins.append(frontend_url)

logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Include routers
app.include_router(documents_router, prefix="/api")


# Health check
@app.get("/health")
def health():
    return {"status": "healthy"}


# Liveness check
@app.post("/api/liveness/check")
async def check_liveness(frames: list[UploadFile] = File(...)):
    if len(frames) < 12 or len(frames) > 50:
        return JSONResponse(
            content={"passed": False, "message": "Invalid frame count"},
            status_code=400,
        )

    usable_frames = []
    for frame in frames:
        if frame.content_type in ["image/jpeg", "image/jpg"]:
            contents = await frame.read()
            if contents and len(contents) <= 1024 * 1024:
                usable_frames.append(contents)

    if len(usable_frames) < 12:
        return JSONResponse(
            content={"passed": False, "message": "Not enough usable frames"},
            status_code=400,
        )

    try:
        result = analyze_blink(usable_frames)
        if result.get("passed"):
            token = secrets.token_urlsafe(32)
            LIVENESS_SESSIONS[token] = {
                "expires_at": time.time() + 300,
                "live_photo_bytes": usable_frames[-1],
            }
            result["liveness_token"] = token
            result["expires_in"] = 300
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Liveness error: {e}")
        return JSONResponse(
            content={"passed": False, "message": "Processing failed"},
            status_code=500,
        )


# Register - Bypass liveness and face verification for direct registration
@app.post("/api/auth/register")
async def register(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    aadhaar_number: str = Form(...),
    liveness_token: str = Form(None),  # Made optional
    aadhaar_image: UploadFile = File(None),  # Made optional
    db: Session = Depends(get_db),
):
    # Skip liveness check if token provided, or just proceed without it
    temp_reg_id = int(time.time() % 100000)

    # Always proceed with MFA setup - skip face verification
    mfa_secret = generate_mfa_secret()
    provisioning_uri = create_provisioning_uri(mfa_secret, email)
    qr_code = create_qr_code_base64(provisioning_uri)

    LOGIN_CHALLENGES[f"mfa_{temp_reg_id}"] = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "password": password,
        "mfa_secret": mfa_secret,
    }

    return {
        "status": "mfa_pending",
        "user_uid": f"REG-{temp_reg_id}",
        "qr_code": qr_code,
        "secret": mfa_secret,
    }


# MFA Setup
@app.post("/api/auth/mfa/setup")
async def mfa_setup(
    user_uid: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db),
):
    reg_data = LOGIN_CHALLENGES.get(f"mfa_{user_uid.replace('REG-', '')}")
    if not reg_data:
        raise HTTPException(status_code=400, detail="Invalid setup state")

    if not verify_totp(reg_data["mfa_secret"], code):
        raise HTTPException(status_code=401, detail="Invalid code")

    # Create user in database
    operational_user_id = str(uuid.uuid4())
    try:
        db.execute(
            text(
                "INSERT INTO public.users (id, full_name, email, badge_number,"
                " security_clearance_level, is_active, created_at) VALUES (:id,"
                " :name, :email, :badge, 1, true, NOW())"
            ),
            {
                "id": operational_user_id,
                "name": reg_data["full_name"],
                "email": reg_data["email"],
                "badge": f"REG-{user_uid.replace('REG-', '')}",
            },
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    del LOGIN_CHALLENGES[f"mfa_{user_uid.replace('REG-', '')}"]
    return {"status": "success", "message": "Account activated"}


# Login
@app.post("/api/auth/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.execute(
        text("SELECT * FROM public.users WHERE email = :email"),
        {"email": email},
    ).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    challenge = secrets.token_urlsafe(32)
    LOGIN_CHALLENGES[challenge] = {
        "user_uid": str(user.id),
        "expires_at": time.time() + 300,
    }

    return {"status": "mfa_required", "challenge_token": challenge}


# MFA Verify
@app.post("/api/auth/mfa/verify")
async def mfa_verify(
    challenge_token: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db),
):
    challenge = LOGIN_CHALLENGES.get(challenge_token)
    if not challenge or challenge["expires_at"] < time.time():
        raise HTTPException(status_code=401, detail="Invalid challenge")

    user = db.execute(
        text("SELECT * FROM public.users WHERE id = :uid"),
        {"uid": challenge["user_uid"]},
    ).fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Fetch user's primary department ID
    user_dept = db.execute(
        text("SELECT department_id FROM user_departments WHERE user_id = :uid AND is_primary = TRUE"),
        {"uid": challenge["user_uid"]},
    ).fetchone()
    
    department_id = str(user_dept.department_id) if user_dept else None
    
    now = datetime.utcnow()
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "roles": ["investigator"],
        "iat": now,
        "exp": now + timedelta(hours=8),
        "jti": str(uuid.uuid4()),
        "iss":settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    
    # Add department_id if available
    if department_id:
        payload["department_id"] = department_id

    with open(settings.JWT_PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()

    token = jwt.encode(payload, private_key, algorithm="RS256")
    del LOGIN_CHALLENGES[challenge_token]

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_uid": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
        },
    }


# Documents
@app.get("/api/documents")
async def get_documents(db: Session = Depends(get_db)):
    try:
        docs = db.execute(
            text(
                "SELECT id, title as name, document_type as type,"
                " document_number as idCode, created_at as updated FROM"
                " public.documents LIMIT 50"
            )
        ).fetchall()
        return [
            {
                "id": str(d.id),
                "name": d.name,
                "type": d.type,
                "status": "Verified",
                "pages": 10,
                "idCode": d.idCode,
                "updated": str(d.updated) if d.updated else "",
            }
            for d in docs
        ]
    except Exception as e:
        # Return empty list if table doesn't exist yet
        print(f"Documents table not available: {e}")
        return []


# Audit logs
@app.get("/api/audit-logs")
async def get_audit_logs(db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text(
                "SELECT action as title, actor_id as description, created_at as"
                " time FROM public.chain_of_custody_logs ORDER BY created_at"
                " DESC LIMIT 20"
            )
        )
        logs = result.fetchall()
        return [
            {
                "title": l.title,
                "description": f"Actor: {l.description}",
                "time": str(l.time) if l.time else "",
            }
            for l in logs
        ]
    except Exception as e:
        # Return empty list if table doesn't exist yet
        logger.warning(f"Audit logs table not available: {e}")
        return []


# Admin endpoints
@app.get("/admin/api/pending-users")
async def pending_users(db: Session = Depends(get_db)):
    try:
        users = db.execute(
            text(
                "SELECT id, full_name, email FROM public.users WHERE is_active ="
                " false LIMIT 50"
            )
        ).fetchall()
        return [
            {
                "user_uid": str(u.id),
                "full_name": u.full_name,
                "email": u.email,
                "face_similarity_score": 0.0,
                "admin_review_status": "PENDING",
            }
            for u in users
        ]
    except Exception as e:
        print(f"Pending users query failed: {e}")
        return []


@app.get("/admin/api/reviewed-users")
async def reviewed_users(db: Session = Depends(get_db)):
    try:
        users = db.execute(
            text(
                "SELECT id, full_name FROM public.users WHERE is_active = true"
                " LIMIT 50"
            )
        ).fetchall()

        return [
            {
                "user_uid": str(u.id),
                "full_name": u.full_name,
                "admin_review_status": "APPROVED",
            }
            for u in users
        ]
    except Exception as e:
        print(f"Reviewed users query failed: {e}")
        return []


@app.post("/admin/user/{user_uid}/approve")
async def approve_user(user_uid: str, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("UPDATE public.users SET is_active = true WHERE id = :id"),
            {"id": user_uid},
        )
        db.commit()
        return {"status": "approved"}
    except Exception as e:
        print(f"Approve user failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/user/{user_uid}/reject")
async def reject_user(user_uid: str, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("UPDATE public.users SET is_active = false WHERE id = :id"),
            {"id": user_uid},
        )
        db.commit()
        return {"status": "rejected"}
    except Exception as e:
        print(f"Reject user failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SERVE REACT FRONTEND - MUST BE LAST
frontend_dist = BASE_DIR.parent / "frontend" / "dist"

if frontend_dist.exists():
    app.mount(
        "/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend"
    )
    logger.info("✅ React frontend mounted")
else:

    @app.get("/")
    def root():
        return {
            "message": "Frontend not built. Run: cd frontend && npm run build"
        }
