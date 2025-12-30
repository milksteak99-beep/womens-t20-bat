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

def render_ball_type_page(df):
    """Render the Ball Type Specific analysis page"""
    
    # Sidebar
    selected_batter, filters = render_sidebar(df, page_type="ball_type", key_prefix="bt")
    
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
    
    all_matches_df = df[df['fixtureId'].isin(match_ids)]
    
    # Table 1: Generic ball-type/variation wise stats
    st.markdown("---")
    variation_stats = calculate_stats_by_group(filtered_df, all_matches_df, match_ids, 'variation')
    
    if len(variation_stats) > 0:
        variation_stats = variation_stats.rename(columns={'variation': 'Variation'})
        variation_stats = variation_stats[variation_stats['Variation'].notna()]
        variation_stats = variation_stats[variation_stats['Variation'] != '']
        render_stats_table(variation_stats, "Generic Ball-type/Variation wise Stats", has_effective_metrics=True)
    else:
        st.info("No variation data available.")
    
    st.markdown("---")
    
    # Table 2: Detailed ball-type/variation wise stats
    if 'parsed_len.var' in filtered_df.columns:
        detailed_stats = calculate_stats_by_group(filtered_df, all_matches_df, match_ids, 'parsed_len.var')
        
        if len(detailed_stats) > 0:
            detailed_stats = detailed_stats.rename(columns={'parsed_len.var': 'Detailed Ball Type'})
            detailed_stats = detailed_stats[detailed_stats['Detailed Ball Type'].notna()]
            detailed_stats = detailed_stats[detailed_stats['Detailed Ball Type'] != '']
            render_stats_table(detailed_stats, "Detailed Ball-type/Variation wise Stats", has_effective_metrics=True)
        else:
            st.info("No detailed ball type data available.")
    
    st.markdown("---")
    
    # Table 3: Bowler-type wise stats
    bowler_type_stats = calculate_stats_by_group(filtered_df, all_matches_df, match_ids, 'bowlerType')
    
    if len(bowler_type_stats) > 0:
        bowler_type_stats = bowler_type_stats.rename(columns={'bowlerType': 'Bowler Type'})
        bowler_type_stats = bowler_type_stats[bowler_type_stats['Bowler Type'].notna()]
        bowler_type_stats = bowler_type_stats[bowler_type_stats['Bowler Type'] != '']
        render_stats_table(bowler_type_stats, "Bowler-type wise Stats", has_effective_metrics=True)
    else:
        st.info("No bowler type data available.")
    
    # Footer
    render_footer()
