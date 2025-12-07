"""
Formatting utilities for timestamps, filenames, and display values.
"""
import re
from datetime import datetime
from typing import Optional, Any
import numpy as np
from config import TIMESTAMP_DISPLAY_FORMAT, TIMESTAMP_DISPLAY_FORMAT_SHORT


def safe_filename(s: str) -> str:
    """
    Convert a string to a safe filename by removing special characters.
    
    Args:
        s: Input string
        
    Returns:
        Safe filename string
    """
    s = (s or "").strip()
    s = re.sub(r"\s+", "_", s)
    return re.sub(r"[^A-Za-z0-9._-]", "", s)


def format_timestamp_for_display(ts: Any, short: bool = False) -> str:
    """
    Format a timestamp for user-friendly display.
    
    Args:
        ts: Timestamp (datetime, string, or None)
        short: If True, use short format
        
    Returns:
        Formatted timestamp string
    """
    if ts is None:
        return "N/A"
    
    # Convert to datetime if needed
    if isinstance(ts, str):
        dt = parse_timestamp_string(ts)
        if dt is None:
            return ts  # Return original if parsing fails
    elif isinstance(ts, datetime):
        dt = ts
    else:
        return str(ts)
    
    format_str = TIMESTAMP_DISPLAY_FORMAT_SHORT if short else TIMESTAMP_DISPLAY_FORMAT
    return dt.strftime(format_str)


def parse_timestamp_string(ts: Any) -> Optional[datetime]:
    """
    Robust ISO-like timestamp parsing.
    
    Args:
        ts: Timestamp to parse (string, datetime, or other)
        
    Returns:
        datetime object or None if parsing fails
    """
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts
    if not isinstance(ts, str):
        return None
    
    s = ts.strip()
    
    # Handle microsecond trimming/zero-padding and 'Z' suffix
    if "T" in s and "." in s:
        date_part, frac = s.split(".", 1)
        frac_digits = "".join(ch for ch in frac if ch.isdigit())
        frac6 = frac_digits[:6].ljust(6, "0")
        s = f"{date_part}.{frac6}"
    
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "5m 30s")
    """
    if seconds is None or np.isnan(seconds):
        return "N/A"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def format_time_of_day(hour: float) -> str:
    """
    Format hour of day (0-24) to readable string.
    
    Args:
        hour: Hour as float (e.g., 14.5 = 2:30 PM)
        
    Returns:
        Formatted time string
    """
    h = int(hour)
    m = int((hour - h) * 60)
    period = "AM" if h < 12 else "PM"
    display_h = h if h <= 12 else h - 12
    if display_h == 0:
        display_h = 12
    return f"{display_h}:{m:02d} {period}"


def unwrap_mat_value(val: Any) -> Any:
    """
    Unwrap values loaded by scipy.io.loadmat into Python-friendly scalars.
    
    Args:
        val: Value from matlab file
        
    Returns:
        Unwrapped Python value
    """
    if isinstance(val, np.ndarray) and val.size == 1:
        return unwrap_mat_value(val.item())
    if isinstance(val, (bytes, bytearray)):
        try:
            return val.decode("utf-8")
        except Exception:
            return val
    if isinstance(val, np.generic):
        return val.item()
    return val
