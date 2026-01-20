"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from upskills.core.config import get_settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # #region agent log - hypothesis F
    import json, os
    log_path = r"c:\Users\leona\source\repos\upskilling\.cursor\debug.log"
    with open(log_path, "a") as f: f.write(json.dumps({"location":"security.py:hash_password","message":"Hashing password","data":{"passwordLength":len(password)},"hypothesisId":"F"}) + "\n")
    # #endregion
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # #region agent log - hypothesis F
    import json, os
    log_path = r"c:\Users\leona\source\repos\upskilling\.cursor\debug.log"
    with open(log_path, "a") as f: f.write(json.dumps({"location":"security.py:verify_password","message":"Verifying password","data":{"passwordLength":len(plain_password),"hashLength":len(hashed_password)},"hypothesisId":"F"}) + "\n")
    # #endregion
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        # #region agent log - hypothesis F
        with open(log_path, "a") as f: f.write(json.dumps({"location":"security.py:verify_password","message":"Password verification failed","data":{"error":str(e)},"hypothesisId":"F"}) + "\n")
        # #endregion
        return False


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    settings = get_settings()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token."""
    settings = get_settings()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT token."""
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> str | None:
    """Verify a token and return the subject (user_id) if valid."""
    payload = decode_token(token)

    if payload is None:
        return None

    if payload.get("type") != token_type:
        return None

    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
        return None

    return payload.get("sub")
