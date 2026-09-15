import os
from pathlib import Path
import re
import secrets
import time
import uuid
import logging
import warnings
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pydantic import BaseModel
import asyncio

import bcrypt
import jwt
import easyocr
from fastapi import APIRouter, Depends,HTTPException, FastAPI, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import close_db_pool, init_db_pool, SessionLocal, engine, get_pool
from config import settings
from routers.documents import limiter, router as documents_router
from services.storage import ensure_bucket

from models import Base, User
from services.face_match import compare_faces
from services.liveness import analyze_blink
from services.mfa import (
    create_provisioning_uri,
    create_qr_code_base64,
    generate_mfa_secret,
    verify_totp,
)
from starlette.middleware.sessions import SessionMiddleware
from security.auth import AuthenticatedUser, verify_jwt

from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# ============================================================
# PATHS
# ============================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"
AADHAAR_DIR = UPLOADS_DIR / "aadhaar"
LIVE_PHOTO_DIR = UPLOADS_DIR / "live_photos"

for folder in [
    TEMPLATES_DIR,
    STATIC_DIR,
    UPLOADS_DIR,
    AADHAAR_DIR,
    LIVE_PHOTO_DIR,
]:
    folder.mkdir(exist_ok=True)




# ============================================================
# DATABASE
# ============================================================
#Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_uid(db: Session, user_uid: str):
    return db.query(User).filter(User.user_uid == user_uid).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user_mapping(db: Session, registration_user_id: int, operational_user_id: str):
    """
    Create mapping between registration user (Integer ID) and operational user (UUID).
    This should be called after user completes registration and verification.
    """

    # Check if mapping already exists
    existing = db.execute(
        text("SELECT 1 FROM public.user_mapping WHERE registration_user_id = :reg_id"),
        {"reg_id": registration_user_id}
    ).fetchone()

    if existing:
        logger.warning(f"Mapping already exists for registration user {registration_user_id}")
        return False

    # Create the mapping
    db.execute(
        text("""
            INSERT INTO public.user_mapping (registration_user_id, operational_user_id)
            VALUES (:reg_id, :op_id)
        """),
        {"reg_id": registration_user_id, "op_id": operational_user_id}
    )
    db.commit()
    logger.info(f"Created user mapping: registration {registration_user_id} -> operational {operational_user_id}")
    return True


async def provision_operational_user(db: Session, registration_user: User):
    """
    Automatically create operational user account after successful registration.
    This bridges the registration system (Integer ID) with the operational system (UUID).

    Args:
        db: Database session
        registration_user: The verified registration user

    Returns:
        str: The operational user UUID if successful, None if failed
    """
    from sqlalchemy import text
    import uuid as uuid_lib

    try:
        # Check if operational user already exists for this registration user
        existing_mapping = db.execute(
            text("SELECT operational_user_id FROM public.user_mapping WHERE registration_user_id = :reg_id"),
            {"reg_id": registration_user.id}
        ).fetchone()

        if existing_mapping:
            logger.info(f"Operational user already exists for registration user {registration_user.id}")
            return str(existing_mapping.operational_user_id)

        # Generate new UUID for operational user
        operational_user_id = str(uuid_lib.uuid4())

        # Get default department and role (can be configured via environment variables)
        default_department_id = os.getenv("DEFAULT_DEPARTMENT_ID")
        default_role_id = os.getenv("DEFAULT_ROLE_ID")

        # If not configured, try to get the first available department and role
        if not default_department_id:
            dept_result = db.execute(
                text("SELECT id FROM public.departments LIMIT 1")
            ).fetchone()
            if dept_result:
                default_department_id = str(dept_result.id)
            else:
                logger.error("No departments found in database. Cannot provision user.")
                return None

        if not default_role_id:
            role_result = db.execute(
                text("SELECT id FROM public.roles WHERE name = 'investigator' LIMIT 1")
            ).fetchone()
            if role_result:
                default_role_id = str(role_result.id)
            else:
                # Fallback to first available role
                role_result = db.execute(
                    text("SELECT id FROM public.roles LIMIT 1")
                ).fetchone()
                if role_result:
                    default_role_id = str(role_result.id)
                else:
                    logger.error("No roles found in database. Cannot provision user.")
                    return None

        # Create operational user
        db.execute(
            text("""
                INSERT INTO public.users (id, full_name, email, badge_number, security_clearance_level, is_active, created_at)
                VALUES (:id, :full_name, :email, :badge_number, :clearance_level, true, NOW())
            """),
            {
                "id": operational_user_id,
                "full_name": registration_user.full_name,
                "email": registration_user.email,
                "badge_number": f"REG-{registration_user.id:06d}",  # Auto-generate badge number
                "clearance_level": 1,  # Default clearance level
            }
        )

        # Assign user to department with role
        db.execute(
            text("""
                INSERT INTO public.user_departments (id, user_id, department_id, role_id, is_primary, assigned_at)
                VALUES (:id, :user_id, :dept_id, :role_id, true, NOW())
            """),
            {
                "id": str(uuid_lib.uuid4()),
                "user_id": operational_user_id,
                "dept_id": default_department_id,
                "role_id": default_role_id,
            }
        )

        # Create mapping
        db.execute(
            text("""
                INSERT INTO public.user_mapping (registration_user_id, operational_user_id)
                VALUES (:reg_id, :op_id)
            """),
            {"reg_id": registration_user.id, "op_id": operational_user_id}
        )

        db.commit()

        logger.info(
            f"✅ Automated user provisioning successful: "
            f"registration {registration_user.id} ({registration_user.email}) -> "
            f"operational {operational_user_id}"
        )

        return operational_user_id

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Failed to provision operational user for registration {registration_user.id}: {e}")
        return None

#================
#LIFESPAN
#+===================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database pool and storage...")
    await init_db_pool()
    await ensure_bucket()
    yield
    # Shutdown
    logger.info("Shutting down, closing database pool...")
    await close_db_pool()


# ============================================================
# SESSION COOKIE
# ============================================================
"""SESSION_SECRET = os.getenv(
    "SIH26_SESSION_SECRET",
    "DEV-ONLY-CHANGE-THIS-BEFORE-PRODUCTION-" + secrets.token_hex(32),
)"""
SESSION_SECRET = os.getenv("SIH26_SESSION_SECRET")
if not SESSION_SECRET:
    import warnings
    warnings.warn(
        "SIH26_SESSION_SECRET not set! Generating random secret. "
        "This will break sessions on restart. Set it in .env for production!"
    )
    SESSION_SECRET = secrets.token_hex(32)

#------session id and token transfer---------
auth_router = APIRouter()


class TokenRequest(BaseModel):
    # The frontend will send the session cookie automatically
    pass

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@auth_router.post("/api/auth/token", response_model=TokenResponse)
async def get_access_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Exchange session cookie for JWT access token.

    This endpoint validates the user's session (from login) and returns
    a JWT token that can be used for API authentication.
    """
    # 1. Get user from session (set during HTML login)
    authenticated = request.session.get("authenticated")
    user_uid = request.session.get("user_uid")

    if not authenticated or not user_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login first."
        )

    # 2. Fetch user from database
    user = get_user_by_uid(db, user_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 3. Verify user is active and MFA-enabled
    if user.registration_status != "ACTIVE" or not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not fully activated"
        )

    # 4. Get operational user UUID from mapping table
    
    mapping_result = db.execute(
        text("""
            SELECT operational_user_id
            FROM public.user_mapping
            WHERE registration_user_id = :reg_user_id
        """),
        {"reg_user_id": user.id}
    )
    mapping_row = mapping_result.fetchone()

    if not mapping_row:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not mapped to operational account. Contact administrator."
        )

    operational_user_id = mapping_row.operational_user_id

    # 5. Get user's department and role from operational system

    department_result = db.execute(
        text("""
            SELECT ud.department_id, r.name as role_name
            FROM public.user_departments ud
            JOIN public.roles r ON ud.role_id = r.id
            WHERE ud.user_id = :user_id AND ud.is_primary = TRUE
        """),
        {"user_id": str(operational_user_id)}
    )
    department_row = department_result.fetchone()
    department_id = department_row.department_id if department_row else None
    role_name = department_row.role_name if department_row else "investigator"

    # 6. Generate JWT token
    now = datetime.utcnow()
    payload = {
        "sub": str(operational_user_id),                    # User UUID as string
        "email": user.email,
        "roles": [role_name],              # Fetch from user_departments.role_id
        "department_id": str(department_id) if department_id else None,
        "iat": now,
        "exp": now + timedelta(minutes=30),     # 30 minute expiry
        "jti": str(uuid.uuid4()),               # Unique token ID
        "aud": settings.JWT_AUDIENCE,
        "iss": settings.JWT_ISSUER,
    }

    # 7. Sign with private key
    key_path = os.getenv("JWT_PRIVATE_KEY_PATH", "keys/private.pem")
    with open(key_path, "r") as f:
        private_key = f.read()

    access_token = jwt.encode(payload, private_key, algorithm="RS256")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )
# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(
    title="SIH26 Secure Document Management System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================
# TEMPLATES / STATIC/routing
# ============================================================

app.include_router(documents_router)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth_router)

# ===========================================================
#limiters
#===========================================================
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================
# MIDDLEWARE
# ============================================================
# 1. Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Session Middleware configuration
# 2. Session Middleware
SESSION_SECRET = os.getenv("SIH26_SESSION_SECRET")
if not SESSION_SECRET:
    warnings.warn(
        "SIH26_SESSION_SECRET not set! Generating random secret. "
        "This will break sessions on container restart. Set it in .env for production!",
        RuntimeWarning,
        stacklevel=2
    )
    SESSION_SECRET = secrets.token_hex(32)


app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="sih26_session",
    max_age=1800,  # Reduced from 3600 to 30 minutes for security
    same_site="strict",  # Changed from "lax" to "strict" for CSRF protection
    https_only=os.getenv("ENVIRONMENT") == "production",  # Dynamic based on environment
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")

# 3. CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["Content-Length", "X-Request-ID"],
)



def ensure_jwt_keys_exist():
    """Generate RSA key pair if they don't exist."""
    private_key_path = Path(settings.JWT_PRIVATE_KEY_PATH)
    public_key_path = Path(settings.JWT_PUBLIC_KEY_PATH)

    if not private_key_path.exists() or not public_key_path.exists():
        logger.info("🔑 Generating JWT key pair...")

        # Create directory if needed
        private_key_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Serialize private key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key
        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Write keys with secure permissions
        with open(private_key_path, "wb") as f:
            f.write(pem_private)
        private_key_path.chmod(0o600)  # Owner read/write only

        with open(public_key_path, "wb") as f:
            f.write(pem_public)
        public_key_path.chmod(0o644)  # Owner read/write, others read

        logger.info("✅ JWT keys generated successfully")
    else:
        logger.info("✅ Existing JWT keys loaded")

# Call this BEFORE the lifespan context
ensure_jwt_keys_exist()


#----------------------------------------------------------------------
# ============================================================
# OCR & VERHOEFF VERIFICATION SETUP
# ============================================================
logger.info("Loading EasyOCR models (this may take 15-30 seconds)...")
ocr_reader = easyocr.Reader(["en", "hi"], gpu=False)
logger.info("EasyOCR models loaded successfully.")



VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 1, 2, 3, 4],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]

VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]


def validate_verhoeff(number_str: str) -> bool:
    if not number_str:
        return False

    clean_num = str(number_str).strip().replace(" ", "").replace("-", "")

    if not clean_num.isdigit() or len(clean_num) != 12 or clean_num[0] in ('0', '1'):
        return False

    c = 0
    for i, item in enumerate(reversed(clean_num)):
        c = VERHOEFF_D[c][VERHOEFF_P[i % 8][int(item)]]

    return c == 0


def is_valid_aadhaar_document(image_bytes: bytes) -> bool:
    try:
        results = ocr_reader.readtext(image_bytes, detail=0)
        extracted_text = " ".join(results)
        text_lower = extracted_text.lower()

        keywords = [
            "government of india",
            "unique identification authority of india",
            "bharat sarkar",
            "dob",
            "male",
            "female",
            "enrollment",
        ]
        keyword_matches = sum(1 for kw in keywords if kw in text_lower)

        if keyword_matches < 1:
            return False

        digit_groups = re.findall(r"\b\d{4}\s?\d{4}\s?\d{4}\b", extracted_text)
        for group in digit_groups:
            clean_digits = re.sub(r"\D", "", group)
            if len(clean_digits) == 12 and validate_verhoeff(clean_digits):
                return True

        return keyword_matches >= 2
    except Exception as e:
        print("DOCUMENT VALIDATION ERROR:", repr(e))
        return False



# ============================================================
# LIVENESS SESSION STORAGE
# ============================================================
LIVENESS_SESSIONS = {}
LIVENESS_SESSION_LIFETIME = 300


def clean_expired_liveness_sessions():
    now = time.time()
    expired = [
        token
        for token, data in LIVENESS_SESSIONS.items()
        if data["expires_at"] < now
    ]
    for token in expired:
        LIVENESS_SESSIONS.pop(token, None)


def create_liveness_session(live_photo_bytes: bytes):
    clean_expired_liveness_sessions()
    token = secrets.token_urlsafe(32)
    LIVENESS_SESSIONS[token] = {
        "expires_at": time.time() + LIVENESS_SESSION_LIFETIME,
        "live_photo_bytes": live_photo_bytes,
    }
    return token


def get_liveness_session(token: str):
    clean_expired_liveness_sessions()
    if not token:
        return None
    return LIVENESS_SESSIONS.get(token)


def consume_liveness_session(token: str):
    LIVENESS_SESSIONS.pop(token, None)


# ============================================================
# LOGIN CHALLENGES
# ============================================================
LOGIN_CHALLENGES = {}
LOGIN_CHALLENGE_LIFETIME = 300


def clean_expired_login_challenges():
    now = time.time()
    expired = [
        token
        for token, data in LOGIN_CHALLENGES.items()
        if data["expires_at"] < now
    ]
    for token in expired:
        LOGIN_CHALLENGES.pop(token, None)


def create_login_challenge(user_uid: str):
    clean_expired_login_challenges()
    token = secrets.token_urlsafe(32)
    LOGIN_CHALLENGES[token] = {
        "user_uid": user_uid,
        "expires_at": time.time() + LOGIN_CHALLENGE_LIFETIME,
    }
    return token


def get_login_challenge(token: str):
    clean_expired_login_challenges()
    if not token:
        return None
    return LOGIN_CHALLENGES.get(token)


def consume_login_challenge(token: str):
    LOGIN_CHALLENGES.pop(token, None)


# ============================================================
# USER HELPERS
# ============================================================
"""def get_user_by_uid(db: Session, user_uid: str):
    return db.query(User).filter(User.user_uid == user_uid).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
"""

# ============================================================
# LOGIN PROTECTION
# ============================================================
def get_logged_in_user(request: Request, db: Session):
    authenticated = request.session.get("authenticated")
    user_uid = request.session.get("user_uid")

    if not authenticated or not user_uid:
        return None

    user = get_user_by_uid(db, user_uid)

    if not user or user.registration_status != "ACTIVE" or not user.mfa_enabled:
        return None

    return user


# ============================================================
# SYSTEM ROUTES
# ============================================================
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "SIH26 backend is running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/health/db")
async def health_db():
    """Check database connectivity"""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unhealthy: {str(e)}"
        )


@app.get("/health/storage")
async def health_storage():
    """Check MinIO/S3 storage connectivity"""
    try:
        await ensure_bucket()
        return {"status": "healthy", "storage": "connected"}
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Storage unhealthy: {str(e)}"
        )


@app.get("/health/antivirus")
async def health_antivirus():
    """Check ClamAV connectivity"""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(settings.CLAMAV_HOST, settings.CLAMAV_PORT),
            timeout=5.0
        )
        writer.close()
        await writer.wait_closed()
        return {"status": "healthy", "antivirus": "connected"}
    except Exception as e:
        logger.error(f"Antivirus health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Antivirus unhealthy: {str(e)}"
        )


# ============================================================
# REGISTRATION HELPERS & ROUTES
# ============================================================
@app.get("/register", response_class=HTMLResponse)
def registration_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": None},
    )


def registration_error(request: Request, message: str):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": message},
        status_code=400,
    )


def delete_file(filepath):
    if not filepath:
        return
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass


async def read_image_upload(uploaded_file: UploadFile):
    allowed = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    if uploaded_file.content_type not in allowed:
        raise ValueError("Only JPG, PNG and WEBP images are allowed.")

    contents = await uploaded_file.read()

    if not contents:
        raise ValueError("Uploaded image is empty.")

    if len(contents) > (5 * 1024 * 1024):
        raise ValueError("Uploaded image must be smaller than 5 MB.")

    return contents, allowed[uploaded_file.content_type]


def save_image_bytes(
    contents: bytes, folder: Path, user_uid: str, extension: str
):
    filename = f"{user_uid}_{uuid.uuid4().hex}{extension}"
    filepath = folder / filename

    with open(filepath, "wb") as file:
        file.write(contents)

    return str(filepath)


@app.post("/api/liveness/check")
async def check_liveness(frames: list[UploadFile] = File(...)):
    if len(frames) < 12 or len(frames) > 50:
        return JSONResponse(
            content={
                "passed": False,
                "message": "Invalid number of camera frames.",
            },
            status_code=400,
        )

    usable_frames = []
    for frame in frames:
        if frame.content_type not in ["image/jpeg", "image/jpg"]:
            continue

        contents = await frame.read()
        if not contents or len(contents) > (1024 * 1024):
            continue

        usable_frames.append(contents)

    if len(usable_frames) < 12:
        return JSONResponse(
            content={
                "passed": False,
                "message": "Not enough usable camera frames.",
            },
            status_code=400,
        )

    try:
        result = analyze_blink(usable_frames)
    except Exception as error:
        print("LIVENESS ERROR:", repr(error))
        return JSONResponse(
            content={
                "passed": False,
                "message": "Liveness processing failed.",
            },
            status_code=500,
        )

    if result.get("passed"):
        live_photo = usable_frames[-1]
        token = create_liveness_session(live_photo)
        result["liveness_token"] = token
        result["expires_in"] = LIVENESS_SESSION_LIFETIME

    return JSONResponse(content=result)


@app.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    aadhaar_number: str = Form(...),
    liveness_token: str = Form(...),
    aadhaar_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip()
    aadhaar_number = aadhaar_number.strip()

    if len(full_name) < 3:
        return registration_error(request, "Please enter your full name.")

    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if not re.match(email_pattern, email):
        return registration_error(request, "Invalid email address.")

    if not phone.isdigit() or len(phone) != 10:
        return registration_error(
            request, "Phone number must contain exactly 10 digits."
        )

    if len(password) < 8:
        return registration_error(
            request, "Password must contain at least 8 characters."
        )

    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        return registration_error(request, "Password is too long.")

    if not validate_verhoeff(aadhaar_number):
        return registration_error(
            request, "The entered Aadhaar number is mathematically invalid."
        )

    if db.query(User).filter(User.email == email).first():
        return registration_error(
            request, "This email is already registered."
        )

    if db.query(User).filter(User.phone == phone).first():
        return registration_error(
            request, "This phone number is already registered."
        )

    session = get_liveness_session(liveness_token)
    if not session:
        return registration_error(
            request, "Liveness verification expired. Please try again."
        )

    live_photo_bytes = session["live_photo_bytes"]

    try:
        aadhaar_bytes, aadhaar_extension = await read_image_upload(
            aadhaar_image
        )
    except ValueError as error:
        return registration_error(request, str(error))

    # --- Document Verification Check (Keywords + Verhoeff) ---
    if not is_valid_aadhaar_document(aadhaar_bytes):
        return registration_error(
            request,
            "Uploaded document does not appear to be a valid Aadhaar card.",
        )
    # ---------------------------------------------------------

    face_verified = False
    try:
        face_result = compare_faces(aadhaar_bytes, live_photo_bytes)
        face_verified = face_result["matched"]
        print("FACE RESULT:", face_result)
    except Exception as error:
        print("FACE MATCH ERROR:", repr(error))
        face_verified = False

    registration_status = "MFA_PENDING" if face_verified else "FLAGGED"
    user_uid = "SIH-" + uuid.uuid4().hex[:12].upper()

    aadhaar_path = None
    live_photo_path = None

    try:
        aadhaar_path = save_image_bytes(
            aadhaar_bytes, AADHAAR_DIR, user_uid, aadhaar_extension
        )
        live_photo_path = save_image_bytes(
            live_photo_bytes, LIVE_PHOTO_DIR, user_uid, ".jpg"
        )
    except Exception as error:
        print("FILE ERROR:", repr(error))
        delete_file(aadhaar_path)
        delete_file(live_photo_path)
        return registration_error(request, "Could not save identity files.")

    password_hash = bcrypt.hashpw(
        password_bytes, bcrypt.gensalt()
    ).decode("utf-8")

    user = User(
        user_uid=user_uid,
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=password_hash,
        aadhaar_number=aadhaar_number,
        aadhaar_image=aadhaar_path,
        live_photo=live_photo_path,
        face_verified=face_verified,
        registration_status=registration_status,
        mfa_secret=None,
        mfa_enabled=False,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as error:
        db.rollback()
        print("DATABASE ERROR:", repr(error))
        delete_file(aadhaar_path)
        delete_file(live_photo_path)
        return registration_error(request, "Registration failed.")

    consume_liveness_session(liveness_token)

    if face_verified:
        return RedirectResponse(
            url=f"/mfa/setup/{user_uid}", status_code=303
        )

    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Manual Review Required</title>
        </head>
        <body>
            <h1>Manual Review Required</h1>
            <p>Face verification could not be confirmed.</p>
            <p>Registration ID: <strong>{user_uid}</strong></p>
        </body>
        </html>
        """
    )


# ============================================================
# MFA SETUP & VERIFICATION
# ============================================================
@app.get("/mfa/setup/{user_uid}", response_class=HTMLResponse)
def mfa_setup(user_uid: str, request: Request, db: Session = Depends(get_db)):
    user = get_user_by_uid(db, user_uid)

    if not user:
        return HTMLResponse("User not found.", status_code=404)

    if user.registration_status == "FLAGGED":
        return HTMLResponse(
            "This account requires administrator review.", status_code=403
        )

    if user.registration_status == "ACTIVE":
        return RedirectResponse(url="/login", status_code=303)

    if not user.face_verified:
        return HTMLResponse(
            "Identity verification has not been completed.", status_code=403
        )

    if not user.mfa_secret:
        user.mfa_secret = generate_mfa_secret()
        db.commit()
        db.refresh(user)

    provisioning_uri = create_provisioning_uri(user.mfa_secret, user.email)
    qr_code = create_qr_code_base64(provisioning_uri)

    return templates.TemplateResponse(
        request=request,
        name="mfa_setup.html",
        context={
            "user_uid": user.user_uid,
            "qr_code": qr_code,
            "secret": user.mfa_secret,
            "error": None,
        },
    )


@app.post("/mfa/verify", response_class=HTMLResponse)
async def verify_mfa(
    request: Request,
    user_uid: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user_by_uid(db, user_uid)

    if not user:
        return HTMLResponse("User not found.", status_code=404)

    if not user.face_verified or user.registration_status == "FLAGGED":
        return HTMLResponse(
            "Account is not eligible for MFA activation.", status_code=403
        )

    if not user.mfa_secret:
        return HTMLResponse(
            "MFA setup has not been initialized.", status_code=400
        )

    if not verify_totp(user.mfa_secret, code):
        provisioning_uri = create_provisioning_uri(user.mfa_secret, user.email)
        qr_code = create_qr_code_base64(provisioning_uri)

        return templates.TemplateResponse(
            request=request,
            name="mfa_setup.html",
            context={
                "user_uid": user.user_uid,
                "qr_code": qr_code,
                "secret": user.mfa_secret,
                "error": "Invalid authentication code. Wait for a new code and try again.",
            },
            status_code=400,
        )

    user.mfa_enabled = True
    user.registration_status = "ACTIVE"
    db.commit()
    db.refresh(user)

   
# AUTOMATED USER PROVISIONING
# Create operational user account and mapping automatically
    operational_user_id = await provision_operational_user(db, user)

    if not operational_user_id:
        logger.error(f"Failed to provision operational user for {user.user_uid}")
        return HTMLResponse(
            """
            <html>
                <head><title>Provisioning Error</title></head>
                <body>
                    <h1>Account Setup Incomplete</h1>
                    <p>Your registration was successful, but we encountered an error setting up your operational account.</p>
                    <p>Please contact support with your User ID: <strong>{user_uid}</strong></p>
                </body>
            </html>
            """,
            status_code=500
        )

    logger.info(f"✅ User {user.user_uid} fully provisioned with operational ID: {operational_user_id}")

    return RedirectResponse(url="/login", status_code=303)


# ============================================================
# LOGIN ROUTES
# ============================================================
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None},
    )


# TODO: Create user mapping after operational user is provisioned
# For now, mapping must be created manually by admin or through automated provisioning
# Example: create_user_mapping(db, user.id, operational_user_uuid)

@app.post("/login", response_class=HTMLResponse)
def login_password(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    email = email.strip().lower()
    user = get_user_by_email(db, email)

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid email or password."},
            status_code=401,
        )

    try:
        password_valid = bcrypt.checkpw(
            password.encode("utf-8"), user.password_hash.encode("utf-8")
        )
    except Exception:
        password_valid = False

    if not password_valid:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid email or password."},
            status_code=401,
        )

    if user.registration_status == "FLAGGED":
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "This account is awaiting administrator review."
            },
            status_code=403,
        )

    if user.registration_status != "ACTIVE":
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "This account has not been activated."},
            status_code=403,
        )

    if not user.mfa_enabled:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Google Authenticator has not been configured."
            },
            status_code=403,
        )

    if not user.mfa_secret:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "MFA configuration is incomplete."},
            status_code=403,
        )

    challenge = create_login_challenge(user.user_uid)
    return RedirectResponse(
        url=f"/login/mfa/{challenge}", status_code=303
    )


@app.get("/login/mfa/{challenge_token}", response_class=HTMLResponse)
def login_mfa_page(challenge_token: str, request: Request):
    challenge = get_login_challenge(challenge_token)
    if not challenge:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login_mfa.html",
        context={"challenge_token": challenge_token, "error": None},
    )


@app.post("/login/mfa", response_class=HTMLResponse)
def login_mfa_verify(
    request: Request,
    challenge_token: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db),
):
    challenge = get_login_challenge(challenge_token)
    if not challenge:
        return RedirectResponse(url="/login", status_code=303)

    user = get_user_by_uid(db, challenge["user_uid"])
    if not user or user.registration_status != "ACTIVE":
        consume_login_challenge(challenge_token)
        return RedirectResponse(url="/login", status_code=303)

    if not verify_totp(user.mfa_secret, code):
        return templates.TemplateResponse(
            request=request,
            name="login_mfa.html",
            context={
                "challenge_token": challenge_token,
                "error": "Invalid authentication code.",
            },
            status_code=401,
        )

    consume_login_challenge(challenge_token)

    # Prevent session fixation
    request.session.clear()
    request.session["authenticated"] = True
    request.session["user_uid"] = user.user_uid
    request.session["login_time"] = int(time.time())

    return RedirectResponse(url="/dashboard", status_code=303)


# ============================================================
# DASHBOARD & LOGOUT
# ============================================================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_logged_in_user(request, db)

    if not user:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user},
    )


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# ============================================================
# ADMIN: USER MAPPING MANAGEMENT
# ============================================================

async def require_admin(user: AuthenticatedUser = Depends(verify_jwt)):
    """
    Dependency that ensures the user has admin role.
    Use this with Depends(require_admin) in admin endpoints.
    """
    if "admin" not in user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. Your roles: " + ", ".join(user.roles)
        )
    return user



@app.post("/admin/users/map")
async def map_user_to_operational(
    request: Request,
    registration_user_id: int = Form(...),
    operational_user_id: str = Form(...),  # UUID string
    db: Session = Depends(get_db),
    admin_user: AuthenticatedUser = Depends(require_admin),  # Admin authentication
    ):
    """
    Admin endpoint to map a registration user to an operational user.
    This creates the bridge between the two user systems.

    Args:
        registration_user_id: Integer ID from models.py User table
        operational_user_id: UUID from public.users table
    """
    
    # Verify registration user exists
    reg_user = db.query(User).filter(User.id == registration_user_id).first()
    if not reg_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration user {registration_user_id} not found"
        )

    # Verify operational user exists
    op_user = db.execute(
        text("SELECT id, email FROM public.users WHERE id = :user_id"),
        {"user_id": operational_user_id}
    ).fetchone()

    if not op_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operational user {operational_user_id} not found"
        )

    # Create the mapping
    success = create_user_mapping(db, registration_user_id, operational_user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mapping already exists for this registration user"
        )

    return {
        "status": "success",
        "message": f"User mapping created: registration {registration_user_id} ({reg_user.email}) -> operational {operational_user_id} ({op_user.email})"
    }


@app.get("/admin/users/mappings")
async def list_user_mappings(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: AuthenticatedUser = Depends(require_admin),  # Admin authentication
):
    """
    Admin endpoint to list all user mappings.
    Authentication: Requires admin role
    """


    mappings = db.execute(
        text("""
            SELECT
                um.registration_user_id,
                u1.email as registration_email,
                um.operational_user_id,
                u2.email as operational_email,
                um.mapped_at
            FROM public.user_mapping um
            JOIN users u1 ON um.registration_user_id = u1.id
            JOIN public.users u2 ON um.operational_user_id = u2.id
            ORDER BY um.mapped_at DESC
        """)
    ).fetchall()

    return {
        "mappings": [
            {
                "registration_user_id": m.registration_user_id,
                "registration_email": m.registration_email,
                "operational_user_id": str(m.operational_user_id),
                "operational_email": m.operational_email,
                "mapped_at": str(m.mapped_at)
            }
            for m in mappings
        ]
    }
