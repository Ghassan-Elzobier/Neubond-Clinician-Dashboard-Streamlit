# Migration Guide: Refactored Neubond Dashboard

## 🎯 Overview

This guide explains the refactoring changes, fixes applied, and how to work with the new modular structure.

## ✅ Issues Fixed

### 1. CSV Download Bug - FIXED ✓
**Problem**: Button clicks weren't properly triggering downloads

**Solution**: 
- Moved export logic to dedicated `components/export_handlers.py`
- Used proper Streamlit download button pattern
- Separated button click from download action
- Fixed button state management

**Before**:
```python
if export_csv_click:
    # Complex logic mixed with UI
    st.download_button(...)  # Often didn't work
```

**After**:
```python
# Clean separation in export_handlers.py
def handle_export_buttons(selected_rows, patient_name):
    if st.button("Export CSV"):
        csv_bytes = export_sessions_csv(...)
        st.download_button("Download", data=csv_bytes, ...)
```

### 2. Timestamp Readability - FIXED ✓
**Problem**: Raw ISO timestamps hard to read

**Solution**:
- Added `format_timestamp_for_display()` in `utils/formatters.py`
- Automatic formatting in session table
- Configurable format in `config.py`

**Before**: `2024-11-15T14:30:25.123456+00:00`  
**After**: `2024-11-15 14:30:25` or `11/15 14:30` (configurable)

### 3. Performance Optimization - IMPROVED ✓
**Problem**: Repeated database queries

**Solution**:
- Added `@st.cache_data` decorators in `services/supabase_client.py`
- 5-minute cache for patients, 1-minute for sessions
- Reduces load times significantly

## 📦 New Project Structure

### Before (Single File)
```
app_streamlit.py  (500+ lines)
```

### After (Modular)
```
neubond_dashboard/
├── app.py                      # Main entry (100 lines)
├── config.py                   # All constants
├── requirements.txt
├── README.md
├── .env.example
│
├── services/                   # External interactions
│   ├── supabase_client.py     # DB queries (cached)
│   └── mat_processor.py       # File handling
│
├── utils/                      # Pure functions
│   ├── data_processing.py     # Transformations
│   └── formatters.py          # Display formatting
│
├── components/                 # UI elements
│   ├── sidebar.py             # Patient selection
│   ├── session_table.py       # Table display
│   └── export_handlers.py     # Export buttons
│
└── visualizations/             # Plotting
    ├── emg_plots.py           # EMG charts
    └── session_plots.py       # Session stats
```

## 🔄 Where Things Moved

### Configuration
```python
# OLD: Scattered throughout app_streamlit.py
SUPABASE_URL = os.getenv(...)
offset = 2000
phase_colors = {"attempt": "#ff6b6b", ...}

# NEW: config.py
from config import SUPABASE_URL, EMG_CHANNEL_OFFSET, PHASE_COLORS
```

### Data Fetching
```python
# OLD: app_streamlit.py
def fetch_patients():
    resp = supabase.table(...).execute()
    return resp.data

# NEW: services/supabase_client.py
from services.supabase_client import fetch_patients

@st.cache_data(ttl=300)  # Cached!
def fetch_patients():
    ...
```

### Formatting
```python
# OLD: Mixed with app logic
def safe_filename(s):
    ...
def parse_timestamp_string(ts):
    ...

# NEW: utils/formatters.py
from utils.formatters import safe_filename, format_timestamp_for_display
```

### Plotting
```python
# OLD: All plotting in app_streamlit.py
def plot_emg_matplotlib(data, title):
    # 100+ lines

# NEW: visualizations/emg_plots.py
from visualizations.emg_plots import plot_emg_channels
fig = plot_emg_channels(data, title="My Title")
```

## 🚀 How to Add New Features

### Example: Adding Day-of-Week Analysis

**1. Add configuration** (`config.py`):
```python
# Day of Week Colors
DAY_COLORS = {
    "Monday": "#FF6B6B",
    "Tuesday": "#4ECDC4",
    # ... etc
}
```

**2. Add data processing** (`utils/data_processing.py`):
```python
def calculate_day_of_week_stats(sessions_df):
    """Calculate sessions per day of week."""
    df = sessions_df.copy()
    df['day_of_week'] = df['start_time'].dt.day_name()
    return df.groupby('day_of_week').size()
```

**3. Add visualization** (`visualizations/session_plots.py`):
```python
def plot_day_of_week_analysis(sessions_df):
    """Bar chart colored by day of week."""
    stats = calculate_day_of_week_stats(sessions_df)
    
    chart = alt.Chart(stats).mark_bar().encode(
        x='day_of_week',
        y='sessions',
        color=alt.Color('day_of_week', scale=alt.Scale(
            domain=list(DAY_COLORS.keys()),
            range=list(DAY_COLORS.values())
        ))
    )
    return chart
```

**4. Use in app** (`app.py`):
```python
from visualizations.session_plots import plot_day_of_week_analysis

# In render_session_statistics_tab():
if not selected_rows.empty:
    st.subheader("Day of Week Analysis")
    chart = plot_day_of_week_analysis(selected_rows)
    st.altair_chart(chart)
```

## 📋 Common Tasks in New Structure

### Add a New Export Format
**File**: `components/export_handlers.py`
```python
def export_sessions_json(selected_rows, patient_name):
    """Export sessions as JSON."""
    import json
    data = selected_rows.to_dict('records')
    return json.dumps(data, indent=2).encode('utf-8')

# Add button in handle_export_buttons()
```

### Add a New Supabase Query
**File**: `services/supabase_client.py`
```python
@st.cache_data(ttl=60)
def fetch_patient_summary(patient_id: str):
    """Fetch summary statistics for a patient."""
    resp = supabase.rpc('get_patient_summary', {
        'patient_id': patient_id
    }).execute()
    return resp.data
```

### Add a New Visualization
**File**: `visualizations/emg_plots.py` or `session_plots.py`
```python
def plot_emg_heatmap(emg_data):
    """Create heatmap of EMG activity."""
    import seaborn as sns
    fig, ax = plt.subplots()
    sns.heatmap(emg_data['emg'].T, ax=ax)
    return fig
```

### Add a New Utility Function
**File**: `utils/data_processing.py`
```python
def calculate_emg_quality_score(emg_data):
    """Calculate signal quality metrics."""
    # SNR calculation
    # Artifact detection
    return quality_dict
```

## 🎨 Customization Guide

### Change Colors
**File**: `config.py`
```python
PHASE_COLORS = {
    "attempt": "#your_color",
    "rest": "#your_color"
}
```

### Adjust Caching
**File**: `services/supabase_client.py`
```python
@st.cache_data(ttl=300)  # Change TTL (seconds)
```

### Modify Table Display
**File**: `components/session_table.py`
```python
# In prepare_session_dataframe():
# Add/remove columns
# Change formatting
```

## 🐛 Debugging Tips

### Check What's Cached
```python
# In app.py or any module:
st.write("Cache info:", fetch_patients.cache_info())
```

### Clear Cache
```python
# Add button in sidebar:
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.rerun()
```

### View Session State
```python
# Add to sidebar for debugging:
with st.expander("Debug: Session State"):
    st.write(st.session_state)
```

## ⚠️ Important Notes

### Import Order
Always import in this order:
```python
# 1. Standard library
import os
from typing import Dict

# 2. Third party
import streamlit as st
import pandas as pd

# 3. Local modules
from config import APP_TITLE
from services.supabase_client import fetch_patients
```

### Module Dependencies
```
app.py
  ↓
components/* ← uses → services/*
  ↓                      ↓
visualizations/*  ←  utils/*
```

**Rule**: Lower layers (utils, services) should NOT import from higher layers (components, app)

### When to Use Cache
- ✅ Database queries
- ✅ File parsing
- ✅ Expensive computations
- ❌ UI state
- ❌ User selections

## 📚 Next Steps

### Immediate Tasks
1. ✅ Create directory structure
2. ✅ Copy files into modules
3. ✅ Test app runs
4. ✅ Verify exports work
5. ✅ Check visualizations

### Future Enhancements (Easy Now!)
- [ ] Day of week color coding
- [ ] Time-of-day statistics
- [ ] EMG amplitude stats
- [ ] Co-contraction detection
- [ ] Trend analysis
- [ ] Authentication

## 💡 Pro Tips

1. **Use TODO comments**: Every TODO in the code marks where to add clinical features

2. **Follow the pattern**: Look at existing functions to see how to add similar ones

3. **Test incrementally**: Add one feature at a time

4. **Keep config.py updated**: Any magic number should go there

5. **Document as you go**: Add docstrings to new functions

## 🤝 Getting Help

- **Can't find where something is?** Use VSCode's "Find in Files" (Ctrl+Shift+F)
- **Import errors?** Check if `__init__.py` exists in each directory
- **Cache issues?** Add `.clear()` button temporarily
- **Still stuck?** Check the README.md for examples

---

**Summary**: The refactor makes the codebase ~10x easier to maintain and extend. Every clinical insight your boss wants can now be added in 10-20 lines instead of hunting through a 500-line file!
