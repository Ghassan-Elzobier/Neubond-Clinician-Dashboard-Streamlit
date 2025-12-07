"""
Session table display and selection components.
"""
import streamlit as st
import pandas as pd
from typing import Optional
from services.supabase_client import fetch_sessions
from utils.data_processing import prepare_session_dataframe


def render_session_table(patient_id: Optional[str]) -> pd.DataFrame:
    """
    Render the sessions table with interactive selection using Streamlit's native dataframe.
    
    Args:
        patient_id: ID of selected patient or None
        
    Returns:
        DataFrame of selected session rows (may be empty)
        
    TODO: Future enhancements for clinical insights:
    - Show session quality indicators
    - Display EMG amplitude summary per session
    - Highlight sessions with unusual patterns
    - Add sortable columns with custom metrics
    """
    st.header("Exercise Sessions")
    
    if patient_id is None:
        st.info("Select a patient from the sidebar to view sessions")
        return pd.DataFrame()
    
    # Fetch and prepare sessions
    with st.spinner("Loading sessions..."):
        sessions = fetch_sessions(patient_id)
    
    if not sessions:
        st.warning("⚠️ No sessions found for this patient")
        return pd.DataFrame()
    
    # Prepare dataframe with readable timestamps
    df_sessions = prepare_session_dataframe(sessions)
    
    # Filter controls (collapsible for clean UI)
    df_filtered = _render_filter_controls(df_sessions)
    
    if df_filtered.empty:
        st.warning("No sessions match the current filters")
        return pd.DataFrame()
    
    # Display session count
    st.metric("Showing Sessions", len(df_filtered))
    
    # Display interactive table with selection
    st.subheader("Select Sessions")
    
    # Prepare columns for display (hide internal columns)
    display_cols = [col for col in df_filtered.columns 
                   if col not in ['start_time_raw']]
    
    # Use Streamlit's interactive dataframe with selection
    event = st.dataframe(
        df_filtered[display_cols],
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row"
    )
    
    # Get selected rows based on user selection
    selected_indices = event.selection.rows
    
    if selected_indices:
        selected_rows = df_filtered.iloc[selected_indices]
        st.success(f"✅ {len(selected_rows)} session(s) selected")
        return selected_rows
    else:
        st.info("💡 Click on rows in the table above to select sessions for export or analysis")
        return pd.DataFrame()


def _render_filter_controls(df_sessions: pd.DataFrame) -> pd.DataFrame:
    """
    Render filter controls and return filtered dataframe.
    
    Args:
        df_sessions: Full dataframe of sessions
        
    Returns:
        Filtered dataframe based on user selections
    """
    with st.expander("Filter Sessions", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        # Date range filter
        with col1:
            st.markdown("**Date Range**")
            
            # Get min/max dates from data
            if 'start_time_raw' in df_sessions.columns:
                dates = pd.to_datetime(df_sessions['start_time_raw'])
                min_date = dates.min().date()
                max_date = dates.max().date()
                
                date_range = st.date_input(
                    "Select range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    label_visibility="collapsed"
                )
                
                # Apply date filter
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_date, end_date = date_range
                    mask = (dates.dt.date >= start_date) & (dates.dt.date <= end_date)
                    df_sessions = df_sessions[mask]
        
        # Exercise type filter
        with col2:
            st.markdown("**Exercise Type**")
            
            if 'exercise_type' in df_sessions.columns:
                exercise_types = ['All'] + sorted(df_sessions['exercise_type'].dropna().unique().tolist())
                selected_type = st.selectbox(
                    "Filter by type",
                    exercise_types,
                    label_visibility="collapsed"
                )
                
                if selected_type != 'All':
                    df_sessions = df_sessions[df_sessions['exercise_type'] == selected_type]
        
        # Gesture filter
        with col3:
            st.markdown("**Gesture**")
            
            if 'exercise_gesture' in df_sessions.columns:
                gestures = ['All'] + sorted(df_sessions['exercise_gesture'].dropna().unique().tolist())
                selected_gesture = st.selectbox(
                    "Filter by gesture",
                    gestures,
                    label_visibility="collapsed"
                )
                
                if selected_gesture != 'All':
                    df_sessions = df_sessions[df_sessions['exercise_gesture'] == selected_gesture]
        
        # Show filter summary
        total = len(df_sessions)
        if total > 0:
            st.info(f"Showing {total} session(s) matching filters")
    
    return df_sessions


def render_session_summary(selected_rows: pd.DataFrame):
    """
    Render summary statistics for selected sessions.
    
    Args:
        selected_rows: DataFrame of selected sessions
        
    TODO: Implement comprehensive session summary as per boss's requirements:
    - Day of week distribution (with color coding)
    - Time of day analysis (average session time)
    - Frequency patterns (sessions per day/week)
    - Duration statistics
    - Exercise type breakdown
    - Rep count averages
    - Trend indicators (improving/steady/declining)
    """
    if selected_rows.empty:
        return
    
    st.markdown("---")
    st.subheader("Session Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sessions", len(selected_rows))
    
    with col2:
        if 'duration_seconds' in selected_rows.columns:
            total_mins = selected_rows['duration_seconds'].sum() / 60
            st.metric("Total Duration", f"{total_mins:.1f} min")
    
    with col3:
        if 'reps_completed' in selected_rows.columns:
            total_reps = selected_rows['reps_completed'].sum()
            st.metric("Total Reps", int(total_reps))
    
    with col4:
        if 'duration_seconds' in selected_rows.columns:
            avg_duration = selected_rows['duration_seconds'].mean() / 60
            st.metric("Avg Duration", f"{avg_duration:.1f} min")
    
    # Placeholder for future detailed statistics
    with st.expander("🔍 Detailed Statistics (Coming Soon)"):
        st.info("""
        **Planned features:**
        - 📅 Day of week analysis with color coding
        - ⏰ Time of day patterns (morning/afternoon/evening)
        - 📊 Session frequency trends
        - 💪 EMG amplitude statistics
        - 🎯 Exercise quality indicators
        - 📈 Progress tracking over time
        """)


# TODO: Additional component functions
# def render_session_filters(df_sessions):
#     """Advanced filtering options for sessions."""
#     pass
#
# def render_session_comparison(sessions_list):
#     """Side-by-side comparison of multiple sessions."""
#     pass