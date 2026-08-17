"""
FraudShield AI — Authentication Middleware
============================================
Provides bcrypt password hashing, JWT token creation/decoding, and the
FastAPI dependency function that validates incoming requests.

Token payload schema::

    {
        "uid":   "<uuid4>",
        "phone": "<phone_number>",
        "plan":  "free | pro | family | business",
        "exp":   <unix_timestamp>
    }
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# JWT configuration
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY: str = os.getenv(
    "SECRET_KEY", "fallback-secret-key-change-me-in-production"
)
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS: int = 7
REFRESH_TOKEN_EXPIRE_DAYS: int = 30


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        password: The raw password string.

    Returns:
        The bcrypt hash string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash.

    Args:
        plain_password:   The raw password input from the user.
        hashed_password:  The stored hash from the database.

    Returns:
        ``True`` if the password matches, ``False`` otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        data:           Payload dictionary (must include ``uid``, ``phone``, ``plan``).
        expires_delta:  Optional custom expiry duration.  Defaults to 7 days.

    Returns:
        A signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a longer-lived refresh token (30 days).

    Args:
        data: Payload dictionary (must include ``uid``).

    Returns:
        A signed JWT string.
    """
    return create_access_token(
        data,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


# ---------------------------------------------------------------------------
# FastAPI dependency — extract and validate current user from JWT
# ---------------------------------------------------------------------------
async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
) -> dict:
    """FastAPI dependency that authenticates requests via JWT.

    Decodes the bearer token, extracts claims, attaches them to
    ``request.state``, and returns the payload dictionary.

    Args:
        request: The active FastAPI ``Request`` object.
        token:   Bearer token from the ``Authorization`` header.

    Returns:
        A dict with ``uid``, ``phone``, and ``plan`` keys.

    Raises:
        HTTPException: 401 if the token is missing, invalid, or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "success": False,
            "error": "Could not validate credentials or token has expired",
            "code": "UNAUTHORIZED",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: Optional[str] = payload.get("uid")
        phone: Optional[str] = payload.get("phone")
        plan: Optional[str] = payload.get("plan")

        if uid is None or phone is None or plan is None:
            raise credentials_exception

        # Attach claims to request.state for downstream access
        request.state.uid = uid
        request.state.phone = phone
        request.state.plan = plan

        return {"uid": uid, "phone": phone, "plan": plan}

    except JWTError:
        raise credentials_exception
