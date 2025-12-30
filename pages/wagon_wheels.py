import streamlit as st
import pandas as pd
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.wagon_wheel import render_wagon_wheels_section
from utils.filters import apply_filters
from utils.data_loader import get_batter_hand
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


def render_wagon_wheels_page(df):
    """Render the Wagon Wheels page with 3 wagon wheel visualizations"""
    
    # Sidebar with filters
    selected_batter, filters = render_sidebar(df, page_type="wagon_wheels", key_prefix="ww")
    
    # Main content
    if not selected_batter:
        st.info("Please select a batter from the sidebar to view wagon wheel analysis.")
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
    is_rhb = batter_hand == "Right"
    
    # Display batter info with raw stats
    render_batter_info(selected_batter, batter_hand, filtered_df)
    
    st.markdown("---")
    
    # Section: Wagon Wheels
    st.markdown("## Wagon Wheels")
    
    # Render all three wagon wheels
    render_wagon_wheels_section(filtered_df, is_rhb)
    
    # Footer
    render_footer()