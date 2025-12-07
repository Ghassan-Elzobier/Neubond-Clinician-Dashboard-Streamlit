"""
EMG visualization components.
Creates matplotlib figures for EMG channel data with phase shading.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, Any, Optional
from config import (
    EMG_CHANNEL_OFFSET, EMG_FIGURE_SIZE, EMG_LINE_WIDTH, 
    EMG_GAP_DETECTION_FACTOR, PHASE_COLORS
)
from utils.data_processing import prepare_emg_data, break_gaps_mask


def plot_emg_channels(
    data: Dict[str, Any], 
    title: str = "EMG Channels over Time"
) -> plt.Figure:
    """
    Create an EMG channel plot with offset channels and phase shading.
    
    Args:
        data: Dictionary with 'emg', 'timestamps', optionally 'exercise_phase'
        title: Plot title
        
    Returns:
        Matplotlib figure object
        
    TODO: Future enhancements for clinical insights:
    - Add channel labels on left side (as per boss's request)
    - Display gesture and active channel info
    - Add EMG amplitude statistics overlay
    - Highlight co-contraction events
    - Add quality indicators (signal-to-noise ratio)
    """
    # Prepare and validate data
    prepared = prepare_emg_data(data)
    times = prepared["times"]
    emg_num = prepared["emg_num"]
    phase_arr = prepared["phase_arr"]
    
    # Handle empty data
    if not times.size or not emg_num.size:
        return _create_empty_plot("No EMG data to display")
    
    # Detect gaps for line breaking
    gap_mask = break_gaps_mask(times, factor=EMG_GAP_DETECTION_FACTOR)
    
    # Create figure
    fig, ax = plt.subplots(figsize=EMG_FIGURE_SIZE)
    n_channels = emg_num.shape[1]
    
    # Add phase shading first (background layer)
    if phase_arr is not None:
        _add_phase_shading(ax, times, phase_arr)
    
    # Plot channels with offset
    channel_handles = _plot_channels(ax, times, emg_num, n_channels, gap_mask)
    
    # Configure axes
    ax.set_xlabel("Time")
    ax.set_ylabel("EMG Channels (offset)")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    # Create legend (reversed channels + phase patches)
    _add_legend(ax, channel_handles, n_channels, phase_arr is not None)
    
    # Format x-axis for dates
    fig.autofmt_xdate(rotation=30)
    
    return fig


def _create_empty_plot(message: str) -> plt.Figure:
    """Create a figure displaying a message when no data available."""
    fig = plt.figure(figsize=EMG_FIGURE_SIZE)
    plt.text(0.5, 0.5, message, ha="center", va="center", fontsize=12)
    plt.axis('off')
    return fig


def _add_phase_shading(ax: plt.Axes, times: np.ndarray, phase_arr: np.ndarray):
    """Add colored background shading for exercise phases."""
    # Build contiguous spans of identical phase
    spans = []
    start_idx = 0
    current = phase_arr[0]
    
    for i in range(1, len(phase_arr)):
        if phase_arr[i] != current:
            spans.append((start_idx, i - 1, current))
            current = phase_arr[i]
            start_idx = i
    spans.append((start_idx, len(phase_arr) - 1, current))
    
    # Draw spans
    for s_idx, e_idx, label in spans:
        start_t = times[s_idx]
        end_t = times[e_idx]
        color = PHASE_COLORS.get(label.lower(), "#888888")
        ax.axvspan(start_t, end_t, color=color, alpha=0.25, zorder=0)


def _plot_channels(
    ax: plt.Axes, 
    times: np.ndarray, 
    emg_num: np.ndarray, 
    n_channels: int, 
    gap_mask: np.ndarray
) -> list:
    """Plot all EMG channels with vertical offset."""
    channel_handles = []
    
    for ch in range(n_channels):
        y = emg_num[:, ch]
        y_shifted = y + ch * EMG_CHANNEL_OFFSET
        
        # Use masked array to break lines at gaps
        y_masked = np.ma.masked_array(y_shifted, mask=gap_mask)
        
        handle, = ax.plot(
            times, 
            y_masked, 
            label=f"Ch {ch+1}", 
            linewidth=EMG_LINE_WIDTH, 
            zorder=1
        )
        channel_handles.append(handle)
    
    return channel_handles


def _add_legend(
    ax: plt.Axes, 
    channel_handles: list, 
    n_channels: int, 
    include_phases: bool
):
    """Add legend with reversed channel order and phase patches."""
    # Reversed channel legend (top channel first)
    rev_handles = list(reversed(channel_handles))
    rev_labels = [f"Ch {i}" for i in range(n_channels, 0, -1)]
    
    legend_handles = rev_handles.copy()
    legend_labels = rev_labels.copy()
    
    # Add phase legend patches
    if include_phases:
        phase_patches = [
            mpatches.Patch(color=color, alpha=0.25, label=name.capitalize())
            for name, color in PHASE_COLORS.items()
        ]
        legend_handles.extend(phase_patches)
        legend_labels.extend([p.get_label() for p in phase_patches])
    
    if legend_handles:
        ax.legend(legend_handles, legend_labels, loc="upper right", fontsize="small")


# TODO: Additional plotting functions for clinical insights
# def plot_emg_statistics_overlay(ax, emg_data, stats):
#     """Overlay statistical markers (mean, std, thresholds)."""
#     pass
#
# def plot_channel_comparison(data, channels_to_compare):
#     """Side-by-side comparison of specific channels."""
#     pass
#
# def plot_emg_quality_indicators(data):
#     """Visual indicators of signal quality and artifacts."""
#     pass
