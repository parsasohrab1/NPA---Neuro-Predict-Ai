from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
import base64
import hashlib

from .config import settings


def _derive_fernet_key(secret: str) -> bytes:
    """
    Derive a 32-byte key from SECRET_KEY using SHA-256 and encode urlsafe for Fernet.
    """
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    key = _derive_fernet_key(settings.SECRET_KEY)
    return Fernet(key)


def encrypt_text(plaintext: str) -> str:
    f = get_fernet()
    token = f.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_text(ciphertext: str) -> Optional[str]:
    f = get_fernet()
    try:
        data = f.decrypt(ciphertext.encode("utf-8"))
        return data.decode("utf-8")
    except InvalidToken:
        return None


