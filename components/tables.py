import streamlit as st
import pandas as pd
import numpy as np
from config.settings import EFFECTIVE_METRICS_NOTE

def render_effective_metrics_note():
    """Render the note explaining eSR, eControl, eAerial"""
    st.markdown("""
        <div class="metrics-note">
            <p><strong>eSR</strong>: Measure of the selected batter's effective SR in comparison to an average batter.</p>
            <p><strong>eControl</strong>: Measure of the selected batter's effective Control in comparison to an average batter.</p>
            <p><strong>eAerial</strong>: Measure of the selected batter's effective Aerial shots frequency in comparison to an average batter.</p>
            <p class="note-sub"><em>(An average batter is a crude quantification of all batters involved in the matches for which the selected batter and set of filters have been chosen.)</em></p>
        </div>
    """, unsafe_allow_html=True)

def format_dataframe(df, effective_cols=['eSR', 'eControl', 'eAerial']):
    """Format dataframe for display with proper styling"""
    if df is None or len(df) == 0:
        return df
    
    df_display = df.copy()
    
    # Round numeric columns to 2 decimal places
    numeric_cols = df_display.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if col not in effective_cols:
            df_display[col] = df_display[col].apply(
                lambda x: f"{x:.2f}" if pd.notna(x) and x != float('inf') and x != float('-inf') else "-"
            )
    
    # Format effective metrics with sign and color
    for col in effective_cols:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(format_effective_value)
    
    return df_display

def format_effective_value(value):
    """Format effective metric value with sign"""
    if pd.isna(value) or value == float('inf') or value == float('-inf'):
        return "-"
    if value > 0:
        return f"+{value:.2f}"
    else:
        return f"{value:.2f}"

def get_sortable_table_js():
    """Return JavaScript for sortable tables"""
    return """
    <script>
    function sortTable(tableId, colIndex) {
        var table = document.getElementById(tableId);
        var tbody = table.querySelector('tbody');
        var rows = Array.from(tbody.querySelectorAll('tr'));
        var header = table.querySelectorAll('th')[colIndex];
        var isAsc = header.classList.contains('sort-asc');
        
        // Remove sort classes from all headers
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        rows.sort((a, b) => {
            var aVal = a.cells[colIndex].textContent.trim();
            var bVal = b.cells[colIndex].textContent.trim();
            
            // Handle numeric values (including those with + or -)
            var aNum = parseFloat(aVal.replace(/[+%,]/g, ''));
            var bNum = parseFloat(bVal.replace(/[+%,]/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAsc ? bNum - aNum : aNum - bNum;
            }
            
            // Handle "-" as lowest value
            if (aVal === '-') return isAsc ? -1 : 1;
            if (bVal === '-') return isAsc ? 1 : -1;
            
            // String comparison
            return isAsc ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
        });
        
        // Add sort class to current header
        header.classList.add(isAsc ? 'sort-desc' : 'sort-asc');
        
        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }
    </script>
    <style>
    .sortable-table th {
        cursor: pointer;
        user-select: none;
        position: relative;
    }
    .sortable-table th:hover {
        background-color: #334155;
    }
    .sortable-table th::after {
        content: ' ↕';
        color: #64748b;
        font-size: 0.8em;
    }
    .sortable-table th.sort-asc::after {
        content: ' ↑';
        color: #4ade80;
    }
    .sortable-table th.sort-desc::after {
        content: ' ↓';
        color: #4ade80;
    }
    </style>
    """

def render_stats_table(df, title, has_effective_metrics=True, key=None):
    """Render a sortable stats table with optional effective metrics note"""
    st.markdown(f"### {title}")
    
    if has_effective_metrics:
        render_effective_metrics_note()
    
    if df is None or len(df) == 0:
        st.info("No data available for the selected filters.")
        return
    
    # Format the dataframe
    effective_cols = ['eSR', 'eControl', 'eAerial'] if has_effective_metrics else []
    df_display = format_dataframe(df, effective_cols)
    
    # Create unique table ID
    table_id = f"table_{title.replace(' ', '_')}_{key if key else ''}"
    
    # Convert to HTML with custom styling and sorting
    table_html = create_sortable_table_html(df_display, effective_cols, table_id)
    st.markdown(get_sortable_table_js() + table_html, unsafe_allow_html=True)

def render_frequency_table(df, title, key=None, hide_zero_percent=False):
    """Render a sortable frequency table without effective metrics"""
    st.markdown(f"### {title}")
    
    if df is None or len(df) == 0:
        st.info("No data available for the selected filters.")
        return
    
    df_sorted = df.copy()
    
    # If hide_zero_percent, replace "0.00%" with blank
    if hide_zero_percent:
        for col in df_sorted.columns:
            if df_sorted[col].dtype == object:
                df_sorted[col] = df_sorted[col].apply(
                    lambda x: "" if x == "0.00%" or x == "0 %" or x == "0%" else x
                )
    
    # Create unique table ID
    table_id = f"table_{title.replace(' ', '_')}_{key if key else ''}"
    
    # Convert to HTML with custom styling and sorting
    table_html = create_sortable_table_html(df_sorted, [], table_id)
    st.markdown(get_sortable_table_js() + table_html, unsafe_allow_html=True)

def create_sortable_table_html(df, effective_cols, table_id):
    """Create HTML table with custom styling and click-to-sort"""
    if df is None or len(df) == 0:
        return "<p>No data available</p>"
    
    # Start table
    html = f'<div class="table-container"><table class="styled-table sortable-table" id="{table_id}">'
    
    # Header row with onclick handlers
    html += '<thead><tr>'
    for idx, col in enumerate(df.columns):
        html += f'<th onclick="sortTable(\'{table_id}\', {idx})">{col}</th>'
    html += '</tr></thead>'
    
    # Data rows
    html += '<tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            value = row[col]
            cell_class = ""
            
            # Handle None/NaN values
            if pd.isna(value) or value == 'None' or value is None:
                value = "-"
            
            # Check if this is an effective metric column
            if col in effective_cols:
                if isinstance(value, str):
                    if value.startswith('+'):
                        cell_class = "positive-value"
                    elif value.startswith('-') and value != '-':
                        cell_class = "negative-value"
            
            html += f'<td class="{cell_class}">{value}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    
    return html