"""
MATLAB .mat file processing service.
Handles parsing, type detection, and data extraction from .mat files.
"""
import io
from typing import Dict, Any, Union
import scipy.io
import streamlit as st
from utils.formatters import unwrap_mat_value


@st.cache_data
def parse_mat_file(mat_path_or_bytes: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
    """
    Parse a .mat file and detect its type.
    
    Args:
        mat_path_or_bytes: File path, bytes, or BytesIO object
        
    Returns:
        Dictionary with 'type' and 'data' keys:
        - type: 'emg', 'sessions_table', 'unknown', or 'error'
        - data: Parsed data dict or error message
    """
    try:
        # Load the .mat file
        if isinstance(mat_path_or_bytes, (bytes, bytearray, io.BytesIO)):
            buf = (mat_path_or_bytes if isinstance(mat_path_or_bytes, io.BytesIO) 
                   else io.BytesIO(mat_path_or_bytes))
            buf.seek(0)
            data = scipy.io.loadmat(buf, simplify_cells=True)
        else:
            data = scipy.io.loadmat(mat_path_or_bytes, simplify_cells=True)
    except Exception as e:
        return {"type": "error", "data": str(e)}
    
    # Detect file type
    file_type = _detect_mat_type(data)
    
    return {"type": file_type, "data": data}


def _detect_mat_type(data: Dict[str, Any]) -> str:
    """
    Detect the type of .mat file based on its contents.
    
    Args:
        data: Parsed .mat file dictionary
        
    Returns:
        Type string: 'emg', 'sessions_table', or 'unknown'
    """
    # Check for explicit 'type' variable
    t_val = data.get("type", None)
    if t_val is not None:
        t = (unwrap_mat_value(t_val[0]) if isinstance(t_val, (list, tuple)) and len(t_val) > 0 
             else unwrap_mat_value(t_val))
        if isinstance(t, str):
            t_low = t.lower()
            if t_low.startswith("sessions"):
                return "sessions_table"
            if t_low.startswith("emg"):
                return "emg"
    
    # Fallback detection based on field names
    if "emg" in data and ("timestamps" in data or "time" in data):
        return "emg"
    if "time" in data or "session_id" in data:
        return "sessions_table"
    
    return "unknown"


def create_sessions_mat_dict(session_rows: list) -> Dict[str, Any]:
    """
    Create a dictionary suitable for saving as a sessions .mat file.
    
    Args:
        session_rows: List of session dictionaries
        
    Returns:
        Dictionary ready for scipy.io.savemat
    """
    import numpy as np
    from utils.data_processing import flatten_to_1d_array
    
    mdict = {
        "session_id": flatten_to_1d_array([r.get("id") for r in session_rows]),
        "time": flatten_to_1d_array([r.get("start_time") for r in session_rows]),
        "duration_seconds": flatten_to_1d_array([r.get("duration_seconds") for r in session_rows]),
        "exercise_type": flatten_to_1d_array([r.get("exercise_type") for r in session_rows]),
        "exercise_gesture": flatten_to_1d_array([r.get("exercise_gesture") for r in session_rows]),
        "stimulation_mode": flatten_to_1d_array([r.get("stimulation_mode") for r in session_rows]),
        "reps_completed": flatten_to_1d_array([r.get("reps_completed") for r in session_rows]),
        "type": np.array(["sessions_table"], dtype=object)
    }
    
    return mdict


def create_emg_mat_dict(timestamps: list, emg_rows: list) -> Dict[str, Any]:
    """
    Create a dictionary suitable for saving as an EMG .mat file.
    
    Args:
        timestamps: List of timestamp strings
        emg_rows: List of EMG arrays (one per timestamp)
        
    Returns:
        Dictionary ready for scipy.io.savemat
    """
    import numpy as np
    
    return {
        "timestamps": np.array(timestamps, dtype=object),
        "emg": np.vstack(emg_rows),
        "type": np.array(["emg"], dtype=object)
    }


def extract_mat_field(data: Dict[str, Any], field_name: str) -> list:
    """
    Extract and unwrap a field from .mat file data.
    
    Args:
        data: Parsed .mat file dictionary
        field_name: Name of field to extract
        
    Returns:
        List of unwrapped values
    """
    import numpy as np
    
    val = data.get(field_name, [])
    
    if isinstance(val, np.ndarray):
        # Flatten to 1D
        while getattr(val, "ndim", 0) > 1:
            val = val.flatten()
        return [unwrap_mat_value(v) for v in val]
    elif isinstance(val, list):
        return [unwrap_mat_value(v) for v in val]
    else:
        return [unwrap_mat_value(val)]
