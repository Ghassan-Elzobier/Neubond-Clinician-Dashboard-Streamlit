"""
Supabase data service for fetching patient and session data.
Uses Streamlit caching for performance.
"""
import streamlit as st
from typing import List, Dict, Optional
from config import SUPABASE_URL, SUPABASE_ANON

# Initialize Supabase client
try:
    from supabase import create_client
    
    if SUPABASE_URL and SUPABASE_ANON:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON)
    else:
        supabase = None
except Exception:
    supabase = None


def is_supabase_available() -> bool:
    """Check if Supabase is configured and available."""
    return supabase is not None

def sign_in(email, password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_id = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {e}")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_patients() -> List[Dict[str, any]]:
    """
    Fetch all patients from Supabase.
    
    Returns:
        List of patient dictionaries with 'id' and 'name' keys
    """
    if not supabase:
        return []
    
    try:
        resp = supabase.table("patient_profiles")\
            .select("id, name")\
            .order("name")\
            .execute()
        return resp.data or []
    except Exception as e:
        st.error(f"Error fetching patients: {e}")
        return []


@st.cache_data(ttl=60)  # Cache for 1 minute (sessions change more frequently)
def fetch_sessions(patient_profile_id: str) -> List[Dict[str, any]]:
    """
    Fetch sessions for a specific patient.
    
    Args:
        patient_profile_id: Patient's ID
        
    Returns:
        List of session dictionaries
    """
    if not supabase:
        return []
    
    try:
        resp = supabase.table("exercise_sessions")\
            .select(
                "id, start_time, exercise_type, exercise_gesture, "
                "duration_seconds, stimulation_mode, reps_completed"
            )\
            .eq("patient_profile_id", patient_profile_id)\
            .order("start_time", desc=True)\
            .execute()
        return resp.data or []
    except Exception as e:
        st.error(f"Error fetching sessions: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_session_data(session_id: str) -> List[Dict[str, any]]:
    """
    Fetch data points for a specific session.
    
    Args:
        session_id: Session ID
        
    Returns:
        List of data point dictionaries
    """
    if not supabase:
        return []
    
    try:
        resp = supabase.table("exercise_data_points")\
            .select(
                "timestamp, norm_emg, rms_emg, stimulation, exercise_phase"
            )\
            .eq("session_id", session_id)\
            .order("timestamp")\
            .execute()
        return resp.data or []
    except Exception as e:
        st.error(f"Error fetching session data: {e}")
        return []


@st.cache_data(ttl=60)
def fetch_multiple_sessions_data(session_ids: List[str]) -> Dict[str, List[Dict]]:
    """
    Fetch data points for multiple sessions efficiently.
    
    Args:
        session_ids: List of session IDs
        
    Returns:
        Dictionary mapping session_id to list of data points
    """
    if not supabase or not session_ids:
        return {}
    
    result = {}
    for sid in session_ids:
        result[sid] = fetch_session_data(sid)
    
    return result


# TODO: Add functions for future clinical data queries
# - fetch_session_statistics(patient_id, date_range) -> Aggregated stats
# - fetch_emg_quality_metrics(session_id) -> Quality analysis
# - fetch_patient_trends(patient_id) -> Long-term trends
