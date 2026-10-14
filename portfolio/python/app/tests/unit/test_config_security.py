"""Startup refuses insecure configuration outside local development."""

import pytest

from config import Settings

GOOD = {
    "ENVIRONMENT": "production",
    "TESTING": False,
    "SECRET_KEY": "s" * 40,
    "JWT_SECRET_KEY": "j" * 40,
    "POSTGRES_PASSWORD": "a-real-db-password",
    "REDIS_PASSWORD": "a-real-redis-password",
    "ALLOWED_ORIGINS": ["https://portfolia.example.com"],
}


def make_settings(**overrides):
    return Settings(**{**GOOD, **overrides})


def test_secure_production_config_passes():
    make_settings().validate_secrets()


@pytest.mark.parametrize(
    "override",
    [
        {"JWT_SECRET_KEY": "your-jwt-secret-key-change-in-production"},
        {"SECRET_KEY": "short"},
        {"POSTGRES_PASSWORD": "password"},
        {"REDIS_PASSWORD": ""},
        {"ALLOWED_ORIGINS": ["*"]},
    ],
)
def test_insecure_production_config_is_rejected(override):
    with pytest.raises(RuntimeError):
        make_settings(**override).validate_secrets()


def test_development_allows_placeholders():
    make_settings(ENVIRONMENT="development", REDIS_PASSWORD="").validate_secrets()
