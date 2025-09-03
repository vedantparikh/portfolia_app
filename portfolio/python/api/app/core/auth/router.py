"""
Authentication router with user registration, login, and management endpoints.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database.connection import get_db
from app.core.database.models import User, UserProfile, UserSession
from app.core.schemas.auth import (
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
    TokenValidationResponse,
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
    store_reset_token,
    validate_reset_token,
    mark_reset_token_used,
)
from app.core.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_user_profile,
    get_token_data,
    validate_refresh_token,
    get_client_ip,
    get_user_agent,
)
from app.core.email_client import send_forgot_password_email
from app.core.logging_config import (
    get_logger,
    log_api_request,
    log_security_event,
)
from app.config import settings

logger = get_logger(__name__)

router = APIRouter(tags=["authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, request: Request, db: Session = Depends(get_db)
):
    """Register a new user."""
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
            logger,
            "failed_login",
            None,  # No user ID for failed login
            client_ip,
            f"Failed login attempt for username: {user_credentials.username} from IP: {client_ip}",
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
        logger,
        "successful_login",
        str(user.id),
        client_ip,
        f"User logged in from IP: {client_ip}",
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
        logger,
        "user_logout",
        str(current_user.id),
        client_ip,
        f"User logged out from IP: {client_ip}",
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
async def forgot_password(
    password_reset: PasswordReset, request: Request, db: Session = Depends(get_db)
):
    """Request password reset."""
    client_ip = get_client_ip(request) if request else "unknown"

    # Log API request
    log_api_request(
        logger, "POST", "/forgot-password", None, client_ip, email=password_reset.email
    )

    user = db.query(User).filter(User.email == password_reset.email.lower()).first()

    if user and user.is_active:
        # Generate reset token
        reset_token = generate_reset_token()

        # Store token in Redis with expiration
        if store_reset_token(reset_token, user.id, user.email, expires_in_minutes=60):
            # Send email with reset link
            # In production, this would construct the frontend URL
            reset_url = f"{settings.FRONTEND_URL}/validate-reset-token?token={reset_token}"

            # Log password reset request
            log_security_event(
                logger,
                "password_reset_requested",
                str(user.id),
                client_ip,
                f"Password reset requested from IP: {client_ip}",
            )

            send_forgot_password_email(recipient_email=user.email, reset_url=reset_url)

            log_security_event(
                logger,
                "password_reset_sent",
                str(user.id),
                client_ip,
                f"Password reset email sent to {user.email}",
            )

            return {
                "message": "If the email exists, a password reset link has been sent",
                "reset_url": reset_url,  # For development/testing
            }
        else:
            logger.error(f"Failed to store reset token for user {user.id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process password reset request",
            )
    else:
        # Log failed password reset request
        log_security_event(
            logger,
            "password_reset_requested",
            None,
            client_ip,
            f"Password reset requested for non-existent email: {password_reset.email}",
        )

        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}


@router.get("/validate-reset-token/")
async def validate_reset_token_endpoint(
    token: str, request: Request, db: Session = Depends(get_db)
):
    """Validate password reset token and return information for frontend redirection."""
    client_ip = get_client_ip(request) if request else "unknown"

    # Log API request
    log_api_request(logger, "GET", f"/validate-reset-token/{token}", None, client_ip)

    # Validate the token
    is_valid, token_data, error_message = validate_reset_token(token)

    if is_valid:
        # Log successful token validation
        log_security_event(
            logger,
            "reset_token_validated",
            str(token_data["user_id"]),
            client_ip,
            f"Reset token validated successfully for user {token_data['user_email']}",
        )

        # Return success response with redirect information
        return TokenValidationResponse(
            is_valid=True,
            message="Token is valid. You can now reset your password.",
            redirect_url=f"{settings.API_URL}{settings.API_V1_STR}/reset-password?token={token}",
            expires_at=datetime.fromisoformat(token_data["created_at"])
            + timedelta(hours=24),
            user_email=token_data["user_email"],
        )
    else:
        # Log failed token validation
        log_security_event(
            logger,
            "reset_token_validation_failed",
            None,
            client_ip,
            f"Reset token validation failed: {error_message}",
        )

        # Return error response
        return TokenValidationResponse(
            is_valid=False,
            message=error_message,
            redirect_url=f"{settings.API_URL}{settings.API_V1_STR}/auth/forgot-password?error=invalid_token",
        )


@router.post("/reset-password")
async def reset_password(
    password_reset: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db),
):
    """Reset password using reset token."""
    client_ip = get_client_ip(request) if request else "unknown"

    # Log API request
    log_api_request(logger, "POST", "/reset-password", None, client_ip)

    # Validate reset token
    is_valid, token_data, error_message = validate_reset_token(password_reset.token)

    if not is_valid:
        log_security_event(
            logger,
            "password_reset_failed",
            None,
            client_ip,
            f"Password reset failed due to invalid token: {error_message}",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_message
        )

    try:
        # Find user
        user = db.query(User).filter(User.id == token_data["user_id"]).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found or account is deactivated",
            )

        # Update password
        user.password_hash = get_password_hash(password_reset.new_password)
        user.updated_at = datetime.utcnow()

        # Mark token as used
        mark_reset_token_used(password_reset.token)

        # Commit changes
        db.commit()

        # Log successful password reset
        log_security_event(
            logger,
            "password_reset_successful",
            str(user.id),
            client_ip,
            f"Password reset successful for user {user.email}",
        )

        return {
            "message": "Password reset successful",
            "redirect_url": f"{settings.API_URL}{settings.API_V1_STR}/auth/login?message=password_reset_successful",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reset password: {e}")

        log_security_event(
            logger,
            "password_reset_failed",
            str(token_data["user_id"]) if token_data else None,
            client_ip,
            f"Password reset failed due to system error: {str(e)}",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password",
        )


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
