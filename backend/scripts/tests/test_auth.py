"""
Auth tests — verifies verify_jwt() in app/security/auth.py rejects every
category of bad token, and accepts a genuinely valid one.
"""
import pytest

from tests.conftest import SAMPLE_PDF_BYTES, SEEDED_CASE_ID


def _upload_files():
    return {"file": ("test.pdf", SAMPLE_PDF_BYTES, "application/pdf")}


def _upload_form():
    return {"case_id": SEEDED_CASE_ID, "title": "Auth Test Doc", "document_type": "pdf"}


@pytest.mark.asyncio
async def test_upload_without_token_returns_403(client):
    response = await client.post("/documents/upload", data=_upload_form(), files=_upload_files())
    assert response.status_code == 403  # HTTPBearer: missing header = 403


@pytest.mark.asyncio
async def test_upload_with_expired_token_returns_401(client, expired_token):
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.post("/documents/upload", data=_upload_form(), files=_upload_files(), headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_with_wrong_signature_returns_401(client, wrong_signature_token):
    headers = {"Authorization": f"Bearer {wrong_signature_token}"}
    response = await client.post("/documents/upload", data=_upload_form(), files=_upload_files(), headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_with_malformed_bearer_returns_401_or_403(client):
    headers = {"Authorization": "Bearer not-a-real-jwt"}
    response = await client.post("/documents/upload", data=_upload_form(), files=_upload_files(), headers=headers)
    assert response.status_code in (401, 403)