import base64
import logging

import hvac

from config import settings

logger = logging.getLogger(__name__)


class VaultKMS:
    """Vault Transit-based KMS for document encryption."""

    def __init__(self):
        self.client = hvac.Client(
            url=settings.VAULT_ADDR,
            token=settings.VAULT_TOKEN,
        )
        self.key_name = settings.VAULT_KMS_KEY_NAME

    def is_available(self) -> bool:
        """Check whether Vault is reachable and authenticated."""
        try:
            return self.client.is_authenticated()
        except Exception as exc:
            logger.error("Vault connection check failed: %s", exc)
            return False

    def encrypt(self, plaintext: bytes) -> str:
        """Encrypt bytes using the Vault Transit key."""
        plaintext_b64 = base64.b64encode(plaintext).decode("utf-8")

        response = self.client.secrets.transit.encrypt_data(
            name=self.key_name,
            plaintext=plaintext_b64,
        )

        return response["data"]["ciphertext"]

    def decrypt(self, ciphertext: str) -> bytes:
        """Decrypt Vault Transit ciphertext back to bytes."""
        response = self.client.secrets.transit.decrypt_data(
            name=self.key_name,
            ciphertext=ciphertext,
        )

        plaintext_b64 = response["data"]["plaintext"]
        return base64.b64decode(plaintext_b64)


vault_kms = VaultKMS()