#!/usr/bin/env python3
"""
Neubond Clinician Dashboard - Main Application

A Streamlit web application for analyzing EMG and exercise session data.
Refactored for modularity, maintainability, and easy feature additions.

Author: Refactored version with best practices
Date: 2024
"""

import streamlit as st
import pandas as pd
from config import APP_TITLE, PAGE_LAYOUT
from components.sidebar import render_sidebar
from components.session_table import render_session_table, render_session_summary
from components.pdf_component import render_pdf_download_section, render_quick_pdf_button
from components.export_handlers import handle_export_buttons
from visualizations.emg_plots import plot_emg_channels, plot_emg_plotly_stacked
from visualizations.session_plots import plot_session_statistics, plot_session_statistics_from_dataframe
from services.supabase_client import fetch_session_data
from utils.data_processing import parse_emg_array, prepare_emg_data
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
    
    # PDF Section
    # render_pdf_download_section(selected_patient["name"], selected_rows)

    
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
        "Session Statistics", 
        "EMG Analysis", 
        "Uploaded File Plots"
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
    
    # Prioritize selected sessions from database
    if not selected_rows.empty:
        with st.spinner("Generating plots from selected sessions..."):
            # Convert DataFrame to format expected by plot_session_statistics
            chart = plot_session_statistics_from_dataframe(selected_rows)
            if chart:
                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning("Unable to generate plots from selected sessions")
    
    # Fallback to uploaded file
    elif uploaded_mat and uploaded_mat["type"] == "sessions_table":
        with st.spinner("Generating plots from uploaded file..."):
            chart = plot_session_statistics(uploaded_mat["data"])
            if chart:
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No session data to plot")
    
    # No data available
    else:
        st.info("""
        📊 **Session statistics visualization**
        
        **To see charts:**
        1. Select sessions from the table above, OR
        2. Upload a sessions .mat file in the sidebar
        
        **Charts include:**
        - Sessions per day
        - Total duration per day  
        - Time of day patterns
        """)


def render_emg_analysis_tab(selected_rows):
    """Render EMG analysis for selected sessions with Plotly."""
    st.subheader("EMG Channel Analysis")

    # ---- No session selected ----
    if selected_rows.empty:
        st.info("Select a session from the table above to plot EMG data")
        return

    # ---- Multiple sessions selected ----
    if len(selected_rows) > 1:
        st.warning("⚠️ Please select exactly ONE session to plot EMG data")
        return

    # ---- Exactly one session selected → AUTO-PLOT ----
    session_id = selected_rows.iloc[0]["id"]

    with st.spinner(f"Loading EMG data for session {session_id}..."):
        datapoints = fetch_session_data(session_id)

        if not datapoints:
            st.error("No EMG data found for this session")
            return

        timestamps = []
        emg_rows = []
        phase_list = []

        for dp in datapoints:
            timestamps.append(dp.get("timestamp"))

            arr_src = dp.get("rms_emg") or dp.get("norm_emg")
            arr = parse_emg_array(arr_src)

            if arr is not None and arr.size > 0:
                emg_rows.append(arr)
                phase_list.append(dp.get("exercise_phase"))

        if not emg_rows:
            st.error("No valid EMG data to plot")
            return

        # Construct EMG data dictionary
        emg_data = {
            "timestamps": np.array(timestamps, dtype=object),
            "emg": np.vstack(emg_rows),
            "exercise_phase": np.array(phase_list, dtype=object)
        }

        processed = prepare_emg_data(emg_data)

        # X-axis toggle
        display_mode = st.radio("X-axis:", ["duration", "timestamp"], index=0)

        # Y-axis toggle (local vs global)
        y_mode = st.radio(
            "Y-axis scale:",
            ["local (per channel)", "global (shared across channels)"],
            index=0
        )
        y_mode_internal = "local" if "local" in y_mode else "global"

        # Plot
        fig = plot_emg_plotly_stacked(
            processed,
            title=f"EMG Data - Session {session_id}",
            mode=display_mode,
            y_mode=y_mode_internal
        )

        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Unable to plot EMG data.")

        # Optional info box
        with st.expander("ℹ️ Data Information"):
            if len(timestamps) >= 2:
                try:
                    t0 = pd.Timestamp(timestamps[0])
                    duration_sec = (pd.Timestamp(timestamps[-1]) - t0).total_seconds()
                except Exception:
                    duration_sec = "N/A"
            else:
                duration_sec = "N/A"

            st.write(f"**Samples:** {len(timestamps)}")
            st.write(f"**Channels:** {emg_rows[0].shape[0] if emg_rows else 0}")
            st.write(f"**Duration:** {duration_sec if isinstance(duration_sec, str) else f'{duration_sec:.1f} seconds'}")



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
