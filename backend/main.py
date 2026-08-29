import os
from pathlib import Path
import re
import secrets
import time
import uuid

import bcrypt
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
PAN_DIR = UPLOADS_DIR / "pan"
LIVE_PHOTO_DIR = UPLOADS_DIR / "live_photos"

for folder in [
    TEMPLATES_DIR,
    STATIC_DIR,
    UPLOADS_DIR,
    AADHAAR_DIR,
    PAN_DIR,
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
)

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
    pan_number: str = Form(...),
    liveness_token: str = Form(...),
    aadhaar_image: UploadFile = File(...),
    pan_image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip()
    aadhaar_number = aadhaar_number.strip()
    pan_number = pan_number.strip().upper()

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

    if not aadhaar_number.isdigit() or len(aadhaar_number) != 12:
        return registration_error(
            request, "Aadhaar number must contain exactly 12 digits."
        )

    pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    if not re.match(pan_pattern, pan_number):
        return registration_error(request, "Invalid PAN format.")

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
        pan_bytes, pan_extension = await read_image_upload(pan_image)
    except ValueError as error:
        return registration_error(request, str(error))

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
    pan_path = None
    live_photo_path = None

    try:
        aadhaar_path = save_image_bytes(
            aadhaar_bytes, AADHAAR_DIR, user_uid, aadhaar_extension
        )
        pan_path = save_image_bytes(
            pan_bytes, PAN_DIR, user_uid, pan_extension
        )
        live_photo_path = save_image_bytes(
            live_photo_bytes, LIVE_PHOTO_DIR, user_uid, ".jpg"
        )
    except Exception as error:
        print("FILE ERROR:", repr(error))
        delete_file(aadhaar_path)
        delete_file(pan_path)
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
        pan_number=pan_number,
        aadhaar_image=aadhaar_path,
        pan_image=pan_path,
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
        delete_file(pan_path)
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
