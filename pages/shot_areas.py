import streamlit as st
import pandas as pd
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.tables import render_stats_table
from utils.filters import apply_filters
from utils.data_loader import get_batter_hand, get_matches_for_batter_and_filters
from utils.calculations import calculate_stats_by_group, calculate_basic_stats

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

def render_shot_areas_page(df):
    """Render the Shot Areas analysis page"""
    
    # Sidebar
    selected_batter, filters = render_sidebar(df, page_type="shot_areas", key_prefix="shar")
    
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
    
    # Calculate fielding position-wise stats
    all_matches_df = df[df['fixtureId'].isin(match_ids)]
    stats_df = calculate_stats_by_group(filtered_df, all_matches_df, match_ids, 'fielding_position')
    
    if len(stats_df) > 0:
        # Rename column for display
        stats_df = stats_df.rename(columns={'fielding_position': 'Fielding Position'})
        # Filter out empty or null fielding positions
        stats_df = stats_df[stats_df['Fielding Position'].notna()]
        stats_df = stats_df[stats_df['Fielding Position'] != '']
        stats_df = stats_df[stats_df['Fielding Position'] != '-']
        
        render_stats_table(stats_df, "Zone/Field Position wise Shots Breakdown", has_effective_metrics=True)
    else:
        st.info("No shot areas data available for the selected filters.")
    
    # Footer
    render_footer()
