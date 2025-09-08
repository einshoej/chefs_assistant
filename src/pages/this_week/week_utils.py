"""
Week utilities for managing date calculations and week formatting
"""

from datetime import datetime, timedelta
import calendar


def get_current_week_number() -> tuple[int, int]:
    """Get the current ISO week number and year
    
    Returns:
        tuple: (week_number, year)
    """
    now = datetime.now()
    year, week_number, _ = now.isocalendar()
    return week_number, year


def get_week_date_range(week_number: int, year: int) -> tuple[datetime, datetime]:
    """Get the start and end dates for a given ISO week number
    
    Args:
        week_number: ISO week number (1-53)
        year: Year
        
    Returns:
        tuple: (start_date, end_date) as datetime objects
    """
    # Create a date object for the Thursday of the specified week
    # (ISO weeks are defined by their Thursday)
    jan4 = datetime(year, 1, 4)  # Jan 4 is always in the first ISO week
    week1_thursday = jan4 - timedelta(days=jan4.weekday() - 3)  # Thursday of week 1
    target_thursday = week1_thursday + timedelta(weeks=week_number - 1)
    
    # Monday is 3 days before Thursday
    week_start = target_thursday - timedelta(days=3)
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end


def format_week_label(week_number: int, year: int) -> str:
    """Format a week label for display
    
    Args:
        week_number: ISO week number
        year: Year
        
    Returns:
        str: Formatted week label (e.g., "Week 35 (Aug 26 - Sep 1)")
    """
    try:
        start_date, end_date = get_week_date_range(week_number, year)
        
        # Format dates
        start_str = start_date.strftime("%b %d")
        end_str = end_date.strftime("%b %d")
        
        # Handle year boundary
        if start_date.year != end_date.year:
            start_str = start_date.strftime("%b %d, %Y")
            end_str = end_date.strftime("%b %d, %Y")
        
        return f"Week {week_number} ({start_str} - {end_str})"
    except:
        return f"Week {week_number}"


def get_relative_week_label(week_offset: int) -> str:
    """Get a relative week label (e.g., 'This Week', 'Next Week')
    
    Args:
        week_offset: Number of weeks from current week (0 = this week, 1 = next week, etc.)
        
    Returns:
        str: Relative week label
    """
    # Calculate target week by adding weeks to current date
    target_date = datetime.now() + timedelta(weeks=week_offset)
    target_year, target_week, _ = target_date.isocalendar()
    
    # Create base label with week info
    base_label = format_week_label(target_week, target_year)
    
    # Add relative context
    if week_offset == 0:
        return f"This Week - {base_label}"
    elif week_offset == 1:
        return f"Next Week - {base_label}"
    elif week_offset == 2:
        return f"Week After Next - {base_label}"
    else:
        return f"Week +{week_offset} - {base_label}"


def get_week_key(week_offset: int) -> str:
    """Get a consistent key for storing week data
    
    Args:
        week_offset: Number of weeks from current week
        
    Returns:
        str: Week key in format "YYYY-WXX"
    """
    target_date = datetime.now() + timedelta(weeks=week_offset)
    year, week_number, _ = target_date.isocalendar()
    return f"{year}-W{week_number:02d}"


def parse_week_key(week_key: str) -> tuple[int, int]:
    """Parse a week key back to year and week number
    
    Args:
        week_key: Week key in format "YYYY-WXX"
        
    Returns:
        tuple: (year, week_number)
    """
    try:
        year_str, week_str = week_key.split('-W')
        return int(year_str), int(week_str)
    except:
        current_week, current_year = get_current_week_number()
        return current_year, current_week