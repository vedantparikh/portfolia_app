"""
Authentication router with user registration, login, and management endpoints.
"""

import time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database.connection import get_db
from app.core.database.models import User, UserProfile, UserSession
from app.core.auth.schemas import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserProfileResponse,
    Token,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification,
    TwoFactorSetup,
    TwoFactorVerify,
)
from app.core.auth.utils import (
    get_password_hash,
    verify_password,
    create_tokens,
    create_refresh_token,
    generate_reset_token,
    generate_session_id,
    is_password_strong,
    sanitize_username,
)
from app.core.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_current_user_profile,
    get_token_data,
    validate_refresh_token,
    get_client_ip,
    get_user_agent,
)
from app.core.logging_config import (
    get_logger,
    log_api_request,
    log_security_event,
)

logger = get_logger(__name__)

router = APIRouter(tags=["authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, request: Request, db: Session = Depends(get_db)
):
    """Register a new user."""
    start_time = time.time()
    client_ip = get_client_ip(request) if request else "unknown"
    user_agent = get_user_agent(request) if request else "unknown"

    # Log API request
    log_api_request(
        logger,
        "POST",
        "/register",
        None,
        client_ip,
        email=user_data.email,
        username=user_data.username,
        user_agent=user_agent,
    )

    logger.info(
        f"👤 User registration initiated | Email: {user_data.email} | Username: {user_data.username} | IP: {client_ip}"
    )

    try:
        # Check if user already exists
        logger.debug(
            f"Checking for existing user | Email: {user_data.email} | Username: {user_data.username}"
        )
        existing_user = (
            db.query(User)
            .filter(
                (User.email == user_data.email) | (User.username == user_data.username)
            )
            .first()
        )

        if existing_user:
            if existing_user.email == user_data.email:
                logger.warning(
                    f"🚫 Registration failed - Email already registered | Email: {user_data.email} | IP: {client_ip}"
                )
                log_security_event(
                    logger,
                    "REGISTRATION_ATTEMPT_DUPLICATE_EMAIL",
                    None,
                    client_ip,
                    f"Email: {user_data.email}",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            else:
                logger.warning(
                    f"🚫 Registration failed - Username already taken | Username: {user_data.username} | IP: {client_ip}"
                )
                log_security_event(
                    logger,
                    "REGISTRATION_ATTEMPT_DUPLICATE_USERNAME",
                    None,
                    client_ip,
                    f"Username: {user_data.username}",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

        # Validate password strength
        logger.debug(
            f"Validating password strength for user | Username: {user_data.username}"
        )
        if not is_password_strong(user_data.password):
            logger.warning(
                f"🚫 Registration failed - Weak password | Username: {user_data.username} | IP: {client_ip}"
            )
            log_security_event(
                logger,
                "REGISTRATION_ATTEMPT_WEAK_PASSWORD",
                None,
                client_ip,
                f"Username: {user_data.username}",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet security requirements",
            )

        # Create user
        logger.debug(
            f"Creating new user | Username: {user_data.username} | Email: {user_data.email}"
        )
        hashed_password = get_password_hash(user_data.password)
        sanitized_username = sanitize_username(user_data.username)

        new_user = User(
            email=user_data.email.lower(),
            username=sanitized_username,
            password_hash=hashed_password,
            is_active=True,
            is_verified=False,  # Email verification required
        )

        db.add(new_user)
        db.flush()  # Get the user ID

        # Create user profile
        user_profile = UserProfile(
            user_id=new_user.id,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            timezone="UTC",
            currency_preference="USD",
            language_preference="en",
        )

        db.add(user_profile)
        db.commit()
        db.refresh(new_user)

        # Log security event
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        log_security_event(
            logger,
            "user_registration",
            str(new_user.id),
            client_ip,
            f"New user registered from IP: {client_ip}, UA: {user_agent}",
        )

        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User registration failed"
        )


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin, request: Request, db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens."""
    # Find user by username
    user = (
        db.query(User)
        .filter(User.username == user_credentials.username.lower())
        .first()
    )

    if not user or not verify_password(user_credentials.password, user.password_hash):
        # Log failed login attempt
        client_ip = get_client_ip(request)
        log_security_event(
            None,
            "failed_login",
            f"Failed login attempt for username: {user_credentials.username} from IP: {client_ip}",
            client_ip,
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated"
        )

    # Create session
    session_id = generate_session_id()
    refresh_token = create_refresh_token(
        {"sub": str(user.id), "email": user.email, "username": user.username}
    )
    user_session = UserSession(
        user_id=user.id,
        session_id=session_id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )

    db.add(user_session)
    db.commit()

    # Generate tokens
    tokens = create_tokens(user.id, user.email, user.username)

    # Log successful login
    client_ip = get_client_ip(request)
    log_security_event(
        user.id, "successful_login", f"User logged in from IP: {client_ip}", client_ip
    )

    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token_data: dict = Depends(validate_refresh_token),
    db: Session = Depends(get_db),
):
    """Refresh access token using refresh token."""
    user_id = int(refresh_token_data.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Generate new tokens
    tokens = create_tokens(user.id, user.email, user.username)

    return tokens


@router.post("/logout")
async def logout_user(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout user and invalidate session."""
    # Invalidate current session
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            token_data = get_token_data(token)
            # Mark session as expired
            session = (
                db.query(UserSession)
                .filter(
                    UserSession.user_id == current_user.id,
                    UserSession.expires_at > datetime.utcnow(),
                )
                .first()
            )

            if session:
                session.expires_at = datetime.utcnow()
                db.commit()
        except:
            pass

    # Log logout event
    client_ip = get_client_ip(request)
    log_security_event(
        current_user.id,
        "user_logout",
        f"User logged out from IP: {client_ip}",
        client_ip,
    )

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_current_user_profile_info(
    current_user_profile: UserProfile = Depends(get_current_user_profile),
):
    """Get current user's profile information."""
    return current_user_profile


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    # Update user profile
    profile = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    )
    if profile:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        profile.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change user password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Validate new password strength
    if not is_password_strong(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password does not meet security requirements",
        )

    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()

    db.commit()

    # Log password change
    log_security_event(
        logger, "password_changed", str(current_user.id), None, "User changed password"
    )

    return {"message": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(password_reset: PasswordReset, db: Session = Depends(get_db)):
    """Request password reset."""
    user = db.query(User).filter(User.email == password_reset.email.lower()).first()

    if user and user.is_active:
        # Generate reset token (in production, this would be sent via email)
        reset_token = generate_reset_token()
        # Store reset token in database or Redis with expiration

        # Log password reset request
        log_security_event(
            logger,
            "password_reset_requested",
            str(user.id),
            None,
            "Password reset requested",
        )

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    password_reset: PasswordResetConfirm, db: Session = Depends(get_db)
):
    """Reset password using reset token."""
    # Validate reset token (in production, this would check against stored token)
    # For now, we'll just validate the token format

    if len(password_reset.token) < 32:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
        )

    # Find user by reset token (in production, this would query the database)
    # For now, we'll return a generic message

    return {"message": "Password reset successful"}


@router.post("/verify-email")
async def verify_email(verification: EmailVerification, db: Session = Depends(get_db)):
    """Verify user email address."""
    # In production, this would validate the verification token
    # and mark the user as verified

    return {"message": "Email verification successful"}


@router.post("/resend-verification")
async def resend_verification(current_user: User = Depends(get_current_user)):
    """Resend email verification."""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
        )

    # In production, this would generate a new verification token
    # and send it via email

    return {"message": "Verification email sent"}


@router.post("/2fa/setup")
async def setup_two_factor(
    two_factor_data: TwoFactorSetup,
    current_user: User = Depends(get_current_verified_user),
):
    """Setup two-factor authentication."""
    # In production, this would generate a QR code for TOTP apps
    # and store the secret in the database

    if two_factor_data.enable:
        # Generate 2FA secret and QR code
        return {"message": "Two-factor authentication setup initiated"}
    else:
        # Disable 2FA
        return {"message": "Two-factor authentication disabled"}


@router.post("/2fa/verify")
async def verify_two_factor(
    two_factor_data: TwoFactorVerify,
    current_user: User = Depends(get_current_verified_user),
):
    """Verify two-factor authentication code."""
    # In production, this would validate the TOTP code
    # against the stored secret

    # For now, we'll just validate the code format
    if len(two_factor_data.code) != 6 or not two_factor_data.code.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
        )

    return {"message": "Two-factor authentication verified"}


@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Delete current user account."""
    # In production, this would require additional confirmation
    # and might implement soft delete instead of hard delete

    # Mark user as inactive
    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()

    # Expire all sessions
    db.query(UserSession).filter(UserSession.user_id == current_user.id).update(
        {UserSession.expires_at: datetime.utcnow()}
    )

    db.commit()

    # Log account deletion
    log_security_event(
        logger, "account_deleted", str(current_user.id), None, "User account deleted"
    )

    return {"message": "Account deleted successfully"}
