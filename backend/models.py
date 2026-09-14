import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class User(Base):
    __tablename__ = "registration_users" 
    
    # Using UUID to match the rest of the system's design
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_uid = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    aadhaar_number = Column(String, nullable=False)
    aadhaar_image = Column(String, nullable=False)
    live_photo = Column(String, nullable=False)
    
    # Face Verification & Review Status
    face_verified = Column(Boolean, default=False)
    face_similarity_score = Column(Float, nullable=True)
    face_match_threshold = Column(Float, nullable=True)
    flag_reason = Column(String, nullable=True)
    admin_review_status = Column(String, default="NOT_REQUIRED")
    
    # Account Status: PENDING, MFA_PENDING, ACTIVE, FLAGGED, REJECTED
    registration_status = Column(String, default="PENDING")
    
    # MFA
    mfa_secret = Column(String, nullable=True)
    mfa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

"""
class OperationalUser(Base):
    """#Maps to police/operational staff with clearance levels.
"""
    __tablename__ = "operational_users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    badge_number = Column(String, unique=True, nullable=False)
    security_clearance_level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Optional link to the base registration user if they have a login
    registration_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)"""

class User(Base):
    __tablename__ = "registration_users"
    # ... existing fields ...
    intended_role = Column(String, default="citizen")  # NEW