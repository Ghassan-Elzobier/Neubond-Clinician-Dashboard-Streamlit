# Neubond Clinician Dashboard

A Streamlit web application for analyzing EMG (electromyography) and exercise session data. Built for clinical teams to visualize patient exercise patterns, EMG signals, and track rehabilitation progress.

## 🎯 Features

### Current Features
- **Patient Selection**: Browse and select patients from Supabase database
- **Session Management**: View, filter, and select exercise sessions
- **EMG Visualization**: Multi-channel EMG plots with phase shading (rest/attempt)
- **Session Statistics**: Charts showing sessions per day, duration, and timing patterns
- **Data Export**: Export to CSV and .mat formats
- **File Upload**: Support for offline analysis via .mat file uploads

### Planned Features (Easy to Add with Current Structure)
- ✅ Day of week analysis with color coding
- ✅ Average session time calculations
- ✅ EMG amplitude statistics alongside session logs
- ✅ Co-contraction detection
- ✅ Trend analysis (improving/steady/declining)
- ✅ Exercise quality indicators
- ✅ Time-of-day behavioral patterns

## 📁 Project Structure

```
neubond_dashboard/
├── app.py                      # Main application entry point
├── config.py                   # Configuration and constants
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env.example                # Environment variables template
│
├── services/
│   ├── __init__.py
│   ├── supabase_client.py     # Database interactions (cached)
│   └── mat_processor.py       # .mat file handling
│
├── utils/
│   ├── __init__.py
│   ├── data_processing.py     # Data transformation utilities
│   └── formatters.py          # Formatting helpers (timestamps, etc.)
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py             # Sidebar UI components
│   ├── session_table.py       # Session table display
│   └── export_handlers.py     # Export functionality
│
└── visualizations/
    ├── __init__.py
    ├── emg_plots.py           # EMG plotting with matplotlib
    └── session_plots.py       # Session statistics with Altair
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Supabase account (optional, for database features)

### Installation

1. **Clone or download the project**
   ```bash
   cd neubond_dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## ⚙️ Configuration

### Environment Variables (.env)
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_anon_key
```

### App Configuration (config.py)
Customize visual parameters:
- EMG channel offset spacing
- Figure sizes
- Color schemes for phases
- Chart heights
- Timestamp formats

## 📊 Usage

### Basic Workflow

1. **Select a Patient**
   - Use sidebar to choose patient from dropdown
   - Or upload a .mat file for offline analysis

2. **View Sessions**
   - Sessions table shows all exercise sessions
   - Timestamps are formatted for readability
   - Select one or more sessions for analysis

3. **Export Data**
   - CSV: Detailed datapoints from all selected sessions
   - Sessions .mat: Session metadata
   - EMG .mat: Raw EMG channel data

4. **Visualize**
   - **Session Statistics**: Patterns over time (frequency, duration, timing)
   - **EMG Analysis**: Multi-channel plots with exercise phase shading
   - Color-coded phases (red=attempt, blue=rest)

### Working Offline
Upload .mat files in the sidebar to analyze data without Supabase connection.

## 🔧 Adding Clinical Features

The codebase is structured to make adding your boss's requested features straightforward:

### 1. Day of Week Analysis
**Location**: `visualizations/session_plots.py`
```python
def plot_day_of_week_analysis(sessions_df):
    # Add color coding by day
    # Show which days are most active
    # Weekend vs weekday patterns
```

### 2. Time-of-Day Statistics
**Location**: `utils/data_processing.py`
```python
def calculate_session_statistics(sessions):
    # Average session time by hour
    # Morning/afternoon/evening breakdown
```

### 3. EMG Statistics
**Location**: `visualizations/emg_plots.py`
```python
def plot_emg_statistics_overlay(emg_data):
    # Amplitude statistics
    # Channel-specific metrics
    # Quality indicators
```

### 4. Co-contraction Detection
**Location**: `utils/data_processing.py`
```python
def detect_cocontraction(emg_data):
    # Identify unintended muscle activation
    # Flag problematic patterns
```

### 5. Trend Analysis
**Location**: `visualizations/session_plots.py`
```python
def plot_session_trends(sessions_df):
    # Increasing/decreasing frequency
    # Rep count improvements
    # Duration trends
```

## 🎨 Customization

### Adjust EMG Plot Appearance
**File**: `config.py`
```python
EMG_CHANNEL_OFFSET = 2000  # Vertical spacing between channels
PHASE_COLORS = {
    "attempt": "#ff6b6b",  # Red for exercise attempts
    "rest": "#6ba4ff"       # Blue for rest periods
}
```

### Modify Timestamp Display
**File**: `config.py`
```python
TIMESTAMP_DISPLAY_FORMAT = "%Y-%m-%d %H:%M:%S"
```

## 🐛 Known Issues & Fixes

### ✅ Fixed Issues
- **CSV Download Bug**: Now uses proper Streamlit download buttons with session state
- **Timestamp Readability**: Formatted display in session table with `format_timestamp_for_display()`

### Potential Improvements
- Add session filtering (date range, exercise type)
- Implement caching for large EMG datasets
- Add data validation warnings
- Create session comparison views

## 🔒 Security & Deployment

### Adding Authentication
When ready to deploy, uncomment in `requirements.txt`:
```python
streamlit-authenticator>=0.2.0
```

Then add to `app.py`:
```python
import streamlit_authenticator as stauth
# Configure authenticator before main content
```

### Deployment Options
- **Streamlit Cloud**: Free hosting (connect GitHub repo)
- **Local Network**: Run on clinic server
- **Docker**: Containerize for portability

## 📝 Best Practices Implemented

✅ **Caching**: `@st.cache_data` on expensive operations
✅ **Modular Code**: Clear separation of concerns
✅ **Type Hints**: Better IDE support and clarity  
✅ **Error Handling**: Graceful failures with user feedback
✅ **Documentation**: Inline comments and docstrings
✅ **Configuration**: Centralized in `config.py`
✅ **TODO Comments**: Clear markers for future features

## 🤝 Contributing

When adding features:
1. Follow the existing module structure
2. Add functions to appropriate files
3. Update config.py for new constants
4. Add TODO comments for future enhancements
5. Test with both Supabase and offline modes

## 📚 Dependencies

- **streamlit**: Web app framework
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **matplotlib**: EMG plotting
- **altair**: Interactive session charts
- **scipy**: .mat file handling
- **supabase**: Database client
- **python-dotenv**: Environment management

## 📄 License

[Add your license here]

## 👥 Team

Created for clinical analysis of rehabilitation exercise data.

---

*For questions or issues, contact your development team.*
