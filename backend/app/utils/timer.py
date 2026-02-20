"""
Timer utilities for session management.
"""
from datetime import datetime, timedelta, timezone
import secrets

# Uzbekistan timezone UTC+5
UZ_TZ = timezone(timedelta(hours=5))


def now_uz() -> datetime:
    """Get current Uzbekistan time (UTC+5) as naive datetime."""
    return datetime.now(UZ_TZ).replace(tzinfo=None)


def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)


def calculate_expiry_time(duration_minutes: int) -> datetime:
    """
    Calculate expiration time from now.
    
    Args:
        duration_minutes: Session duration in minutes
    
    Returns:
        Datetime object representing expiration time
    """
    return now_uz() + timedelta(minutes=duration_minutes)


def is_expired(expires_at: datetime) -> bool:
    """
    Check if session has expired.
    
    Args:
        expires_at: Expiration datetime
    
    Returns:
        True if expired, False otherwise
    """
    return now_uz() >= expires_at


def time_remaining(expires_at: datetime) -> int:
    """
    Calculate remaining time in seconds.
    
    Args:
        expires_at: Expiration datetime
    
    Returns:
        Remaining seconds (0 if expired)
    """
    remaining = (expires_at - now_uz()).total_seconds()
    return max(0, int(remaining))
