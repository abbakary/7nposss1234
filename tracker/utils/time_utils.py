"""
Time utilities for calculating order duration and overdue status.
Overdue threshold: 9 calendar hours (simple calculation).
"""

from datetime import datetime, timedelta
from django.utils import timezone


# Simple overdue threshold: 9 calendar hours
OVERDUE_THRESHOLD_HOURS = 9


def is_order_overdue(started_at: datetime, now: datetime = None) -> bool:
    """
    Check if an order has exceeded the 9-hour calendar threshold.
    Simple calculation: just check elapsed calendar hours, no working hour complexity.

    Args:
        started_at: Order start datetime
        now: Current datetime (defaults to timezone.now())

    Returns:
        True if order has been active for 9+ calendar hours, False otherwise
    """
    if not started_at:
        return False

    if now is None:
        now = timezone.now()

    # Ensure both datetimes are timezone-aware
    if timezone.is_naive(started_at):
        started_at = timezone.make_aware(started_at)
    if timezone.is_naive(now):
        now = timezone.make_aware(now)

    # Simple calendar hours check
    elapsed_hours = (now - started_at).total_seconds() / 3600.0

    return elapsed_hours >= OVERDUE_THRESHOLD_HOURS


def get_order_overdue_status(order) -> dict:
    """
    Get the overdue status of an order.
    Simple calculation: just check elapsed calendar hours.

    Args:
        order: Order instance

    Returns:
        Dictionary with:
        - is_overdue (bool): Whether the order is overdue (9+ hours elapsed)
        - hours_elapsed (float): Calendar hours since start
        - overdue_by_hours (float): How many hours over the threshold (0 if not overdue)
    """
    result = {
        'is_overdue': False,
        'hours_elapsed': 0.0,
        'overdue_by_hours': 0.0,
    }

    if not order.started_at:
        return result

    now = timezone.now()

    # Ensure timezone-aware
    started_at = order.started_at
    if timezone.is_naive(started_at):
        started_at = timezone.make_aware(started_at)
    if timezone.is_naive(now):
        now = timezone.make_aware(now)

    # Simple calendar hours check
    elapsed_hours = (now - started_at).total_seconds() / 3600.0
    result['hours_elapsed'] = round(elapsed_hours, 2)

    if elapsed_hours >= OVERDUE_THRESHOLD_HOURS:
        result['is_overdue'] = True
        result['overdue_by_hours'] = round(elapsed_hours - OVERDUE_THRESHOLD_HOURS, 2)

    return result


def format_hours(hours: float) -> str:
    """
    Format hours as a human-readable string.

    Args:
        hours: Number of hours (float)

    Returns:
        Formatted string like "9h 30m" or "2h 15m"
    """
    if hours < 0:
        return "0h"

    total_minutes = int(hours * 60)
    hours_part = total_minutes // 60
    minutes_part = total_minutes % 60

    if hours_part == 0 and minutes_part == 0:
        return "0h"
    elif hours_part == 0:
        return f"{minutes_part}m"
    elif minutes_part == 0:
        return f"{hours_part}h"
    else:
        return f"{hours_part}h {minutes_part}m"


def estimate_completion_time(started_at: datetime, estimated_minutes: int = None) -> dict:
    """
    Estimate the completion time based on start time and estimated duration.

    Args:
        started_at: Order start datetime
        estimated_minutes: Estimated duration in minutes (defaults to 9 hours)

    Returns:
        Dictionary with:
        - estimated_end (datetime): Estimated completion datetime
        - estimated_hours (float): Estimated duration in hours
        - formatted (str): Human-readable format
    """
    if not started_at:
        return None

    if estimated_minutes is None:
        estimated_minutes = OVERDUE_THRESHOLD_HOURS * 60

    estimated_hours = estimated_minutes / 60.0

    # Simple: add estimated hours to start time
    estimated_end = started_at + timedelta(hours=estimated_hours)

    return {
        'estimated_end': estimated_end,
        'estimated_hours': estimated_hours,
        'formatted': format_hours(estimated_hours),
    }
