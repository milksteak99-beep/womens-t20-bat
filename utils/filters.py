import streamlit as st
import pandas as pd
from datetime import datetime
from config.settings import MIN_DATE, MAX_DATE

def apply_filters(df, batter, filters):
    """Apply all filters to the dataframe"""
    if df is None:
        return None
    
    filtered_df = df.copy()
    
    # Apply batter filter
    if batter:
        filtered_df = filtered_df[filtered_df['batsman'] == batter]
    
    # Apply team filter
    if filters.get('for_team') and 'All' not in filters['for_team']:
        filtered_df = filtered_df[filtered_df['battingTeam'].isin(filters['for_team'])]
    
    # Apply opposition filter
    if filters.get('opposition') and 'All' not in filters['opposition']:
        filtered_df = filtered_df[filtered_df['bowlingTeam'].isin(filters['opposition'])]
    
    # Apply competition filter
    if filters.get('competition') and 'All' not in filters['competition']:
        filtered_df = filtered_df[filtered_df['competition'].isin(filters['competition'])]
    
    # Apply venue filter
    if filters.get('venue') and 'All' not in filters['venue']:
        filtered_df = filtered_df[filtered_df['ground'].isin(filters['venue'])]
    
    # Apply host country filter
    if filters.get('host_country') and 'All' not in filters['host_country']:
        filtered_df = filtered_df[filtered_df['country'].isin(filters['host_country'])]
    
    # Apply overs filter
    if filters.get('overs'):
        over_min, over_max = filters['overs']
        filtered_df = filtered_df[(filtered_df['over'] >= over_min) & (filtered_df['over'] <= over_max)]
    
    # Apply bowler type filter
    if filters.get('bowler_type') and 'All' not in filters['bowler_type']:
        filtered_df = filtered_df[filtered_df['bowlerType'].isin(filters['bowler_type'])]
    
    # Apply specific bowler filter
    if filters.get('against_bowler') and 'All' not in filters['against_bowler']:
        filtered_df = filtered_df[filtered_df['bowler'].isin(filters['against_bowler'])]
    
    # Apply innings filter
    if filters.get('innings') and 'All' not in filters['innings']:
        filtered_df = filtered_df[filtered_df['inns'].isin(filters['innings'])]
    
    # Apply date filter
    if filters.get('date_range'):
        start_date, end_date = filters['date_range']
        if 'matchDate' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['matchDate'] >= pd.Timestamp(start_date)) & 
                (filtered_df['matchDate'] <= pd.Timestamp(end_date))
            ]
    
    # Apply bowler hand filter
    if filters.get('bowler_hand') and 'All' not in filters['bowler_hand']:
        filtered_df = filtered_df[filtered_df['bowlerHand'].isin(filters['bowler_hand'])]
    
    # Apply bowling angle filter
    if filters.get('bowling_angle') and 'All' not in filters['bowling_angle']:
        filtered_df = filtered_df[filtered_df['bowlingAngle'].isin(filters['bowling_angle'])]
    
    return filtered_df

def create_batter_selector(df, key_prefix=""):
    """Create batter selection dropdown with session state preservation"""
    batters = sorted(df['batsman'].dropna().unique().tolist()) if df is not None else []
    
    # Get default from session state if available
    default_index = 0
    if st.session_state.get('selected_batter') and st.session_state.selected_batter in batters:
        default_index = batters.index(st.session_state.selected_batter) + 1  # +1 for empty option
    
    selected_batter = st.selectbox(
        "Select Batter",
        options=[""] + batters,
        index=default_index,
        key=f"{key_prefix}_batter_selector",
        help="Type to search for a batter"
    )
    
    return selected_batter if selected_batter else None

def create_filter_widgets(df, page_type="default", key_prefix=""):
    """Create filter widgets based on page type"""
    filters = {}
    
    if df is None:
        return filters
    
    st.markdown("### Filters")
    
    # For Team filter
    teams = sorted(df['battingTeam'].dropna().unique().tolist())
    filters['for_team'] = st.multiselect(
        "For Team",
        options=teams,
        default=[],
        key=f"{key_prefix}_for_team",
        help="Select batting team(s)"
    )
    if not filters['for_team']:
        filters['for_team'] = ['All']
    
    # Opposition filter
    oppositions = sorted(df['bowlingTeam'].dropna().unique().tolist())
    filters['opposition'] = st.multiselect(
        "Opposition",
        options=oppositions,
        default=[],
        key=f"{key_prefix}_opposition",
        help="Select opposition team(s)"
    )
    if not filters['opposition']:
        filters['opposition'] = ['All']
    
    # Competition filter
    competitions = sorted(df['competition'].dropna().unique().tolist())
    filters['competition'] = st.multiselect(
        "Competition",
        options=competitions,
        default=[],
        key=f"{key_prefix}_competition",
        help="Select competition(s)"
    )
    if not filters['competition']:
        filters['competition'] = ['All']
    
    # Venue filter
    venues = sorted(df['ground'].dropna().unique().tolist())
    filters['venue'] = st.multiselect(
        "Venue",
        options=venues,
        default=[],
        key=f"{key_prefix}_venue",
        help="Select venue(s)"
    )
    if not filters['venue']:
        filters['venue'] = ['All']
    
    # Host Country filter
    countries = sorted(df['country'].dropna().unique().tolist())
    filters['host_country'] = st.multiselect(
        "Host Country",
        options=countries,
        default=[],
        key=f"{key_prefix}_host_country",
        help="Select host country(ies)"
    )
    if not filters['host_country']:
        filters['host_country'] = ['All']
    
    # Overs filter (slider) - for pages that need it
    if page_type in ["default", "line_length", "shots_analysis", "shot_areas", 
                      "ball_type", "feet_movement", "dismissals", "bowler_wise", "wagon_wheels"]:
        filters['overs'] = st.slider(
            "Overs",
            min_value=1,
            max_value=20,
            value=(1, 20),
            key=f"{key_prefix}_overs",
            help="Select over range"
        )
    
    # Against Bowler Type filter - for specific pages
    if page_type in ["default", "line_length", "shots_analysis", "shot_areas", 
                      "innings_progression", "feet_movement", "wagon_wheels"]:
        bowler_types = sorted(df['bowlerType'].dropna().unique().tolist())
        filters['bowler_type'] = st.multiselect(
            "Against Bowler Type",
            options=bowler_types,
            default=[],
            key=f"{key_prefix}_bowler_type",
            help="Select bowler type(s)"
        )
        if not filters['bowler_type']:
            filters['bowler_type'] = ['All']
    
    # Against Bowler filter - for specific pages
    if page_type in ["default", "line_length", "shots_analysis", "shot_areas", 
                      "innings_progression", "feet_movement", "wagon_wheels"]:
        bowlers = sorted(df['bowler'].dropna().unique().tolist())
        filters['against_bowler'] = st.multiselect(
            "Against Bowler",
            options=bowlers,
            default=[],
            key=f"{key_prefix}_against_bowler",
            help="Select specific bowler(s)"
        )
        if not filters['against_bowler']:
            filters['against_bowler'] = ['All']
    
    # Bowler Hand filter - for ball_type page
    if page_type == "ball_type":
        bowler_hands = sorted(df['bowlerHand'].dropna().unique().tolist())
        filters['bowler_hand'] = st.multiselect(
            "Against Bowling Hand",
            options=bowler_hands,
            default=[],
            key=f"{key_prefix}_bowler_hand",
            help="Select bowler hand(s)"
        )
        if not filters['bowler_hand']:
            filters['bowler_hand'] = ['All']
        
        bowling_angles = sorted(df['bowlingAngle'].dropna().unique().tolist())
        filters['bowling_angle'] = st.multiselect(
            "Against Bowling Angle",
            options=bowling_angles,
            default=[],
            key=f"{key_prefix}_bowling_angle",
            help="Select bowling angle(s)"
        )
        if not filters['bowling_angle']:
            filters['bowling_angle'] = ['All']
    
    # Innings filter
    innings_options = sorted(df['inns'].dropna().unique().tolist())
    filters['innings'] = st.multiselect(
        "Innings",
        options=innings_options,
        default=[],
        key=f"{key_prefix}_innings",
        help="Select innings"
    )
    if not filters['innings']:
        filters['innings'] = ['All']
    
    # Date range filter
    st.markdown("**Select Date Range**")
    min_date = datetime.strptime(MIN_DATE, "%Y-%m-%d").date()
    max_date = datetime.strptime(MAX_DATE, "%Y-%m-%d").date()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "From",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_start_date"
        )
    with col2:
        end_date = st.date_input(
            "To",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key=f"{key_prefix}_end_date"
        )
    
    filters['date_range'] = (start_date, end_date)
    
    # Rolling window slider - for innings_progression page only
    if page_type == "innings_progression":
        st.markdown("**Rolling Window for Balls Faced**")
        filters['rolling_window'] = st.slider(
            "Balls faced range",
            min_value=0,
            max_value=84,
            value=(0, 20),
            key=f"{key_prefix}_rolling_window",
            help="Select rolling window range for balls faced"
        )
    
    return filters