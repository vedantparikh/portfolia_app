"""
Authentication utilities for password hashing, JWT tokens, and security.
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token configuration
ALGORITHM = settings.JWT_ALGORITHM
SECRET_KEY = settings.JWT_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type_from_payload = payload.get("type")

        if token_type_from_payload != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def create_tokens(user_id: int, email: str, username: str) -> dict:
    """Create both access and refresh tokens for a user."""
    data = {"sub": str(user_id), "email": email, "username": username}

    access_token = create_access_token(data=data)
    refresh_token = create_refresh_token(data=data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
    }


def generate_verification_token() -> str:
    """Generate a random verification token."""
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Generate a random password reset token."""
    return secrets.token_urlsafe(32)


def generate_two_factor_code() -> str:
    """Generate a 6-digit two-factor authentication code."""
    return "".join(secrets.choice(string.digits) for _ in range(6))


def generate_session_id() -> str:
    """Generate a random session ID."""
    return secrets.token_urlsafe(32)


def is_password_strong(password: str) -> bool:
    """Check if password meets security requirements."""
    if len(password) < 8:
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    return has_upper and has_lower and has_digit and has_special


def sanitize_username(username: str) -> str:
    """Sanitize username for safe storage."""
    return username.lower().strip()


def validate_email_format(email: str) -> bool:
    """Basic email format validation."""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def rate_limit_key(identifier: str, action: str) -> str:
    """Generate rate limiting key."""
    return f"rate_limit:{action}:{identifier}"


def is_rate_limited(
    identifier: str, action: str, max_attempts: int, window_seconds: int
) -> bool:
    """Check if an action is rate limited."""
    # This would typically integrate with Redis for actual rate limiting
    # For now, return False (not rate limited)
    return False


def log_security_event(
    user_id: Optional[int],
    event_type: str,
    details: str,
    ip_address: Optional[str] = None,
):
    """Log security-related events."""
    # This would typically integrate with a logging system
    # For now, just print to console
    timestamp = datetime.utcnow().isoformat()
    print(
        f"[SECURITY] {timestamp} - User: {user_id}, Event: {event_type}, Details: {details}, IP: {ip_address}"
    )


def validate_token_expiry(token_exp: Union[int, datetime]) -> bool:
    """Validate if token is expired."""
    if isinstance(token_exp, int):
        exp_datetime = datetime.fromtimestamp(token_exp)
    else:
        exp_datetime = token_exp

    return datetime.utcnow() < exp_datetime


def get_token_expiry_time(token_type: str = "access") -> datetime:
    """Get expiry time for a token type."""
    if token_type == "access":
        return datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh":
        return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        raise ValueError(f"Unknown token type: {token_type}")
