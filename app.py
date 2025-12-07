#!/usr/bin/env python3
"""
Neubond Clinician Dashboard - Main Application

A Streamlit web application for analyzing EMG and exercise session data.
Refactored for modularity, maintainability, and easy feature additions.

Author: Refactored version with best practices
Date: 2024
"""

import streamlit as st
from config import APP_TITLE, PAGE_LAYOUT
from components.sidebar import render_sidebar
from components.session_table import render_session_table, render_session_summary
from components.export_handlers import handle_export_buttons
from visualizations.emg_plots import plot_emg_channels
from visualizations.session_plots import plot_session_statistics
from services.supabase_client import fetch_session_data
from utils.data_processing import parse_emg_array
import numpy as np


def main():
    """Main application entry point."""
    # Configure page
    st.set_page_config(
        page_title=APP_TITLE,
        layout=PAGE_LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    st.title(APP_TITLE)
    st.markdown("*Analyze patient exercise sessions and EMG data*")
    
    # Render sidebar and get selections
    sidebar_data = render_sidebar()
    selected_patient = sidebar_data["selected_patient"]
    uploaded_mat = sidebar_data["uploaded_mat"]
    
    # Main content area
    render_main_content(selected_patient, uploaded_mat)


def render_main_content(selected_patient, uploaded_mat):
    """
    Render the main content area with sessions table and visualizations.
    
    Args:
        selected_patient: Selected patient dict or None
        uploaded_mat: Uploaded .mat file info or None
    """
    # Sessions Table (primary focus)
    patient_id = selected_patient["id"] if selected_patient else None
    selected_rows = render_session_table(patient_id)
    
    # Session Summary
    if not selected_rows.empty:
        render_session_summary(selected_rows)
    
    # Export Section
    if selected_patient:
        st.markdown("---")
        handle_export_buttons(
            selected_rows,
            selected_patient["name"]
        )
    
    # Visualization Section
    st.markdown("---")
    render_visualizations(selected_rows, uploaded_mat)


def render_visualizations(selected_rows, uploaded_mat):
    """
    Render visualization section with plots from database or uploaded files.
    
    Args:
        selected_rows: DataFrame of selected sessions
        uploaded_mat: Uploaded .mat file info or None
    """
    st.header("Visualizations")
    
    # Create tabs for different visualization modes
    tab1, tab2, tab3 = st.tabs([
        "📊 Session Statistics", 
        "📈 EMG Analysis", 
        "📁 Uploaded File Plots"
    ])
    
    with tab1:
        render_session_statistics_tab(selected_rows, uploaded_mat)
    
    with tab2:
        render_emg_analysis_tab(selected_rows)
    
    with tab3:
        render_uploaded_file_tab(uploaded_mat)


def render_session_statistics_tab(selected_rows, uploaded_mat):
    """Render session statistics visualizations."""
    st.subheader("Session Statistics Over Time")
    
    # Try uploaded file first
    if uploaded_mat and uploaded_mat["type"] == "sessions_table":
        with st.spinner("Generating plots..."):
            chart = plot_session_statistics(uploaded_mat["data"])
            if chart:
                st.altair_chart(chart, width="stretch")
            else:
                st.info("No session data to plot")
    else:
        st.info("""
        📊 **Session statistics visualization**
        
        Upload a sessions .mat file to see:
        - Sessions per day
        - Total duration per day  
        - Time of day patterns
        
        *Future: Generate directly from selected database sessions*
        """)


def render_emg_analysis_tab(selected_rows):
    """Render EMG analysis for selected sessions."""
    st.subheader("EMG Channel Analysis")
    
    if selected_rows.empty:
        st.info("Select a session from the table above to plot EMG data")
        return
    
    if len(selected_rows) > 1:
        st.warning("⚠️ Please select exactly ONE session to plot EMG data")
        return
    
    # Plot single session EMG
    session_id = selected_rows.iloc[0]["id"]
    
    if st.button("🔄 Load EMG Data", width="stretch"):
        with st.spinner("Loading EMG data..."):
            datapoints = fetch_session_data(session_id)
            
            if not datapoints:
                st.error("No EMG data found for this session")
                return
            
            # Extract EMG arrays
            timestamps = []
            emg_rows = []
            phase_list = []
            
            for dp in datapoints:
                timestamps.append(dp.get("timestamp"))
                
                # Try rms_emg first, then norm_emg
                arr_src = dp.get("rms_emg") or dp.get("norm_emg")
                arr = parse_emg_array(arr_src)
                
                if arr is not None and arr.size > 0:
                    emg_rows.append(arr)
                    phase_list.append(dp.get("exercise_phase"))
            
            if not emg_rows:
                st.error("No valid EMG data to plot")
                return
            
            # Create EMG data dict
            emg_data = {
                "timestamps": np.array(timestamps, dtype=object),
                "emg": np.vstack(emg_rows),
                "exercise_phase": np.array(phase_list, dtype=object)
            }
            
            # Generate plot
            fig = plot_emg_channels(emg_data, title=f"EMG Data - Session {session_id}")
            st.pyplot(fig)
            
            # Show data info
            with st.expander("ℹ️ Data Information"):
                st.write(f"**Samples:** {len(timestamps)}")
                st.write(f"**Channels:** {emg_rows[0].shape[0] if emg_rows else 0}")
                st.write(f"**Duration:** {(timestamps[-1] if timestamps else 'N/A')}")


def render_uploaded_file_tab(uploaded_mat):
    """Render visualizations for uploaded .mat files."""
    st.subheader("Uploaded File Visualization")
    
    if not uploaded_mat:
        st.info("📁 Upload a .mat file in the sidebar to visualize it here")
        return
    
    file_type = uploaded_mat["type"]
    
    if file_type == "sessions_table":
        if st.button("📊 Plot Session Statistics"):
            with st.spinner("Generating plots..."):
                chart = plot_session_statistics(uploaded_mat["data"])
                if chart:
                    st.altair_chart(chart, width="stretch")
                else:
                    st.info("No valid session data to plot")
    
    elif file_type == "emg":
        if st.button("📈 Plot EMG Channels"):
            with st.spinner("Generating plot..."):
                fig = plot_emg_channels(uploaded_mat["data"])
                st.pyplot(fig)
    
    else:
        st.warning(f"⚠️ Unknown file type: {file_type}")
        st.info("Upload a sessions table or EMG .mat file")


if __name__ == "__main__":
    main()
