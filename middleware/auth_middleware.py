"""Authentication middleware and token management utilities.

Exposes password hashing (bcrypt), token creation and decoding (JWT), and the
FastAPI dependency function to validate requests.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

# Setup password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup OAuth2 token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt.

    Args:
        password: The plain text password.

    Returns:
        The hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against its bcrypt hash.

    Args:
        plain_password: The raw password input.
        hashed_password: The stored hashed password.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token.

    Args:
        data: The payload dictionary containing user info (uid, phone, plan).
        expires_delta: Optional custom expiry duration. Defaults to 7 days.

    Returns:
        A signed JWT token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency to authenticate requests and extract user payload.

    Decodes JWT token, extracts claims, attaches them to request.state,
    and returns the payload.

    Args:
        request: The active FastAPI Request object.
        token: The bearer token provided in the Authorization header.

    Returns:
        dict: The user payload (uid, phone, plan) from the token.

    Raises:
        HTTPException: If the token is missing, invalid, or expired.
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
        uid: str = payload.get("uid")
        phone: str = payload.get("phone")
        plan: str = payload.get("plan")

        if uid is None or phone is None or plan is None:
            raise credentials_exception

        # Attach claims to request.state
        request.state.uid = uid
        request.state.phone = phone
        request.state.plan = plan

        return {"uid": uid, "phone": phone, "plan": plan}

    except JWTError:
        raise credentials_exception
