from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
)

from database import Base


# ============================================================
# NORMAL USERS
# ============================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_uid = Column(
        String,
        unique=True,
        index=True
    )

    full_name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    phone = Column(
        String,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    aadhaar_number = Column(
        String,
        nullable=False
    )

    pan_number = Column(
        String,
        nullable=False
    )

    aadhaar_image = Column(
        String,
        nullable=False
    )

    # --------------------------------------------------------
    # Kept temporarily for compatibility with old SQLite DB.
    #
    # New registrations DO NOT upload PAN images.
    # --------------------------------------------------------

    pan_image = Column(
        String,
        nullable=True
    )

    live_photo = Column(
        String,
        nullable=False
    )

    # --------------------------------------------------------
    # FACE VERIFICATION
    # --------------------------------------------------------

    face_verified = Column(
        Boolean,
        default=False
    )

    face_similarity_score = Column(
        Float,
        nullable=True
    )

    face_match_threshold = Column(
        Float,
        nullable=True
    )

    flag_reason = Column(
        String,
        nullable=True
    )

    # NOT_REQUIRED
    # PENDING
    # APPROVED
    # REJECTED

    admin_review_status = Column(
        String,
        default="NOT_REQUIRED"
    )

    # --------------------------------------------------------
    # ACCOUNT STATUS
    #
    # PENDING
    # MFA_PENDING
    # ACTIVE
    # FLAGGED
    # REJECTED
    # --------------------------------------------------------

    registration_status = Column(
        String,
        default="PENDING"
    )

    # --------------------------------------------------------
    # MFA
    # --------------------------------------------------------

    mfa_secret = Column(
        String,
        nullable=True
    )

    mfa_enabled = Column(
        Boolean,
        default=False
    )


# ============================================================
# ADMIN USERS
# ============================================================

class Admin(Base):

    __tablename__ = "admins"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )