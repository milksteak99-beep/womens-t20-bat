import streamlit as st
import pandas as pd
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.tables import render_frequency_table
from utils.filters import apply_filters
from utils.data_loader import get_batter_hand, get_matches_for_batter_and_filters
from utils.calculations import calculate_dismissal_by_group, calculate_basic_stats

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

def render_dismissals_page(df):
    """Render the Dismissals analysis page"""
    
    # Sidebar
    selected_batter, filters = render_sidebar(df, page_type="dismissals", key_prefix="dis")
    
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
    
    # Get batter hand for display
    batter_hand = get_batter_hand(df, selected_batter)
    
    # Display batter info with raw stats
    render_batter_info(selected_batter, batter_hand, filtered_df)
    
    # Table 1: Ball-type/variation wise dismissals
    variation_dismissals = calculate_dismissal_by_group(filtered_df, 'variation', include_runout=True)
    
    if len(variation_dismissals) > 0:
        variation_dismissals = variation_dismissals.rename(columns={'variation': 'Variation'})
        variation_dismissals = variation_dismissals[variation_dismissals['Variation'].notna()]
        variation_dismissals = variation_dismissals[variation_dismissals['Variation'] != '']
        render_frequency_table(variation_dismissals, "Ball-type/Variation wise Dismissals")
    else:
        st.info("No variation-wise dismissal data available.")
    
    st.markdown("---")
    
    # Table 2: Bowler wise dismissals (excluding run outs)
    bowler_dismissals = calculate_dismissal_by_group(filtered_df, 'bowler', include_runout=False)
    
    if len(bowler_dismissals) > 0:
        bowler_dismissals = bowler_dismissals.rename(columns={'bowler': 'Bowler'})
        render_frequency_table(bowler_dismissals, "Bowler wise Dismissals")
    else:
        st.info("No bowler-wise dismissal data available.")
    
    # Footer
    render_footer()
