"""
Centralized info notes for the weather analytics dashboard.
All informational messages, warnings, and help text are stored here for consistency.
"""

PAGE_NOTES = {
    # Home page notes
    "dashboard_overview": (
        "This dashboard demonstrates a weather data pipeline with layered processing: "
        "raw ingestion (bronze), cleaned and validated data (silver), and aggregated analytical tables (gold). "
        "It supports data exploration, quality assessment, and anomaly detection."
    ),

    "scientific_exploration": """
    Possible analyses include:
    - comparing stations across time and weather conditions
    - identifying missingness or sensor inconsistencies
    - exploring relationships between humidity, dew point, precipitation, and pressure
    - detecting statistically unusual observations
    - comparing raw-resolution patterns with hourly or daily aggregates
    """,

    # Data Explorer page notes
    "data_explorer_intro": (
        "Use this page to explore weather variables across stations and time periods. "
        "Lower resolutions such as hourly or daily are often better for trend interpretation, "
        "while 10-minute data is useful for short-term variability and quality inspection."
    ),

    "select_at_least_one_metric": "Select at least one metric.",
    "combined_plot_note": "With 2 or fewer metrics selected, showing combined plot.",

    # Data Quality page notes
    "data_quality_intro": (
        "This page summarizes data quality checks applied during preprocessing. "
        "The goal is not only to detect missing values, but also to identify implausible or internally inconsistent observations."
    ),

    # Anomalies page notes
    "anomaly_intro": (
        "Anomalies shown here are statistical anomalies, not automatically mistakes. "
        "A flagged value is one that deviates strongly from its recent local baseline for the same station and variable."
    ),

    "no_anomalies_found": "No anomalies found for the selected filters.",
    "no_anomaly_columns": "No anomaly columns found yet for this resolution.",

    # General warnings
    "silver_dataset_not_found": "Silver dataset not found. Run the pipeline first.",
    "no_data_found_resolution": "No data found for resolution: {resolution}",
    "no_data_after_station_filter": "No data available after station filtering.",
    "no_data_in_time_period": "No data available in the selected time period.",
}

# Helper function to format notes with variables
def format_note(note_key: str, **kwargs) -> str:
    """Format a note with variable substitution."""
    note = PAGE_NOTES.get(note_key, "")
    if isinstance(note, str) and kwargs:
        return note.format(**kwargs)
    return note