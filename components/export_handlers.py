"""
Export functionality for sessions and EMG data.
Handles CSV and .mat file exports with proper formatting.
"""
import io
import pandas as pd
import scipy.io
import streamlit as st
from typing import List, Dict
from services.supabase_client import fetch_session_data
from services.mat_processor import create_sessions_mat_dict, create_emg_mat_dict
from utils.data_processing import parse_emg_array
from utils.formatters import safe_filename


def export_sessions_csv(
    selected_rows: pd.DataFrame,
    patient_name: str
) -> bytes:
    """
    Export selected sessions as CSV with all datapoints.
    
    Args:
        selected_rows: DataFrame of selected sessions
        patient_name: Name of patient for filename
        
    Returns:
        CSV file as bytes
    """
    if selected_rows.empty:
        raise ValueError("No sessions selected for export")
    
    # Gather all datapoints for selected sessions
    all_rows = []
    session_ids = selected_rows["id"].tolist()
    
    for sid in session_ids:
        datapoints = fetch_session_data(sid)
        for dp in datapoints:
            all_rows.append({
                "session_id": sid,
                "timestamp": dp.get("timestamp"),
                "norm_emg": dp.get("norm_emg"),
                "rms_emg": dp.get("rms_emg"),
                "stimulation": dp.get("stimulation"),
                "exercise_phase": dp.get("exercise_phase")
            })
    
    if not all_rows:
        raise ValueError("No datapoints available for selected sessions")
    
    # Convert to CSV
    df = pd.DataFrame(all_rows)
    return df.to_csv(index=False).encode("utf-8")


def export_sessions_mat(
    selected_rows: pd.DataFrame,
    patient_name: str
) -> bytes:
    """
    Export selected sessions as .mat file.
    
    Args:
        selected_rows: DataFrame of selected sessions
        patient_name: Name of patient for filename
        
    Returns:
        .mat file as bytes
    """
    if selected_rows.empty:
        raise ValueError("No sessions selected for export")
    
    # Convert DataFrame rows to dicts (excluding display columns)
    session_dicts = []
    for _, row in selected_rows.iterrows():
        row_dict = row.to_dict()
        # Remove display-only columns
        row_dict.pop("_label", None)
        row_dict.pop("start_time_display", None)
        row_dict.pop("duration_display", None)
        session_dicts.append(row_dict)
    
    # Create .mat dictionary
    mdict = create_sessions_mat_dict(session_dicts)
    
    # Save to bytes
    bio = io.BytesIO()
    scipy.io.savemat(bio, mdict)
    bio.seek(0)
    return bio.read()


def export_emg_mat(
    selected_rows: pd.DataFrame,
    patient_name: str
) -> bytes:
    """
    Export EMG data from selected sessions as .mat file.
    
    Args:
        selected_rows: DataFrame of selected sessions
        patient_name: Name of patient for filename
        
    Returns:
        .mat file as bytes
    """
    if selected_rows.empty:
        raise ValueError("No sessions selected for export")
    
    timestamps = []
    emg_rows = []
    
    session_ids = selected_rows["id"].tolist()
    
    for sid in session_ids:
        datapoints = fetch_session_data(sid)
        for dp in datapoints:
            ts = dp.get("timestamp")
            
            # Try rms_emg first, then norm_emg
            arr_src = dp.get("rms_emg") or dp.get("norm_emg")
            if arr_src is None:
                continue
            
            # Parse EMG array
            arr = parse_emg_array(arr_src)
            if arr is None or arr.size == 0:
                continue
            
            timestamps.append(ts)
            emg_rows.append(arr)
    
    if not timestamps or not emg_rows:
        raise ValueError("No valid EMG samples to export")
    
    # Create .mat dictionary
    mdict = create_emg_mat_dict(timestamps, emg_rows)
    
    # Save to bytes
    bio = io.BytesIO()
    scipy.io.savemat(bio, mdict)
    bio.seek(0)
    return bio.read()


def handle_export_buttons(
    selected_rows: pd.DataFrame,
    patient_name: str
):
    """
    Render export buttons and handle download actions.
    
    Args:
        selected_rows: DataFrame of selected sessions
        patient_name: Name of patient for filename
    """
    st.markdown("### Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export CSV", width="stretch"):
            if selected_rows.empty:
                st.warning("⚠️ Select sessions first to export CSV")
            else:
                try:
                    csv_bytes = export_sessions_csv(selected_rows, patient_name)
                    filename = f"{safe_filename(patient_name)}_sessions.csv"
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv_bytes,
                        file_name=filename,
                        mime="text/csv",
                        width="stretch"
                    )
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    with col2:
        if st.button("📥 Export Sessions .mat", width="stretch"):
            if selected_rows.empty:
                st.warning("⚠️ Select sessions first to export .mat")
            else:
                try:
                    mat_bytes = export_sessions_mat(selected_rows, patient_name)
                    filename = f"{safe_filename(patient_name)}_sessions_table.mat"
                    st.download_button(
                        label="💾 Download Sessions .mat",
                        data=mat_bytes,
                        file_name=filename,
                        mime="application/octet-stream",
                        width="stretch"
                    )
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    with col3:
        if st.button("📥 Export EMG .mat", width="stretch"):
            if selected_rows.empty:
                st.warning("⚠️ Select sessions first to export EMG")
            else:
                try:
                    mat_bytes = export_emg_mat(selected_rows, patient_name)
                    filename = f"{safe_filename(patient_name)}_emg.mat"
                    st.download_button(
                        label="💾 Download EMG .mat",
                        data=mat_bytes,
                        file_name=filename,
                        mime="application/octet-stream",
                        width="stretch"
                    )
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
