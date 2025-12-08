# streamlit_pdf_ui.py
"""
Streamlit UI helpers for generating and downloading the Rehabilitation PDF.
Exports two functions:
- render_pdf_download_section(patient_name, selected_sessions_df, generator=None)
- render_quick_pdf_button(patient_name, selected_sessions_df, generator=None)
"""

import io
from datetime import datetime
import streamlit as st
import pandas as pd

from services.pdf_generator import RehabilitationReportGenerator, safe_filename

# default generator instance (reuse)
_default_generator = RehabilitationReportGenerator()

def render_pdf_download_section(
    patient_name: str,
    selected_sessions: pd.DataFrame,
    generator: RehabilitationReportGenerator = None
):
    """
    Renders a UI panel with options and a 'Generate PDF' button.
    Provides a downloadable PDF when generated.
    """
    if generator is None:
        generator = _default_generator

    st.markdown("---")
    st.subheader("📄 Generate PDF Report")

    if selected_sessions is None or selected_sessions.empty:
        st.info("Select sessions from the table to enable PDF generation.")
        return

    # Options layout
    col_a, col_b = st.columns(2)
    with col_a:
        include_summary = st.checkbox("Include summary metrics", value=True)
        include_details = st.checkbox("Include session details", value=True)
    with col_b:
        include_charts = st.checkbox("Include charts", value=True)
        include_trends = st.checkbox("Include trends section", value=True)

    # Optional text input for a human-friendly period or notes
    report_period = st.text_input("Report period (optional)", value="")

    # Generate button
    if st.button("🔄 Generate PDF report", use_container_width=True):
        with st.spinner("Generating PDF…"):
            try:
                pdf_buf = generator.generate_rehabilitation_report(
                    patient_name=patient_name or "Patient",
                    sessions_df=selected_sessions,
                    report_period=report_period or None,
                    include_summary=include_summary,
                    include_details=include_details,
                    include_temporal=True,
                    include_exercises=True,
                    include_trends=include_trends,
                    include_charts=include_charts
                )
                # Prepare download
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{safe_filename(patient_name or 'patient')}_report_{ts}.pdf"
                st.success("PDF ready — click to download below.")
                st.download_button(
                    label="💾 Download PDF",
                    data=pdf_buf,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {str(e)}")
                st.exception(e)

def render_quick_pdf_button(
    patient_name: str,
    selected_sessions: pd.DataFrame,
    generator: RehabilitationReportGenerator = None,
    button_label: str = "📄 Quick PDF"
) -> bool:
    """
    Single-click quick PDF generation with default options.
    Returns True if generated and a download button shown.
    """
    if generator is None:
        generator = _default_generator
    if selected_sessions is None or selected_sessions.empty:
        st.info("Select sessions first.")
        return False

    if st.button(button_label):
        try:
            pdf_buf = generator.generate_rehabilitation_report(
                patient_name=patient_name or "Patient",
                sessions_df=selected_sessions,
                include_summary=True,
                include_details=False,
                include_temporal=True,
                include_exercises=False,
                include_trends=False,
                include_charts=True
            )
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_filename(patient_name or 'patient')}_report_{ts}.pdf"
            st.download_button("💾 Download PDF", data=pdf_buf, file_name=filename, mime="application/pdf")
            return True
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
            st.exception(e)
            return False
    return False
