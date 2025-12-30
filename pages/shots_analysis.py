import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from components.sidebar import render_sidebar
from components.footer import render_footer
from components.tables import render_effective_metrics_note
from utils.filters import apply_filters
from utils.data_loader import get_batter_hand, get_matches_for_batter_and_filters
from utils.calculations import calculate_basic_stats, calculate_risk_reward_by_shot

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


def render_risk_reward_plot(risk_reward_df):
    """Render the Risk-Reward scatter plot for shot types"""
    if risk_reward_df is None or len(risk_reward_df) == 0:
        st.info("Insufficient data for Risk-Reward analysis.")
        return
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Get data
    x = risk_reward_df['Expected Run Value']
    y = risk_reward_df['Wicket Probability']
    sizes = risk_reward_df['Frequency'] * 20  # Scale for visibility
    labels = risk_reward_df['Shot Type']
    
    # Create scatter plot
    scatter = ax.scatter(x, y, s=sizes, alpha=0.7, c='#3b82f6', edgecolors='#1e40af', linewidth=1)
    
    # Add labels for each point
    for i, label in enumerate(labels):
        ax.annotate(
            label,
            (x.iloc[i], y.iloc[i]),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
            color='#333',
            alpha=0.9
        )
    
    # Add quadrant lines at means
    mean_x = x.mean()
    mean_y = y.mean()
    ax.axvline(x=mean_x, color='#94a3b8', linestyle='--', linewidth=1, alpha=0.7)
    ax.axhline(y=mean_y, color='#94a3b8', linestyle='--', linewidth=1, alpha=0.7)
    
    # Add quadrant labels
    x_range = x.max() - x.min()
    y_range = y.max() - y.min()
    
    # Quadrant annotations (subtle)
    ax.annotate('Low Risk\nHigh Reward', xy=(ax.get_xlim()[1] - x_range*0.15, ax.get_ylim()[0] + y_range*0.08),
                fontsize=8, color='#22c55e', alpha=0.7, ha='center')
    ax.annotate('High Risk\nHigh Reward', xy=(ax.get_xlim()[1] - x_range*0.15, ax.get_ylim()[1] - y_range*0.08),
                fontsize=8, color='#f59e0b', alpha=0.7, ha='center')
    ax.annotate('Low Risk\nLow Reward', xy=(ax.get_xlim()[0] + x_range*0.15, ax.get_ylim()[0] + y_range*0.08),
                fontsize=8, color='#64748b', alpha=0.7, ha='center')
    ax.annotate('High Risk\nLow Reward', xy=(ax.get_xlim()[0] + x_range*0.15, ax.get_ylim()[1] - y_range*0.08),
                fontsize=8, color='#ef4444', alpha=0.7, ha='center')
    
    # Labels and title
    ax.set_xlabel('Expected Run Value (Reward)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Wicket Probability (Risk)', fontsize=11, fontweight='bold')
    ax.set_title('Risk-Reward Analysis by Shot Type', fontsize=13, fontweight='bold', pad=15)
    
    # Style
    ax.set_facecolor('#f8fafc')
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    return fig


def calculate_shots_analysis(df, all_matches_df, match_ids):
    """Calculate stats by shot type with frequency"""
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    # Get unique shot types
    shot_types = df['shot_type'].dropna().unique()
    
    # Calculate overall balls for frequency calculation
    overall_balls = len(df)
    
    results = []
    for shot in shot_types:
        if not shot or shot == '':
            continue
            
        shot_df = df[df['shot_type'] == shot]
        shot_all_df = all_matches_df[all_matches_df['shot_type'] == shot] if all_matches_df is not None else shot_df
        
        if len(shot_df) == 0:
            continue
        
        # Calculate basic stats
        balls = len(shot_df)
        runs = shot_df['runs_scored'].sum() if 'runs_scored' in shot_df.columns else 0
        outs = shot_df['is_out'].sum() if 'is_out' in shot_df.columns else 0
        
        average = runs / outs if outs > 0 else None
        sr = (runs / balls * 100) if balls > 0 else 0
        
        controlled_balls = shot_df['with_control'].sum() if 'with_control' in shot_df.columns else 0
        control_pct = (controlled_balls / balls * 100) if balls > 0 else 0
        
        dots = shot_df['is_dot'].sum() if 'is_dot' in shot_df.columns else 0
        dot_pct = (dots / balls * 100) if balls > 0 else 0
        
        boundaries = shot_df['is_boundary'].sum() if 'is_boundary' in shot_df.columns else 0
        boundary_pct = (boundaries / balls * 100) if balls > 0 else 0
        
        frequency = (balls / overall_balls * 100) if overall_balls > 0 else 0
        
        # Calculate average metrics for this shot type
        if len(shot_all_df) > 0:
            all_runs = shot_all_df['runs_scored'].sum() if 'runs_scored' in shot_all_df.columns else 0
            all_balls = len(shot_all_df)
            all_controlled = shot_all_df['with_control'].sum() if 'with_control' in shot_all_df.columns else 0
            
            avgSR = (all_runs / all_balls * 100) if all_balls > 0 else 0
            avgControl = (all_controlled / all_balls * 100) if all_balls > 0 else 0
        else:
            avgSR = 0
            avgControl = 0
        
        eSR = sr - avgSR
        eControl = control_pct - avgControl
        
        results.append({
            'Shot Type': shot,
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

def render_shots_analysis_page(df):
    """Render the Shots Analysis page"""
    
    # Sidebar
    selected_batter, filters = render_sidebar(df, page_type="shots_analysis", key_prefix="sa")
    
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
    
    st.markdown("---")
    
    # --- RISK-REWARD PLOT SECTION ---
    st.markdown("### Risk-Reward Shot Analysis")
    
    # Brief explanation
    st.markdown("""
        <div class="metrics-note">
            <p><strong>Expected Run Value (Reward)</strong>: The average change in run expectancy caused by playing this shot. 
            Higher values indicate shots that add more value to the innings.</p>
            <p><strong>Wicket Probability (Risk)</strong>: The probability of getting out when playing this shot. 
            Higher values indicate riskier shots.</p>
            <p class="note-sub"><em>Point size reflects shot frequency. Dashed lines show average values. 
            Ideal shots are in the bottom-right quadrant (high reward, low risk).</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Calculate risk-reward metrics
    risk_reward_df = calculate_risk_reward_by_shot(filtered_df, df)
    
    if len(risk_reward_df) > 0:
        # Center the plot
        col_left, col_center, col_right = st.columns([1, 4, 1])
        with col_center:
            fig = render_risk_reward_plot(risk_reward_df)
            st.pyplot(fig)
            plt.close(fig)
    else:
        st.info("Insufficient data for Risk-Reward analysis.")
    
    st.markdown("---")
    
    # --- BREAKDOWN OF SHOTS TABLE ---
    # Calculate shots analysis
    all_matches_df = df[df['fixtureId'].isin(match_ids)]
    stats_df = calculate_shots_analysis(filtered_df, all_matches_df, match_ids)
    
    if len(stats_df) > 0:
        st.markdown("### Breakdown of Shots")
        
        # Custom note for this table (without eAerial)
        st.markdown("""
            <div class="metrics-note">
                <p><strong>eSR</strong>: Measure of the selected batter's effective SR in comparison to an average batter.</p>
                <p><strong>eControl</strong>: Measure of the selected batter's effective Control in comparison to an average batter.</p>
                <p class="note-sub"><em>(An average batter is a crude quantification of all batters involved in the matches for which the selected batter and set of filters have been chosen.)</em></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Display table with custom formatting
        display_shots_table(stats_df)
    else:
        st.info("No shot analysis data available for the selected filters.")
    
    # Footer
    render_footer()

def display_shots_table(df):
    """Display the shots analysis table with proper formatting"""
    if df is None or len(df) == 0:
        st.info("No data available.")
        return
    
    # Create sorting controls
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        sort_column = st.selectbox(
            "Sort by",
            options=["None"] + list(df.columns),
            key="shots_sort_select",
            label_visibility="collapsed"
        )
    with col2:
        sort_order = st.selectbox(
            "Order",
            options=["Ascending", "Descending"],
            key="shots_sort_order",
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