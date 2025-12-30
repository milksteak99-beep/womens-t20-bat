import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    """Load and preprocess the cricket data"""
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "wt20.csv")
    
    if not os.path.exists(data_path):
        st.error(f"Data file not found at: {data_path}")
        st.info("Please place your wt20.csv file in the 'data' folder.")
        return None
    
    df = pd.read_csv(data_path)
    
    # Preprocess data
    df = preprocess_data(df)
    
    return df

def preprocess_data(df):
    """Preprocess the dataframe"""
    # Convert date columns
    if 'matchDate' in df.columns:
        df['matchDate'] = pd.to_datetime(df['matchDate'], errors='coerce')
    
    # Filter ball column to only include 1-6
    if 'ball' in df.columns:
        df = df[df['ball'].isin([1, 2, 3, 4, 5, 6])]
    
    # Handle foot column - combine '0' and 'NoMovement' as 'No Effective Movement'
    if 'foot' in df.columns:
        df['foot'] = df['foot'].replace({'0': 'No Effective Movement', 'NoMovement': 'No Effective Movement'})
    
    # Handle dismissalType - combine 'Caught' and 'CaughtSub' as 'Caught Out'
    if 'dismissalType' in df.columns:
        df['dismissalType'] = df['dismissalType'].replace({
            'Caught': 'Caught Out', 
            'CaughtSub': 'Caught Out',
            'RunOut': 'Run Out',
            'RunOutSub': 'Run Out'
        })
    
    # Create 'with_control' column
    if 'parsed_control' in df.columns:
        df['with_control'] = df['parsed_control'].isin(['under control', 'well timed'])
    
    # Create 'is_aerial' column
    if 'elevation' in df.columns:
        df['is_aerial'] = df['elevation'] == 'in the air'
    
    # Create 'is_boundary' column
    if 'runs_scored' in df.columns:
        df['is_boundary'] = df['runs_scored'].isin([4, 6])
        df['is_dot'] = df['runs_scored'] == 0
    
    # Create 'is_out' column - handle various formats
    if 'is_wicket' in df.columns:
        # Handle string 'True'/'False', boolean, or 1/0
        df['is_out'] = df['is_wicket'].apply(lambda x: 
            x == True or x == 'True' or x == 1 or x == '1' or x == 'true'
        )
    
    # Also check dismissalType for outs
    if 'dismissalType' in df.columns:
        df['is_out'] = df['is_out'] | df['dismissalType'].notna() & (df['dismissalType'] != '')
    
    return df

@st.cache_data
def get_batters_list(_df):
    """Get sorted list of all batters"""
    if _df is None or 'batsman' not in _df.columns:
        return []
    return sorted(_df['batsman'].dropna().unique().tolist())

@st.cache_data
def get_unique_values(_df, column):
    """Get unique values from a column"""
    if _df is None or column not in _df.columns:
        return []
    return sorted(_df[column].dropna().unique().tolist())

def get_batter_hand(df, batter):
    """Get the handedness of a batter"""
    if df is None or batter is None:
        return "Right"
    batter_data = df[df['batsman'] == batter]
    if len(batter_data) > 0 and 'batsmanHand' in batter_data.columns:
        hand = batter_data['batsmanHand'].mode()
        if len(hand) > 0:
            return hand.iloc[0]
    return "Right"

def get_matches_for_batter_and_filters(df, batter, filters):
    """Get all fixture IDs for matches involving the selected batter and filters"""
    if df is None:
        return []
    
    filtered_df = df.copy()
    
    # Apply batter filter
    if batter:
        batter_matches = df[df['batsman'] == batter]['fixtureId'].unique()
        filtered_df = filtered_df[filtered_df['fixtureId'].isin(batter_matches)]
    
    # Apply other filters
    if filters.get('for_team') and 'All' not in filters['for_team']:
        filtered_df = filtered_df[filtered_df['battingTeam'].isin(filters['for_team'])]
    
    if filters.get('opposition') and 'All' not in filters['opposition']:
        filtered_df = filtered_df[filtered_df['bowlingTeam'].isin(filters['opposition'])]
    
    if filters.get('competition') and 'All' not in filters['competition']:
        filtered_df = filtered_df[filtered_df['competition'].isin(filters['competition'])]
    
    if filters.get('venue') and 'All' not in filters['venue']:
        filtered_df = filtered_df[filtered_df['ground'].isin(filters['venue'])]
    
    if filters.get('host_country') and 'All' not in filters['host_country']:
        filtered_df = filtered_df[filtered_df['country'].isin(filters['host_country'])]
    
    if filters.get('innings') and 'All' not in filters['innings']:
        filtered_df = filtered_df[filtered_df['inns'].isin(filters['innings'])]
    
    return filtered_df['fixtureId'].unique().tolist()
