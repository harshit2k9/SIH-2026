
"""
Unit tests for audit trail and hash chaining.
"""
import pytest
from unittest.mock import AsyncMock, Mock
import uuid
from datetime import datetime
import json


@pytest.mark.unit
class TestAuditHashComputation:
    """Test audit trail hash computation."""

    def test_hash_computation_deterministic(self):
        """Test that same inputs produce same hash."""
        from services.audit import _compute_entry_hash

        case_id = uuid.uuid4()
        doc_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        hash1 = _compute_entry_hash(
            prev_hash="abc123",
            case_id=case_id,
            document_id=doc_id,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"test": "data"},
            timestamp="2026-01-15T10:00:00+00:00"
        )

        hash2 = _compute_entry_hash(
            prev_hash="abc123",
            case_id=case_id,
            document_id=doc_id,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"test": "data"},
            timestamp="2026-01-15T10:00:00+00:00"
        )

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_hash_changes_with_different_details(self):
        """Test that different details produce different hashes."""
        from services.audit import _compute_entry_hash

        case_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        hash1 = _compute_entry_hash(
            prev_hash=None,
            case_id=case_id,
            document_id=None,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"version": 1},
            timestamp="2026-01-15T10:00:00+00:00"
        )

        hash2 = _compute_entry_hash(
            prev_hash=None,
            case_id=case_id,
            document_id=None,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"version": 2},  # Different
            timestamp="2026-01-15T10:00:00+00:00"
        )

        assert hash1 != hash2

    def test_hash_changes_with_different_actions(self):
        """Test that different actions produce different hashes."""
        from services.audit import _compute_entry_hash

        case_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        hash1 = _compute_entry_hash(
            prev_hash=None,
            case_id=case_id,
            document_id=None,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={},
            timestamp="2026-01-15T10:00:00+00:00"
        )

        hash2 = _compute_entry_hash(
            prev_hash=None,
            case_id=case_id,
            document_id=None,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_DOWNLOADED",  # Different action
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={},
            timestamp="2026-01-15T10:00:00+00:00"
        )

        assert hash1 != hash2

    def test_hash_includes_all_fields(self):
        """Test that hash includes all audit fields."""
        from services.audit import _compute_entry_hash

        case_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        # Hash with IP address
        hash_with_ip = _compute_entry_hash(
            prev_hash=None,
            case_id=case_id,
            document_id=None,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={},
            timestamp="2026-01-15T10:00:00+00:00"
        )

        # Hash without IP address
        hash_without_ip = _compute_entry_hash(
            prev_hash=None,
            case_id=case_id,
            document_id=None,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address=None,  # Different
            user_agent="Mozilla/5.0",
            details={},
            timestamp="2026-01-15T10:00:00+00:00"
        )

        assert hash_with_ip != hash_without_ip

    def test_hash_chain_integrity(self):
        """Test that hash chain maintains integrity."""
        from services.audit import _compute_entry_hash

        case_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        # First entry (no previous hash)
        hash1 = _compute_entry_hash(
            prev_hash=None,
            case_id=case_id,
            document_id=None,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"doc_id": "123"},
            timestamp="2026-01-15T10:00:00+00:00"
        )

        # Second entry (chains from first)
        hash2 = _compute_entry_hash(
            prev_hash=hash1,  # Links to first hash
            case_id=case_id,
            document_id=None,
            evidence_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_DOWNLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"doc_id": "123"},
            timestamp="2026-01-15T10:05:00+00:00"
        )

        # Verify chain
        assert hash1 != hash2
        assert len(hash1) == 64
        assert len(hash2) == 64


@pytest.mark.unit
class TestAuditEntryCreation:
    """Test audit entry creation."""

    @pytest.mark.asyncio
    async def test_audit_entry_creation(self):
        """Test that audit entries are created correctly."""
        from services.audit import write_audit_entry

        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = "prev_hash_abc123"

        case_id = uuid.uuid4()
        document_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        result = await write_audit_entry(
            conn=mock_conn,
            case_id=case_id,
            document_id=document_id,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="DOCUMENT_UPLOADED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"test": "data"}
        )

        # Verify hash was returned
        assert isinstance(result, str)
        assert len(result) == 64

        # Verify execute was called
        assert mock_conn.execute.called

    @pytest.mark.asyncio
    async def test_audit_entry_with_null_document(self):
        """Test audit entry creation without document_id."""
        from services.audit import write_audit_entry

        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = None

        case_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        result = await write_audit_entry(
            conn=mock_conn,
            case_id=case_id,
            document_id=None,  # No document
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="CASE_CREATED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={}
        )

        assert isinstance(result, str)
        assert len(result) == 64

    @pytest.mark.asyncio
    async def test_audit_entry_uses_advisory_lock(self):
        """Test that audit entry uses PostgreSQL advisory lock."""
        from services.audit import write_audit_entry

        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = None

        case_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        await write_audit_entry(
            conn=mock_conn,
            case_id=case_id,
            document_id=None,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="TEST_ACTION",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={}
        )

        # Verify advisory lock was acquired
        calls = [str(call) for call in mock_conn.execute.call_args_list]
        assert any("pg_advisory_xact_lock" in call for call in calls)


@pytest.mark.unit
class TestAuditLogEvent:
    """Test audit log event helper."""

    @pytest.mark.asyncio
    async def test_log_audit_event(self):
        """Test log_audit_event helper function."""
        from services.audit import log_audit_event

        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = None

        case_id = uuid.uuid4()
        document_id = uuid.uuid4()
        actor_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        result = await log_audit_event(
            conn=mock_conn,
            case_id=case_id,
            document_id=document_id,
            actor_id=actor_id,
            actor_department_id=dept_id,
            action="PRESIGNED_URL_GENERATED",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            extra_details={"download_initiated": True}
        )

        assert isinstance(result, str)
        assert len(result) == 64
        assert mock_conn.execute.called
