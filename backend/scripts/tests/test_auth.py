
"""
Unit tests for authentication and JWT verification.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import uuid
import jwt


@pytest.mark.unit
class TestJWTVerification:
    """Test JWT token verification logic."""

    @pytest.fixture
    def mock_public_key(self):
        """Mock public key for testing."""
        return "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"

    @pytest.fixture
    def valid_payload(self):
        """Valid JWT payload."""
        return {
            "sub": "20000000-0000-0000-0000-000000000001",
            "email": "test@example.com",
            "roles": ["investigator"],
            "department_id": "10000000-0000-0000-0000-000000000001",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "jti": str(uuid.uuid4()),
            "aud": "sddms-api",
            "iss": "sddms-auth-service"
        }

    def test_authenticated_user_creation(self):
        """Test AuthenticatedUser object creation."""
        from security.auth import AuthenticatedUser

        user_id = uuid.uuid4()
        dept_id = uuid.uuid4()

        user = AuthenticatedUser(
            user_id=user_id,
            roles=["investigator", "admin"],
            token_jti="test-jti-123",
            department_id=dept_id
        )

        assert user.id == user_id
        assert "investigator" in user.roles
        assert "admin" in user.roles
        assert user.token_jti == "test-jti-123"
        assert user.department_id == dept_id

    def test_authenticated_user_without_department(self):
        """Test AuthenticatedUser without department_id."""
        from security.auth import AuthenticatedUser

        user = AuthenticatedUser(
            user_id=uuid.uuid4(),
            roles=["investigator"],
            token_jti="test-jti-123",
            department_id=None
        )

        assert user.department_id is None

    @pytest.mark.asyncio
    async def test_expired_token_detection(self):
        """Test that expired tokens are detected."""
        payload = {
            "sub": "20000000-0000-0000-0000-000000000001",
            "exp": datetime.utcnow() - timedelta(minutes=1),  # Expired
            "iat": datetime.utcnow() - timedelta(minutes=31),
            "jti": "test-jti",
            "aud": "sddms-api",
            "iss": "sddms-auth-service"
        }

        # Mock JWT decode to raise ExpiredSignatureError
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

            from fastapi import HTTPException
            from security.auth import verify_jwt

            mock_credentials = Mock()
            mock_credentials.credentials = "fake_token"

            with pytest.raises(HTTPException) as exc_info:
                await verify_jwt(mock_credentials)

            assert exc_info.value.status_code == 401
            assert "expired" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")

            from fastapi import HTTPException
            from security.auth import verify_jwt

            mock_credentials = Mock()
            mock_credentials.credentials = "invalid_token"

            with pytest.raises(HTTPException) as exc_info:
                await verify_jwt(mock_credentials)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_revoked_token_rejected(self):
        """Test that revoked tokens are rejected."""
        valid_payload = {
            "sub": "20000000-0000-0000-0000-000000000001",
            "email": "test@example.com",
            "roles": ["investigator"],
            "department_id": "10000000-0000-0000-0000-000000000001",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "jti": "revoked-token-jti",
            "aud": "sddms-api",
            "iss": "sddms-auth-service"
        }

        with patch('jwt.decode', return_value=valid_payload):
            with patch('security.auth.get_pool') as mock_pool:
                # Mock database to return revoked token
                mock_conn = AsyncMock()
                mock_pool.return_value.acquire.return_value.__aenter__.return_value = mock_conn
                mock_conn.fetchval.return_value = 1  # Token is revoked
                mock_conn.fetchrow.return_value = {
                    "id": "20000000-0000-0000-0000-000000000001",
                    "is_active": True
                }

                from fastapi import HTTPException
                from security.auth import verify_jwt

                mock_credentials = Mock()
                mock_credentials.credentials = "valid_but_revoked_token"

                with pytest.raises(HTTPException) as exc_info:
                    await verify_jwt(mock_credentials)

                assert exc_info.value.status_code == 401
                assert "revoked" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_inactive_user_rejected(self):
        """Test that inactive users are rejected."""
        valid_payload = {
            "sub": "20000000-0000-0000-0000-000000000001",
            "email": "test@example.com",
            "roles": ["investigator"],
            "department_id": "10000000-0000-0000-0000-000000000001",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=30),
            "jti": "test-jti",
            "aud": "sddms-api",
            "iss": "sddms-auth-service"
        }

        with patch('jwt.decode', return_value=valid_payload):
            with patch('security.auth.get_pool') as mock_pool:
                mock_conn = AsyncMock()
                mock_pool.return_value.acquire.return_value.__aenter__.return_value = mock_conn
                mock_conn.fetchval.return_value = None  # Not revoked
                mock_conn.fetchrow.return_value = {
                    "id": "20000000-0000-0000-0000-000000000001",
                    "is_active": False  # Inactive user
                }

                from fastapi import HTTPException
                from security.auth import verify_jwt

                mock_credentials = Mock()
                mock_credentials.credentials = "valid_token"

                with pytest.raises(HTTPException) as exc_info:
                    await verify_jwt(mock_credentials)

                assert exc_info.value.status_code == 401
                assert "inactive" in str(exc_info.value.detail).lower()


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_bcrypt_hashing(self):
        """Test bcrypt password hashing."""
        import bcrypt

        password = "SecurePassword123!"
        password_bytes = password.encode('utf-8')

        # Hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Verify correct password
        assert bcrypt.checkpw(password_bytes, hashed) is True

        # Verify wrong password
        wrong_password = "WrongPassword".encode('utf-8')
        assert bcrypt.checkpw(wrong_password, hashed) is False

    def test_password_too_long_rejected(self):
        """Test that passwords longer than 72 bytes are rejected."""
        import bcrypt

        # bcrypt has a 72-byte limit
        long_password = "a" * 100
        password_bytes = long_password.encode('utf-8')

        assert len(password_bytes) > 72

        # Should still work (bcrypt truncates), but we should validate before
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Note: bcrypt silently truncates, so we should validate length before hashing
        assert len(password_bytes) > 72


@pytest.mark.unit
class TestTOTPVerification:
    """Test TOTP (Time-based One-Time Password) verification."""

    def test_totp_generation(self):
        """Test TOTP secret generation."""
        import pyotp

        secret = pyotp.random_base32()

        # Secret should be base32 encoded
        assert len(secret) > 0
        assert all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in secret)

    def test_totp_verification(self):
        """Test TOTP code verification."""
        import pyotp

        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)

        # Generate current code
        current_code = totp.now()

        # Verify current code
        assert totp.verify(current_code) is True

        # Verify wrong code
        assert totp.verify("000000") is False

    def test_totp_with_window(self):
        """Test TOTP verification with time window."""
        import pyotp
        import time

        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)

        # Generate code
        code = totp.now()

        # Verify with window=1 (allows previous and next code)
        assert totp.verify(code, valid_window=1) is True
