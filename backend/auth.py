"""Authentication utilities — password hashing, JWT, and the auth dependency."""

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models.user import User

# Static salt (kept for backwards compatibility with the existing demo database).
SALT = "adaptivelearn_salt"


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a salt."""
    return hashlib.sha256(f"{SALT}{password}".encode()).hexdigest()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash (constant-time comparison)."""
    return hmac.compare_digest(hash_password(plain), hashed)


def create_token(user_id: int, email: str) -> str:
    """Issue a signed JWT for the given user."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {"sub": str(user_id), "email": email, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """Decode and verify a JWT, returning the payload or None if invalid."""
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency that resolves the logged-in student from the
    `Authorization: Bearer <token>` request header.

    NOTE: this must be a real dependency with an annotated `Header(...)`
    parameter. Using `Depends(lambda request: ...)` makes FastAPI treat
    `request` as a required *query* parameter, which 422s every request.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization[7:] if authorization.startswith("Bearer ") else authorization
    token = token.strip()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token subject")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
