# generator.py
"""
RehabilitationReportGenerator
Generates a compact multi-page PDF report with optional charts embedded as PNGs.

Uses:
- reportlab for PDF layout
- matplotlib for charts (rendered to PNGs)
- pandas/numpy for data handling

Public:
- RehabilitationReportGenerator.generate_rehabilitation_report(...)
"""

import io
from datetime import datetime
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.enums import TA_CENTER

# -------------------------
# Utility helpers
# -------------------------
def safe_filename(s: str) -> str:
    s = (s or "").strip()
    import re
    s = re.sub(r"\s+", "_", s)
    return re.sub(r"[^A-Za-z0-9._-]", "", s)

def fig_to_png_bytes(fig, dpi=150):
    """Render a matplotlib figure to PNG bytes and close the figure."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    return buf

# -------------------------
# Report generator class
# -------------------------
class RehabilitationReportGenerator:
    def __init__(self, page_size=letter):
        self.page_size = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2980b9'),
            spaceBefore=8,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='Small',
            parent=self.styles['Normal'],
            fontSize=9
        ))

    # -------------------------
    # Public generator entry point
    # -------------------------
    def generate_rehabilitation_report(
        self,
        patient_name: str,
        sessions_df: pd.DataFrame,
        report_period: Optional[str] = None,
        include_summary: bool = True,
        include_details: bool = True,
        include_temporal: bool = True,
        include_exercises: bool = True,
        include_trends: bool = True,
        include_charts: bool = True
    ) -> io.BytesIO:
        """
        Create PDF bytes for the provided sessions DataFrame.

        sessions_df: pandas DataFrame expected to have at least:
            - start_time (ISO string or datetime)
            - duration_seconds (numeric)
            - reps_completed (numeric) optional
            - exercise_type, exercise_gesture (optional)
            - any other clinical columns used for tables/charts

        Returns BytesIO.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=self.page_size,
            leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50
        )

        story = []
        # Header
        story.append(Paragraph("Clinical Rehabilitation Report", self.styles['ReportTitle']))
        info_text = f"<b>Patient:</b> {patient_name} | <b>Generated:</b> {datetime.now().strftime('%d %b %Y %H:%M')}"
        if report_period:
            info_text += f" | <b>Period:</b> {report_period}"
        story.append(Paragraph(info_text, self.styles['Small']))
        story.append(Spacer(1, 0.12 * inch))

        # Summary metrics + chart (page 1)
        if include_summary:
            story.append(Paragraph("Key Metrics", self.styles['SectionHeader']))
            story.extend(self._build_key_metrics_block(sessions_df))

        if include_charts and include_temporal:
            # Time-of-day / daily frequency chart
            fig1 = self._plot_activity_over_time(sessions_df)
            if fig1:
                png = fig_to_png_bytes(fig1)
                story.append(Image(png, width=6.5*inch, height=2.0*inch))
                story.append(Spacer(1, 0.12 * inch))

        # Exercises section
        if include_exercises:
            story.append(Paragraph("Exercise Breakdown", self.styles['SectionHeader']))
            story.extend(self._build_exercises_block(sessions_df))
            story.append(Spacer(1, 0.1 * inch))

        # Optionally add a new page for trends & recommendations
        if include_trends:
            story.append(PageBreak())
            story.append(Paragraph("Trends & Assessment", self.styles['SectionHeader']))
            story.extend(self._build_trends_block(sessions_df))
            if include_charts:
                fig2 = self._plot_trend_reps_over_time(sessions_df)
                if fig2:
                    png2 = fig_to_png_bytes(fig2)
                    story.append(Image(png2, width=6.5*inch, height=2.2*inch))
                    story.append(Spacer(1, 0.12 * inch))
            # Clinical notes / recommendations
            story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
            recs = self._generate_recommendations(sessions_df)
            for r in recs:
                story.append(Paragraph(f"• {r}", self.styles['Normal']))

        # Detailed session table (if requested) appended at end
        if include_details:
            story.append(PageBreak())
            story.append(Paragraph("Session Details", self.styles['SectionHeader']))
            story.extend(self._build_session_table(sessions_df))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    # -------------------------
    # Sections building helpers
    # -------------------------
    def _build_key_metrics_block(self, df: pd.DataFrame):
        out = []
        if df is None or df.empty:
            out.append(Paragraph("No data available.", self.styles['Normal']))
            return out

        df2 = df.copy()
        # Normalize start_time column if present
        if 'start_time' in df2.columns:
            df2['start_time'] = pd.to_datetime(df2['start_time'], errors='coerce')
        total_sessions = len(df2)
        active_days = df2['start_time'].dt.date.nunique() if 'start_time' in df2.columns else 0
        avg_duration = (df2['duration_seconds'].dropna().mean() / 60.0) if 'duration_seconds' in df2.columns else 0.0
        total_reps = int(df2['reps_completed'].dropna().sum()) if 'reps_completed' in df2.columns else 0
        avg_reps = df2['reps_completed'].dropna().mean() if 'reps_completed' in df2.columns else 0.0
        sessions_per_day = total_sessions / max(active_days, 1)

        metrics_data = [
            ['Total Sessions', str(total_sessions), 'Active Days', str(active_days)],
            ['Avg Session Duration (min)', f"{avg_duration:.1f}", 'Sessions/Day', f"{sessions_per_day:.2f}"],
            ['Total Reps', str(total_reps), 'Avg Reps/Session', f"{avg_reps:.1f}"]
        ]
        table = Table(metrics_data, colWidths=[2.2*inch, 1.0*inch, 1.6*inch, 1.0*inch])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0),(0,-1), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (2,0),(2,-1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (1,0),(1,-1), 'CENTER'),
            ('ALIGN', (3,0),(3,-1), 'CENTER')
        ]))
        out.append(table)
        return out

    def _build_exercises_block(self, df: pd.DataFrame):
        out = []
        if df is None or df.empty:
            out.append(Paragraph("No data available.", self.styles['Normal']))
            return out
        # Top exercise types table
        if 'exercise_type' in df.columns:
            top = df['exercise_type'].value_counts().head(6)
            rows = [['Exercise', 'Count', '%']]
            total = len(df)
            for k, v in top.items():
                rows.append([str(k), str(v), f"{(v/total*100):.0f}%"])
            table = Table(rows, colWidths=[2.5*inch, 1*inch, 1*inch])
            table.setStyle(self._compact_table_style())
            out.append(table)
        # Gestures summary text
        if 'exercise_gesture' in df.columns:
            top_g = df['exercise_gesture'].value_counts().head(6)
            out.append(Spacer(1, 6))
            out.append(Paragraph("Top Gestures: " + ", ".join([f"{g} ({c})" for g, c in top_g.items()]), self.styles['Normal']))
        return out

    def _build_trends_block(self, df: pd.DataFrame):
        out = []
        if df is None or len(df) < 2:
            out.append(Paragraph("Insufficient data for trends.", self.styles['Normal']))
            return out
        # Simple early vs late comparison
        n = len(df)
        mid = n // 2
        df2 = df.copy()
        if 'start_time' in df2.columns:
            df2['start_time'] = pd.to_datetime(df2['start_time'], errors='coerce')
            df2 = df2.sort_values('start_time')
        early, late = df2.iloc[:mid], df2.iloc[mid:]
        def mean_or_na(s):
            try:
                return float(s.dropna().mean())
            except Exception:
                return float('nan')
        early_reps = mean_or_na(early['reps_completed']) if 'reps_completed' in df2.columns else float('nan')
        late_reps = mean_or_na(late['reps_completed']) if 'reps_completed' in df2.columns else float('nan')
        rows = [['Metric', 'Early', 'Recent', 'Change']]
        rows.append(['Avg Reps', f"{early_reps:.1f}" if not np.isnan(early_reps) else 'N/A',
                     f"{late_reps:.1f}" if not np.isnan(late_reps) else 'N/A',
                     f"{((late_reps - early_reps)/early_reps*100):+.0f}%" if early_reps and not np.isnan(early_reps) else 'N/A'])
        table = Table(rows, colWidths=[2.2*inch, 1.0*inch, 1.0*inch, 1.0*inch])
        table.setStyle(self._compact_table_style())
        out.append(table)
        return out

    def _build_session_table(self, df: pd.DataFrame):
        out = []
        if df is None or df.empty:
            out.append(Paragraph("No sessions to display.", self.styles['Normal']))
            return out
        # keep columns reasonably short for PDF
        display_cols = list(df.columns[:8])  # limit wide tables
        header = [c.replace('_', ' ').title() for c in display_cols]
        rows = [header]
        for _, r in df.iterrows():
            row = []
            for c in display_cols:
                v = r.get(c, '')
                # small formatting
                if pd.isna(v):
                    row.append('')
                else:
                    row.append(str(v))
            rows.append(row)
        tbl = Table(rows, repeatRows=1, colWidths=[(6.5*inch)/len(display_cols)]*len(display_cols))
        tbl.setStyle(self._compact_table_style())
        out.append(tbl)
        return out

    # -------------------------
    # Chart generators (matplotlib) -> return fig or None
    # -------------------------
    def _plot_activity_over_time(self, df: pd.DataFrame):
        if df is None or df.empty: return None
        if 'start_time' not in df.columns:
            # try 'time' or leave
            if 'time' in df.columns:
                df2 = df.copy(); df2['start_time'] = pd.to_datetime(df2['time'], errors='coerce')
            else:
                return None
        else:
            df2 = df.copy(); df2['start_time'] = pd.to_datetime(df2['start_time'], errors='coerce')

        df2 = df2.dropna(subset=['start_time'])
        if df2.empty: return None

        # sessions per day
        df2['date'] = df2['start_time'].dt.date
        per_day = df2.groupby('date').size()
        # times of day histogram (hour)
        df2['hour'] = df2['start_time'].dt.hour

        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 2.4), constrained_layout=True)
        # left: sessions per day (bar)
        ax[0].bar(per_day.index.astype('O'), per_day.values, color='#4e79a7')
        ax[0].set_title('Sessions per Day')
        ax[0].tick_params(axis='x', rotation=45)
        # right: histogram of hour
        ax[1].hist(df2['hour'].dropna().astype(int), bins=range(0,25), color='#f28e2b')
        ax[1].set_title('Session Hour Distribution')
        ax[1].set_xlabel('Hour of day')
        ax[1].set_xlim(0,24)
        return fig

    def _plot_trend_reps_over_time(self, df: pd.DataFrame):
        if df is None or 'reps_completed' not in df.columns: return None
        df2 = df.copy()
        if 'start_time' in df2.columns:
            df2['start_time'] = pd.to_datetime(df2['start_time'], errors='coerce')
            df2 = df2.sort_values('start_time')
            x = df2['start_time']
        else:
            x = pd.RangeIndex(len(df2))
        y = pd.to_numeric(df2['reps_completed'], errors='coerce')
        if y.dropna().empty: return None
        fig, ax = plt.subplots(figsize=(6.5, 2.2))
        ax.plot(x, y, marker='o', linewidth=1.0)
        ax.set_title('Reps over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Reps')
        fig.autofmt_xdate()
        return fig

    # -------------------------
    # Small helpers
    # -------------------------
    def _compact_table_style(self):
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ])

    def _generate_recommendations(self, df: pd.DataFrame):
        recs = []
        if df is None or df.empty:
            recs.append("No data available to generate recommendations.")
            return recs
        # Simple heuristic recommendations (demo)
        if 'reps_completed' in df.columns:
            mean_reps = pd.to_numeric(df['reps_completed'], errors='coerce').dropna().mean()
            if mean_reps < 5:
                recs.append("Consider increasing target repetitions per session to improve dosing.")
            else:
                recs.append("Repetition count is reasonable; consider focusing on progression over weeks.")
        if 'duration_seconds' in df.columns:
            avg_min = pd.to_numeric(df['duration_seconds'], errors='coerce').dropna().mean()/60
            if avg_min < 5:
                recs.append("Sessions are short — ensure minimum therapeutic dose is met.")
        recs.append("Review signal quality for any sessions with few valid EMG samples.")
        return recs
