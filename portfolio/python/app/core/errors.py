"""
Errors whose message is written for the user.

Raise `DomainError` (or `NotFoundError`) for expected failures: routers may put
`str(error)` in the response. Anything else is an implementation detail; use
`public_message` so only a fixed text reaches the client and the cause is logged.
Both subclass ValueError, so existing `except ValueError` handlers still catch them.
"""

import logging

logger = logging.getLogger(__name__)


class DomainError(ValueError):
    """An expected failure with a user-facing message."""


class NotFoundError(DomainError):
    """The requested resource does not exist or is not the user's."""


def public_message(error: BaseException, fallback: str) -> str:
    """`str(error)` for a DomainError, otherwise `fallback` (and the error is logged)."""
    if isinstance(error, DomainError):
        return str(error)
    logger.error("%s: %s", fallback, error, exc_info=error)
    return fallback
