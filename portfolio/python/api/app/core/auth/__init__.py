"""
Authentication package for Portfolia application.
"""

from .dependencies import *
from .router import router as auth_router
from .utils import *

__all__ = [
    "auth_router",
    # Utils
    "verify_password",
    "get_password_hash",
    "create_tokens",
    "generate_verification_token",
    "generate_reset_token",
    "generate_two_factor_code",
    "is_password_strong",
    "sanitize_username",
    "store_verification_token",
    "validate_verification_token",
    "mark_verification_token_used",
    "store_reset_token",
    "validate_reset_token",
    "mark_reset_token_used",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_current_user_profile",
    "require_permission",
    "require_admin",
]
