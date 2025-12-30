import streamlit as st
import pandas as pd
import numpy as np
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.tables import render_frequency_table, render_effective_metrics_note
from utils.filters import apply_filters
from utils.data_loader import get_batter_hand, get_matches_for_batter_and_filters
from utils.calculations import calculate_basic_stats

def render_batter_info(selected_batter, batter_hand, filtered_df):
    """Render batter info box with raw stats"""
    stats = calculate_basic_stats(filtered_df)
    
    avg_display = f"{stats['average']:.2f}" if stats['average'] is not None else "-"
    
    st.markdown(f"""
        <div class="batter-info">
            <h2>{selected_batter}</h2>
            <p>Batting Style: <strong>{"Right-Handed" if batter_hand == "Right" else "Left-Handed"}</strong></p>
            <div class="stats-row">
                <div class="stat-item">
                    <span class="stat-label">Runs</span>
                    <span class="stat-value">{stats['runs']:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Balls</span>
                    <span class="stat-value">{stats['balls']:,}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Average</span>
                    <span class="stat-value">{avg_display}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Strike Rate</span>
                    <span class="stat-value">{stats['sr']:.2f}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Boundary %</span>
                    <span class="stat-value">{stats['boundary_pct']:.2f}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Dot Ball %</span>
                    <span class="stat-value">{stats['dot_pct']:.2f}%</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def calculate_feet_movement_by_line_length(df):
    """Calculate feet movement frequency by line-length combination with merged columns"""
    if df is None or len(df) == 0 or 'foot' not in df.columns:
        return pd.DataFrame()
    
    lines = df['parsed_line'].dropna().unique()
    lengths = df['parsed_length'].dropna().unique()
    
    # Get foot types and merge '0.0' and 'No Effective Movement'
    foot_types = df['foot'].dropna().unique()
    
    results = []
    for length in lengths:
        for line in lines:
            combo_df = df[(df['parsed_length'] == length) & (df['parsed_line'] == line)]
            if len(combo_df) > 0:
                row = {
                    'Length': length.title() if isinstance(length, str) else length,
                    'Line': line.title() if isinstance(line, str) else line
                }
                total_balls = len(combo_df)
                
                # Calculate No Effective Movement (combining '0.0', 'No Effective Movement', etc.)
                no_movement_count = 0
                other_foot_types = []
                
                for foot in foot_types:
                    foot_str = str(foot).strip()
                    if foot_str in ['0.0', '0', 'No Effective Movement', 'NoMovement', 'None', '']:
                        no_movement_count += len(combo_df[combo_df['foot'] == foot])
                    else:
                        other_foot_types.append(foot)
                
                # Add No Effective Movement column
                row['No Effective Movement'] = f"{(no_movement_count / total_balls * 100):.2f}%" if total_balls > 0 else "0.00%"
                
                # Add other foot types
                for foot in other_foot_types:
                    foot_count = len(combo_df[combo_df['foot'] == foot])
                    row[str(foot)] = f"{(foot_count / total_balls * 100):.2f}%" if total_balls > 0 else "0.00%"
                
                results.append(row)
    
    return pd.DataFrame(results)

def calculate_feet_movement_stats(df, all_matches_df, match_ids):
    """Calculate feet movement induced performance stats"""
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    # Get unique foot types
    foot_types = df['foot'].dropna().unique()
    
    # Calculate overall balls for frequency
    overall_balls = len(df)
    
    results = []
    for foot in foot_types:
        foot_str = str(foot).strip()
        if not foot_str or foot_str == '' or foot_str == 'None':
            continue
        
        # Merge '0.0' with 'No Effective Movement'
        if foot_str in ['0.0', '0']:
            continue  # Skip these, they'll be merged with 'No Effective Movement'
        
        foot_df = df[df['foot'] == foot]
        foot_all_df = all_matches_df[all_matches_df['foot'] == foot] if all_matches_df is not None else foot_df
        
        if len(foot_df) == 0:
            continue
        
        # Calculate basic stats
        balls = len(foot_df)
        runs = foot_df['runs_scored'].sum() if 'runs_scored' in foot_df.columns else 0
        outs = foot_df['is_out'].sum() if 'is_out' in foot_df.columns else 0
        
        average = runs / outs if outs > 0 else None
        sr = (runs / balls * 100) if balls > 0 else 0
        
        controlled_balls = foot_df['with_control'].sum() if 'with_control' in foot_df.columns else 0
        control_pct = (controlled_balls / balls * 100) if balls > 0 else 0
        
        dots = foot_df['is_dot'].sum() if 'is_dot' in foot_df.columns else 0
        dot_pct = (dots / balls * 100) if balls > 0 else 0
        
        boundaries = foot_df['is_boundary'].sum() if 'is_boundary' in foot_df.columns else 0
        boundary_pct = (boundaries / balls * 100) if balls > 0 else 0
        
        frequency = (balls / overall_balls * 100) if overall_balls > 0 else 0
        
        # Calculate average metrics
        if len(foot_all_df) > 0:
            all_runs = foot_all_df['runs_scored'].sum() if 'runs_scored' in foot_all_df.columns else 0
            all_balls = len(foot_all_df)
            all_controlled = foot_all_df['with_control'].sum() if 'with_control' in foot_all_df.columns else 0
            
            avgSR = (all_runs / all_balls * 100) if all_balls > 0 else 0
            avgControl = (all_controlled / all_balls * 100) if all_balls > 0 else 0
        else:
            avgSR = 0
            avgControl = 0
        
        eSR = sr - avgSR
        eControl = control_pct - avgControl
        
        results.append({
            'Feet Movement': foot_str,
            'Balls': balls,
            'Runs': runs,
            'Average': average,
            'SR': sr,
            'eSR': eSR,
            'Control %': control_pct,
            'eControl': eControl,
            'Dot %': dot_pct,
            'Boundary %': boundary_pct,
            'Frequency': f"{frequency:.2f}%"
        })
    
    return pd.DataFrame(results)

def render_feet_movement_page(df):
    """Render the Feet Movement analysis page"""
    
    # Sidebar
    selected_batter, filters = render_sidebar(df, page_type="feet_movement", key_prefix="fm")
    
    # Main content
    if not selected_batter:
        st.info("Please select a batter from the sidebar to view analysis.")
        render_footer()
        return
    
    # Apply filters
    filtered_df = apply_filters(df, selected_batter, filters)
    
    if filtered_df is None or len(filtered_df) == 0:
        st.warning("No data available for the selected batter and filters.")
        render_footer()
        return
    
    # Get match IDs for average metrics calculation
    match_ids = get_matches_for_batter_and_filters(df, selected_batter, filters)
    
    # Get batter hand for display
    batter_hand = get_batter_hand(df, selected_batter)
    
    # Display batter info with raw stats
    render_batter_info(selected_batter, batter_hand, filtered_df)
    
    # Table 1: Recorded feet movement per line-length
    feet_by_line_length = calculate_feet_movement_by_line_length(filtered_df)
    
    if len(feet_by_line_length) > 0:
        render_frequency_table(feet_by_line_length, "Recorded Feet Movement per Line-Length")
    else:
        st.info("No feet movement data by line-length available.")
    
    st.markdown("---")
    
    # Table 2: Feet movement induced performance
    all_matches_df = df[df['fixtureId'].isin(match_ids)]
    feet_stats = calculate_feet_movement_stats(filtered_df, all_matches_df, match_ids)
    
    if len(feet_stats) > 0:
        st.markdown("### Feet Movement Induced Performance")
        
        # Custom note (without eAerial)
        st.markdown("""
            <div class="metrics-note">
                <p><strong>eSR</strong>: Measure of the selected batter's effective SR in comparison to an average batter.</p>
                <p><strong>eControl</strong>: Measure of the selected batter's effective Control in comparison to an average batter.</p>
                <p class="note-sub"><em>(An average batter is a crude quantification of all batters involved in the matches for which the selected batter and set of filters have been chosen.)</em></p>
            </div>
        """, unsafe_allow_html=True)
        
        display_feet_stats_table(feet_stats)
    else:
        st.info("No feet movement performance data available.")
    
    # Footer
    render_footer()

def display_feet_stats_table(df):
    """Display the feet movement stats table with proper formatting"""
    if df is None or len(df) == 0:
        st.info("No data available.")
        return
    
    # Create sorting controls
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        sort_column = st.selectbox(
            "Sort by",
            options=["None"] + list(df.columns),
            key="feet_sort_select",
            label_visibility="collapsed"
        )
    with col2:
        sort_order = st.selectbox(
            "Order",
            options=["Ascending", "Descending"],
            key="feet_sort_order",
            label_visibility="collapsed"
        )
    
    # Apply sorting
    df_sorted = df.copy()
    if sort_column and sort_column != "None":
        ascending = sort_order == "Ascending"
        try:
            df_sorted = df_sorted.sort_values(by=sort_column, ascending=ascending)
        except:
            pass
    
    df_display = df_sorted.copy()
    
    for col in ['Average', 'SR', 'Control %', 'Dot %', 'Boundary %']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: f"{x:.2f}" if pd.notna(x) and x != float('inf') else "-"
            )
    
    for col in ['eSR', 'eControl']:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(
                lambda x: f"+{x:.2f}" if pd.notna(x) and x > 0 else (f"{x:.2f}" if pd.notna(x) else "-")
            )
    
    # Create HTML table
    html = '<div class="table-container"><table class="styled-table">'
    
    html += '<thead><tr>'
    for col in df_display.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead>'
    
    html += '<tbody>'
    for _, row in df_display.iterrows():
        html += '<tr>'
        for col in df_display.columns:
            value = row[col]
            cell_class = ""
            
            if col in ['eSR', 'eControl']:
                if isinstance(value, str):
                    if value.startswith('+'):
                        cell_class = "positive-value"
                    elif value.startswith('-') and value != '-':
                        cell_class = "negative-value"
            
            html += f'<td class="{cell_class}">{value}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    
    st.markdown(html, unsafe_allow_html=True)
