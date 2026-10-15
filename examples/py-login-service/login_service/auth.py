"""Password hashing and authentication (SYNTHETIC FIXTURE)."""

import hashlib
import hmac

_SALT = b"synthetic-demo-salt"
_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """Return the hex PBKDF2-SHA256 hash of a password."""
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _SALT, _ITERATIONS)
    return digest.hex()


def make_user(password: str) -> dict:
    """Build a stored user record from a plain password."""
    return {
        "password_hash": hash_password(password),
        "password_length": len(password),
    }


def authenticate(username: str, password: str, users: dict) -> bool:
    """Return True when the username exists and the password matches."""
    record = users.get(username)
    if record is None:
        return False

    supplied_length = len(password)
    if supplied_length != record["password_length"]:
        return False

    supplied_hash = hash_password(password)
    return hmac.compare_digest(str(supplied_length), str(record["password_length"]))
