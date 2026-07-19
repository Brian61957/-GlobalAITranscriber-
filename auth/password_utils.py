import hashlib
import os


def hash_password(password: str, salt: bytes = None):
    """
    Returns (hash_hex, salt_hex). Uses PBKDF2-HMAC-SHA256, stdlib only.
    """
    if salt is None:
        salt = os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )

    return digest.hex(), salt.hex()


def verify_password(password: str, hash_hex: str, salt_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)

    check_hash, _ = hash_password(password, salt)

    return check_hash == hash_hex
