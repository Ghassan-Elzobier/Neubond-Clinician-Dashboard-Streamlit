"""
Data processing utilities for EMG and session data.
"""
import ast
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from utils.formatters import parse_timestamp_string, unwrap_mat_value, format_timestamp_for_display


def flatten_to_1d_array(values: Any) -> np.ndarray:
    """
    Flatten nested arrays to 1D.
    
    Args:
        values: Input values (list, array, etc.)
        
    Returns:
        1D numpy array
    """
    arr = np.array(values, dtype=object)
    if arr.ndim > 1:
        arr = arr.flatten()
    return arr


def break_gaps_mask(times: np.ndarray, factor: float = 5.0) -> np.ndarray:
    """
    Return boolean mask of points AFTER a large time gap.
    Used to break plotting lines at gaps.
    
    Args:
        times: Array of datetime objects
        factor: Threshold multiplier for gap detection
        
    Returns:
        Boolean mask array
    """
    if len(times) < 2:
        return np.zeros(len(times), dtype=bool)
    
    t64 = np.array(times).astype("datetime64[us]")
    dt = np.diff(t64).astype("timedelta64[us]").astype(np.float64)
    base = np.median(dt) if dt.size > 0 else 1.0
    threshold = base * factor
    gap_after = dt > threshold
    mask = np.insert(gap_after, 0, False)
    return mask.astype(bool)


def parse_emg_array(arr_src: Any) -> Optional[np.ndarray]:
    """
    Parse EMG array from various source formats.
    
    Args:
        arr_src: Source data (list, string, array)
        
    Returns:
        Numpy array or None if parsing fails
    """
    if arr_src is None:
        return None
    
    try:
        if isinstance(arr_src, list):
            return np.array(arr_src, dtype=float)
        elif isinstance(arr_src, str):
            return np.array(ast.literal_eval(arr_src), dtype=float)
        else:
            return np.array(arr_src, dtype=float)
    except Exception:
        return None


def prepare_emg_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare EMG data for plotting by extracting and aligning arrays.
    
    Args:
        data: Dictionary with 'emg', 'timestamps', optionally 'exercise_phase'
        
    Returns:
        Dictionary with processed arrays: 'times', 'emg_num', 'phase_arr'
    """
    emg = data.get("emg", None)
    timestamps = data.get("timestamps", None)
    phase_array = data.get("exercise_phase", None)
    
    # Prepare timestamps -> list of datetimes
    if timestamps is None:
        times = np.array([], dtype=object)
    else:
        times_list = [
            parse_timestamp_string(str(unwrap_mat_value(t))) 
            for t in np.array(timestamps, dtype=object)
        ]
        valid_mask = np.array([t is not None for t in times_list], dtype=bool)
        times = np.array(times_list, dtype=object)[valid_mask]
    
    # Prepare emg as numeric 2D array
    if emg is None:
        emg_num = np.empty((0, 0))
    else:
        emg_arr = np.array(emg, dtype=object)
        if emg_arr.ndim == 1 and emg_arr.dtype == object:
            try:
                emg_num = np.vstack([np.array(r, dtype=float) for r in emg_arr])
            except Exception:
                try:
                    emg_num = np.array(emg_arr, dtype=float)
                except Exception:
                    emg_num = np.empty((0, 0))
        else:
            try:
                emg_num = np.asarray(emg_arr, dtype=float)
            except Exception:
                emg_num = np.empty((0, 0))
    
    # Align shapes
    if times.size and emg_num.size:
        if emg_num.shape[0] > len(times):
            emg_num = emg_num[:len(times), :]
        elif emg_num.shape[0] < len(times):
            times = times[:emg_num.shape[0]]
    
    # Phase handling
    phase_arr = None
    if phase_array is not None and times.size > 0:
        pa = np.array(phase_array, dtype=object)
        if pa.shape[0] >= len(times):
            pa = pa[:len(times)]
        phase_arr = np.array([str(unwrap_mat_value(v)) for v in pa], dtype=object)
    
    # Sort by time
    if times.size > 0:
        sort_idx = np.argsort(times)
        times = times[sort_idx]
        emg_num = emg_num[sort_idx, :]
        if phase_arr is not None:
            phase_arr = phase_arr[sort_idx]
    
    return {
        "times": times,
        "emg_num": emg_num,
        "phase_arr": phase_arr
    }


def prepare_session_dataframe(sessions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert session list to formatted DataFrame with readable timestamps.
    
    Args:
        sessions: List of session dictionaries
        
    Returns:
        Formatted pandas DataFrame
    """
    if not sessions:
        return pd.DataFrame()
    
    df = pd.DataFrame(sessions)
    
    # Format timestamps for display
    if 'start_time' in df.columns:
        df['start_time_display'] = df['start_time'].apply(
            lambda x: format_timestamp_for_display(x)
        )
        # Keep original for sorting/filtering
        df['start_time_raw'] = df['start_time']
        # Reorder columns to show display version
        cols = list(df.columns)
        cols.remove('start_time')
        cols.remove('start_time_display')
        cols.remove('start_time_raw')
        df = df[['start_time_display'] + cols + ['start_time_raw']]
        df = df.rename(columns={'start_time_display': 'start_time'})
    
    # Format duration
    if 'duration_seconds' in df.columns:
        df['duration_display'] = df['duration_seconds'].apply(
            lambda x: format_duration_seconds(x)
        )
    
    return df


def format_duration_seconds(seconds: float) -> str:
    """Format seconds into readable duration."""
    if seconds is None or np.isnan(seconds):
        return "N/A"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


# TODO: Add functions for clinical analysis
# - calculate_session_statistics(sessions) -> Dict with avg duration, frequency, etc.
# - analyze_time_patterns(sessions) -> Day of week, time of day analysis
# - calculate_emg_statistics(emg_data) -> Amplitude stats, quality metrics
# - detect_cocontraction(emg_data) -> Co-contraction analysis
# - calculate_trends(sessions) -> Trend analysis over time
