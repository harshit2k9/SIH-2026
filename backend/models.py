from database import Base
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    String,
)

# ============================================================
# NORMAL USERS
# ============================================================


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    user_uid = Column(String, unique=True, index=True, nullable=False)

    full_name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)

    phone = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)

    aadhaar_number = Column(String, nullable=False)

    aadhaar_image = Column(String, nullable=False)

    live_photo = Column(String, nullable=False)

    # --------------------------------------------------------
    # FACE VERIFICATION & REVIEW STATUS
    # --------------------------------------------------------

    face_verified = Column(Boolean, default=False)

    face_similarity_score = Column(Float, nullable=True)

    face_match_threshold = Column(Float, nullable=True)

    flag_reason = Column(String, nullable=True)

    # Statuses: NOT_REQUIRED, PENDING, APPROVED, REJECTED
    admin_review_status = Column(String, default="NOT_REQUIRED")

    # --------------------------------------------------------
    # ACCOUNT STATUS
    # Statuses: PENDING, MFA_PENDING, ACTIVE, FLAGGED, REJECTED
    # --------------------------------------------------------

    registration_status = Column(String, default="PENDING")

    # --------------------------------------------------------
    # MFA
    # --------------------------------------------------------

    mfa_secret = Column(String, nullable=True)

    mfa_enabled = Column(Boolean, default=False)


# ============================================================
# ADMIN USERS
# ============================================================


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
'''
class OperationalUser(Base):
    """Maps to public.users in SIH_DATABASE.sql"""
    __tablename__ = "operational_users"
    
    id = Column(UUID, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    badge_number = Column(String, unique=True)
    security_clearance_level = Column(Integer)
    is_active = Column(Boolean, default=True)
    
    # Link to registration user
    registration_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
'''