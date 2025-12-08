"""
Sidebar UI components for patient selection and file upload.
"""
import streamlit as st
from typing import Optional, Dict, Any
from services.supabase_client import fetch_patients, is_supabase_available, sign_out
from services.mat_processor import parse_mat_file


def render_sidebar() -> Dict[str, Any]:
    """
    Render sidebar with patient selector and file uploader.
    
    Returns:
        Dictionary containing:
        - selected_patient: Dict with 'id' and 'name' or None
        - uploaded_mat: Dict with parsed .mat file info or None
    """
    with st.sidebar:
        st.header("Controls")
        
        # Patient selection
        selected_patient = _render_patient_selector()
        
        st.markdown("---")
        
        # File upload
        uploaded_mat = _render_file_uploader()
        
        st.markdown("---")
        
        # Info about mode
        _render_connection_status()

        if st.button("Logout"):
            sign_out()
        
        return {
            "selected_patient": selected_patient,
            "uploaded_mat": uploaded_mat
        }


def _render_patient_selector() -> Optional[Dict[str, str]]:
    """Render patient selection dropdown."""
    st.subheader("Patient Selection")
    
    if not is_supabase_available():
        st.info("💡 Supabase not configured. Upload .mat files to view data.")
        return None
    
    patients = fetch_patients()
    
    if not patients:
        st.warning("⚠️ No patients found in database")
        return None
    
    patient_map = {p["name"]: p["id"] for p in patients}
    patient_names = ["(Select a patient)"] + list(patient_map.keys())
    
    selected_name = st.selectbox(
        "Select patient",
        patient_names,
        index=0,
        help="Choose a patient to view their exercise sessions"
    )
    
    if selected_name == "(Select a patient)":
        return None
    
    return {
        "name": selected_name,
        "id": patient_map[selected_name]
    }


def _render_file_uploader() -> Optional[Dict[str, Any]]:
    """Render file uploader for .mat files."""
    st.subheader("📁 File Upload")
    
    uploaded_file = st.file_uploader(
        "Upload .mat file",
        type=["mat"],
        help="Upload EMG data or session table .mat file"
    )
    
    if uploaded_file is None:
        return None
    
    # Parse uploaded file
    file_bytes = uploaded_file.read()
    parsed_info = parse_mat_file(file_bytes)
    
    if parsed_info["type"] == "error":
        st.error(f"❌ Failed to read .mat file: {parsed_info['data']}")
        return None
    
    # Show success with file type
    file_type = parsed_info["type"]
    type_emoji = "📊" if file_type == "sessions_table" else "📈" if file_type == "emg" else "❓"
    st.success(f"{type_emoji} Detected as: **{file_type}**")
    
    return parsed_info


def _render_connection_status():
    """Render connection status and mode information."""
    st.caption("ℹ️ **Connection Status**")
    
    if is_supabase_available():
        st.caption("✅ Connected to Supabase")
        st.caption("📡 Live data mode")
    else:
        st.caption("⚪ Supabase not configured")
        st.caption("📂 Upload .mat files to view data")
        st.caption("")
        with st.expander("🔧 Setup Instructions"):
            st.markdown("""
            To connect to Supabase:
            1. Create a `.env` file in the project root
            2. Add your credentials:
               ```
               SUPABASE_URL=your_url_here
               SUPABASE_SECRET_KEY=your_key_here
               ```
            3. Restart the app
            """)
