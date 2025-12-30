import streamlit as st
import pandas as pd
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.tables import render_stats_table, render_frequency_table
from components.pitchmap import render_pitchmaps_section
from utils.filters import apply_filters
from utils.data_loader import get_batter_hand, get_matches_for_batter_and_filters
from utils.calculations import (
    calculate_pitchmap_data,
    calculate_stats_by_line_length,
    calculate_control_by_line_length,
    calculate_avg_metrics_for_matches,
    calculate_basic_stats
)

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

def render_line_length_page(df):
    """Render the Line-Length wise analysis page"""
    
    # Sidebar
    selected_batter, filters = render_sidebar(df, page_type="line_length", key_prefix="ll")
    
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
    
    # Get batter hand
    batter_hand = get_batter_hand(df, selected_batter)
    
    # Get match IDs for average metrics calculation
    match_ids = get_matches_for_batter_and_filters(df, selected_batter, filters)
    
    # Display batter info with raw stats
    render_batter_info(selected_batter, batter_hand, filtered_df)
    
    # Section 1: Pitchmaps
    st.markdown("## Pitchmaps")
    
    # Calculate pitchmap data
    control_data = calculate_pitchmap_data(filtered_df, 'control')
    average_data = calculate_pitchmap_data(filtered_df, 'average')
    sr_data = calculate_pitchmap_data(filtered_df, 'sr')
    
    # Render pitchmaps
    render_pitchmaps_section(control_data, average_data, sr_data, batter_hand)
    
    st.markdown("---")
    
    # Section 2: Line-length wise stats table
    all_matches_df = df[df['fixtureId'].isin(match_ids)]
    stats_df = calculate_stats_by_line_length(filtered_df, all_matches_df, match_ids)
    
    if len(stats_df) > 0:
        render_stats_table(stats_df, "Line-length wise Stats", has_effective_metrics=True)
    
    st.markdown("---")
    
    # Section 3: Line-length wise shot controls table (with blank instead of 0%)
    control_freq_df = calculate_control_by_line_length(filtered_df)
    
    if len(control_freq_df) > 0:
        render_frequency_table(control_freq_df, "Line-length wise Shot Controls", hide_zero_percent=True)
    
    # Footer
    render_footer()
