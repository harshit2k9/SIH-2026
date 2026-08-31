import os
from pathlib import Path
import re
import secrets
import time
import uuid

import bcrypt
from database import SessionLocal, engine
import easyocr
from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from database import close_db_pool, init_db_pool
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
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware


# ============================================================
# PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"
AADHAAR_DIR = UPLOADS_DIR / "aadhaar"
LIVE_PHOTO_DIR = UPLOADS_DIR / "live_photos"
logging.basicConfig(level=logging.INFO)
for folder in [
    TEMPLATES_DIR,
    STATIC_DIR,
    UPLOADS_DIR,
    AADHAAR_DIR,
    LIVE_PHOTO_DIR,
]:
    folder.mkdir(exist_ok=True)

# ============================================================
# FASTAPI
# ============================================================
app = FastAPI(
    title="SIH26 Secure Document Management System",
    version="1.0.0",
)

# ============================================================
# SESSION COOKIE
# ============================================================
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

SESSION_SECRET = os.getenv(
    "SIH26_SESSION_SECRET",
    "DEV-ONLY-CHANGE-THIS-BEFORE-PRODUCTION-" + secrets.token_hex(32),
)


app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="sih26_session",
    max_age=3600,
    same_site="lax",
    https_only=False,  # Set to True when deployed over HTTPS
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.example"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.on_event("startup")
async def on_startup():
    await init_db_pool()
    await ensure_bucket()


@app.on_event("shutdown")
async def on_shutdown():
    await close_db_pool()


app.include_router(documents_router)


# ============================================================
# OCR & VERHOEFF VERIFICATION SETUP
# ============================================================
ocr_reader = easyocr.Reader(["en", "hi"], gpu=False)


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
# DATABASE
# ============================================================
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# TEMPLATES / STATIC
# ============================================================
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

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
def get_user_by_uid(db: Session, user_uid: str):
    return db.query(User).filter(User.user_uid == user_uid).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


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
def verify_mfa(
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