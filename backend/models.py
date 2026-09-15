import uuid
from database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

# ============================================================
# USERS & ACCESS MANAGEMENT
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    badge_number = Column(String, unique=True, nullable=True, index=True)
    security_clearance_level = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    departments = relationship("UserDepartment", back_populates="user")
    mapping = relationship("UserMapping", back_populates="user", uselist=False)


class UserMapping(Base):
    """Maps legacy/registration integer IDs to operational UUID users."""
    __tablename__ = "user_mapping"

    registration_user_id = Column(Integer, primary_key=True)
    operational_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    mapped_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="mapping")


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    permissions = Column(JSONB, nullable=True)


class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserDepartment(Base):
    __tablename__ = "user_departments"
    __table_args__ = (
        UniqueConstraint("user_id", "department_id", "role_id", name="user_departments_user_id_department_id_role_id_key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    is_primary = Column(Boolean, default=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="departments")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token_jti = Column(String, nullable=False, unique=True, index=True)
    revoked_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)


# ============================================================
# CASES & COURT PROCEEDINGS
# ============================================================

class Case(Base):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    classification_level = Column(Integer, nullable=True)
    status = Column(String, nullable=False)
    primary_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    lead_investigator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CaseStageHistory(Base):
    __tablename__ = "case_stage_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    previous_stage = Column(String, nullable=True)
    new_stage = Column(String, nullable=False)
    changed_by_order_id = Column(UUID(as_uuid=True), ForeignKey("court_orders.id"), nullable=True)
    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    remarks = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())


class CourtBench(Base):
    __tablename__ = "court_benches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    bench_name = Column(String, nullable=False)
    bench_type = Column(String, nullable=False)
    presiding_judge_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)


class CourtHearing(Base):
    __tablename__ = "court_hearings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    bench_id = Column(UUID(as_uuid=True), ForeignKey("court_benches.id"), nullable=False)
    hearing_date = Column(DateTime(timezone=True), nullable=False)
    hearing_purpose = Column(String, nullable=False)
    status = Column(String, nullable=False)
    adjournment_reason = Column(Text, nullable=True)
    next_hearing_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CourtOrder(Base):
    __tablename__ = "court_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    hearing_id = Column(UUID(as_uuid=True), ForeignKey("court_hearings.id"), nullable=True)
    order_number = Column(String, nullable=False, unique=True)
    order_type = Column(String, nullable=False)
    order_summary = Column(Text, nullable=True)
    issuing_judge_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), unique=True, nullable=True)
    effective_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    enforcement_status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrderSheet(Base):
    __tablename__ = "order_sheets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    hearing_id = Column(UUID(as_uuid=True), ForeignKey("court_hearings.id"), unique=True, nullable=False)
    order_sheet_number = Column(String, nullable=False, unique=True)
    proceeding_summary = Column(Text, nullable=True)
    advocates_present = Column(JSONB, nullable=True)
    accused_presence_status = Column(String, nullable=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    recorded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WarrantAndSummon(Base):
    __tablename__ = "warrants_and_summons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    court_order_id = Column(UUID(as_uuid=True), ForeignKey("court_orders.id"), nullable=False)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    notice_type = Column(String, nullable=False)
    target_person_details = Column(JSONB, nullable=True)
    assigned_police_station_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    executing_officer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    execution_status = Column(String, nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# EVIDENCE & DOCUMENTS
# ============================================================

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    evidence_item_id = Column(UUID(as_uuid=True), ForeignKey("evidence_items.id"), nullable=True)
    document_number = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    document_type = Column(String, nullable=False)
    confidentiality_level = Column(Integer, nullable=True)
    current_version = Column(Integer, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_locked = Column(Boolean, default=False)


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    storage_uri = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    file_mime_type = Column(String, nullable=True)
    sha256_checksum = Column(String, nullable=True)
    kms_key_id = Column(String, nullable=True)
    wrapped_dek = Column(Text, nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class DocumentAIMetadata(Base):
    __tablename__ = "document_ai_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"), unique=True, nullable=False)
    ocr_extracted_text = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    extracted_entities = Column(JSONB, nullable=True)
    vector_embedding_id = Column(String, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)


class DigitalSignature(Base):
    __tablename__ = "digital_signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id"), nullable=False)
    signer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    signer_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    signature_hash = Column(Text, nullable=False)
    cert_serial_number = Column(String, nullable=True)
    timestamp_seal = Column(Text, nullable=True)
    signed_at = Column(DateTime(timezone=True), server_default=func.now())


class EvidenceProvider(Base):
    __tablename__ = "evidence_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_type = Column(String, nullable=False)
    full_name_or_org = Column(String, nullable=False)
    contact_info = Column(JSONB, nullable=True)
    identification_number = Column(String, nullable=True)
    clearance_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    evidence_number = Column(String, nullable=False, unique=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("evidence_providers.id"), nullable=True)
    title = Column(String, nullable=False)
    evidence_type = Column(String, nullable=False)
    storage_location = Column(String, nullable=True)
    current_status = Column(String, nullable=False)
    seized_at = Column(DateTime(timezone=True), nullable=True)
    seized_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


class EvidenceCustodyTransfer(Base):
    __tablename__ = "evidence_custody_transfers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_item_id = Column(UUID(as_uuid=True), ForeignKey("evidence_items.id"), nullable=False)
    released_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    received_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    purpose = Column(Text, nullable=True)
    transfer_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    physical_condition_notes = Column(Text, nullable=True)


class ChainOfCustodyLog(Base):
    __tablename__ = "chain_of_custody_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence_items.id"), nullable=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    actor_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    action = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    previous_log_hash = Column(String, nullable=True)
    current_log_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InterDepartmentShare(Base):
    __tablename__ = "inter_department_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    source_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    target_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    granted_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    access_level = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False)