"""
Session visualization components.
Creates Altair charts for session statistics and patterns.
"""
import pandas as pd
import altair as alt
from typing import Dict, Any, Optional
from config import SESSION_CHART_HEIGHT_BARS, SESSION_CHART_HEIGHT_SCATTER
from services.mat_processor import extract_mat_field
from utils.formatters import parse_timestamp_string


def plot_session_statistics(data: Dict[str, Any]) -> Optional[alt.Chart]:
    """
    Create stacked charts showing session statistics over time.
    
    Creates three charts:
    1. Number of sessions per day
    2. Total session duration per day
    3. Time of day scatter plot
    
    Args:
        data: .mat file data dictionary with 'time' and 'duration_seconds'
        
    Returns:
        Combined Altair chart or None if no data
        
    TODO: Future enhancements for clinical insights:
    - Color code by day of week (as per boss's request)
    - Add average session time calculation
    - Show weekly patterns and trends
    - Add rep count statistics
    - Include EMG amplitude trends
    - Highlight behavioral patterns (morning/evening preference)
    """
    # Extract and parse data
    dates_raw = extract_mat_field(data, "time")
    duration_raw = extract_mat_field(data, "duration_seconds")
    
    dates = [parse_timestamp_string(str(d)) for d in dates_raw]
    durations = [float(d) if d not in (None, "") else float('nan') for d in duration_raw]
    
    # Create dataframe
    df = pd.DataFrame({
        "dt": dates,
        "duration_minutes": pd.Series(durations, dtype=float) / 60.0
    })
    df = df.dropna(subset=["dt"])
    
    if df.empty:
        return None
    
    # Add derived columns
    df["date_only"] = df["dt"].dt.date
    df["time_of_day_h"] = df["dt"].dt.hour + df["dt"].dt.minute / 60.0
    df["day_of_week"] = df["dt"].dt.day_name()  # For future color coding
    
    # Aggregate by day
    agg = df.groupby("date_only").agg(
        sessions=("dt", "count"),
        total_minutes=("duration_minutes", "sum")
    ).reset_index()
    agg["date_only_dt"] = pd.to_datetime(agg["date_only"])
    
    # Create charts
    chart1 = _create_sessions_per_day_chart(agg)
    chart2 = _create_duration_per_day_chart(agg)
    chart3 = _create_time_of_day_chart(df)
    
    # Combine with shared x-axis
    combined = alt.vconcat(chart1, chart2, chart3).resolve_scale(x="shared")
    
    return combined


def _create_sessions_per_day_chart(agg: pd.DataFrame) -> alt.Chart:
    """Create bar chart of session count per day."""
    return alt.Chart(agg).mark_bar().encode(
        x=alt.X("date_only_dt:T", title="Date"),
        y=alt.Y("sessions:Q", title="Sessions"),
        tooltip=["date_only_dt:T", "sessions:Q"]
    ).properties(
        height=SESSION_CHART_HEIGHT_BARS,
        title="Number of Sessions per Day"
    )


def _create_duration_per_day_chart(agg: pd.DataFrame) -> alt.Chart:
    """Create bar chart of total duration per day."""
    return alt.Chart(agg).mark_bar().encode(
        x=alt.X("date_only_dt:T", title="Date"),
        y=alt.Y("total_minutes:Q", title="Total Minutes"),
        tooltip=["date_only_dt:T", "total_minutes:Q"]
    ).properties(
        height=SESSION_CHART_HEIGHT_BARS,
        title="Total Session Duration per Day"
    )


def _create_time_of_day_chart(df: pd.DataFrame) -> alt.Chart:
    """Create scatter plot of session times throughout the day."""
    return alt.Chart(df).mark_circle(size=50).encode(
        x=alt.X("dt:T", title="Date"),
        y=alt.Y("time_of_day_h:Q", title="Time of Day (hours)"),
        tooltip=["dt:T", "time_of_day_h:Q", "day_of_week:N"]
    ).properties(
        height=SESSION_CHART_HEIGHT_SCATTER,
        title="Session Times per Day"
    )


# TODO: Additional visualization functions for clinical insights
# 
# def plot_day_of_week_analysis(sessions_df):
#     """
#     Show patterns by day of week with color coding.
#     - Which days are most active?
#     - Weekend vs weekday patterns
#     """
#     pass
#
# def plot_time_of_day_heatmap(sessions_df):
#     """
#     Heatmap showing preferred exercise times.
#     - Morning, afternoon, evening patterns
#     - Consistency over weeks
#     """
#     pass
#
# def plot_session_trends(sessions_df):
#     """
#     Trend lines showing progression over time.
#     - Increasing/decreasing session frequency
#     - Duration trends
#     - Rep count improvements
#     """
#     pass
#
# def plot_emg_amplitude_trends(sessions_with_emg):
#     """
#     Track EMG amplitude statistics over sessions.
#     - Average amplitude per session
#     - Peak amplitudes
#     - Consistency metrics
#     """
#     pass
#
# def plot_exercise_type_breakdown(sessions_df):
#     """
#     Pie/bar charts showing distribution of exercise types.
#     - Which gestures are practiced most?
#     - Balance across exercise types
#     """
#     pass
