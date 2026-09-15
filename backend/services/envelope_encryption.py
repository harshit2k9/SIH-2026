import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from services.vault_kms import vault_kms


class EnvelopeEncryption:
    """
    Envelope encryption for DMS documents.

    Document data is encrypted locally with a random AES-256 DEK.
    The DEK is then protected by Vault Transit.
    """

    def encrypt(self, plaintext: bytes) -> tuple[bytes, str]:
        # 1. Generate a random 256-bit Data Encryption Key (DEK)
        dek = AESGCM.generate_key(bit_length=256)

        # 2. Generate a random 96-bit nonce
        nonce = os.urandom(12)

        # 3. Encrypt the document with AES-256-GCM
        aesgcm = AESGCM(dek)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Store nonce together with ciphertext
        encrypted_document = nonce + ciphertext

        # 4. Send the DEK to Vault Transit
        wrapped_dek = vault_kms.encrypt(dek)

        return encrypted_document, wrapped_dek

    def decrypt(self, encrypted_document: bytes, wrapped_dek: str) -> bytes:
        # 1. Recover the DEK from Vault
        dek = vault_kms.decrypt(wrapped_dek)

        # 2. Extract the nonce
        nonce = encrypted_document[:12]
        ciphertext = encrypted_document[12:]

        # 3. Decrypt using AES-256-GCM
        aesgcm = AESGCM(dek)

        return aesgcm.decrypt(nonce, ciphertext, None)


envelope_encryption = EnvelopeEncryption()