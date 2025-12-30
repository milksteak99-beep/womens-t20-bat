import pandas as pd
import numpy as np

def calculate_basic_stats(df):
    """Calculate basic batting statistics"""
    if df is None or len(df) == 0:
        return {
            'balls': 0,
            'runs': 0,
            'outs': 0,
            'average': None,
            'sr': 0,
            'control_pct': 0,
            'dot_pct': 0,
            'boundary_pct': 0,
            'aerial_pct': 0,
            'dots': 0,
            'boundaries': 0,
            'aerials': 0,
            'controlled_balls': 0
        }
    
    balls = len(df)
    runs = int(df['runs_scored'].sum()) if 'runs_scored' in df.columns else 0
    
    # Handle is_out - could be boolean, int, or calculated from dismissalType
    outs = 0
    if 'is_out' in df.columns:
        outs = int(df['is_out'].sum())
    elif 'dismissalType' in df.columns:
        # Count non-null, non-empty dismissal types
        outs = int(df['dismissalType'].notna().sum() - (df['dismissalType'] == '').sum())
    
    average = runs / outs if outs > 0 else None
    sr = (runs / balls * 100) if balls > 0 else 0
    
    controlled_balls = int(df['with_control'].sum()) if 'with_control' in df.columns else 0
    control_pct = (controlled_balls / balls * 100) if balls > 0 else 0
    
    dots = int(df['is_dot'].sum()) if 'is_dot' in df.columns else 0
    dot_pct = (dots / balls * 100) if balls > 0 else 0
    
    boundaries = int(df['is_boundary'].sum()) if 'is_boundary' in df.columns else 0
    boundary_pct = (boundaries / balls * 100) if balls > 0 else 0
    
    aerials = int(df['is_aerial'].sum()) if 'is_aerial' in df.columns else 0
    aerial_pct = (aerials / balls * 100) if balls > 0 else 0
    
    return {
        'balls': balls,
        'runs': runs,
        'outs': outs,
        'average': average,
        'sr': sr,
        'control_pct': control_pct,
        'dot_pct': dot_pct,
        'boundary_pct': boundary_pct,
        'aerial_pct': aerial_pct,
        'dots': dots,
        'boundaries': boundaries,
        'aerials': aerials,
        'controlled_balls': controlled_balls
    }

def calculate_avg_metrics_for_matches(df, match_ids, group_by=None):
    """
    Calculate average metrics for all batters in specified matches.
    Used to compute eSR, eControl, eAerial comparisons.
    """
    if df is None or len(match_ids) == 0:
        return {'avgSR': 0, 'avgControl': 0, 'avgAerial': 0}
    
    # Filter to matches
    match_df = df[df['fixtureId'].isin(match_ids)]
    
    if len(match_df) == 0:
        return {'avgSR': 0, 'avgControl': 0, 'avgAerial': 0}
    
    if group_by:
        # Calculate averages per group
        result = {}
        for group_val in match_df[group_by].unique():
            group_df = match_df[match_df[group_by] == group_val]
            stats = calculate_basic_stats(group_df)
            result[group_val] = {
                'avgSR': stats['sr'],
                'avgControl': stats['control_pct'],
                'avgAerial': stats['aerial_pct']
            }
        return result
    else:
        stats = calculate_basic_stats(match_df)
        return {
            'avgSR': stats['sr'],
            'avgControl': stats['control_pct'],
            'avgAerial': stats['aerial_pct']
        }

def calculate_effective_metrics(batter_stats, avg_metrics):
    """Calculate effective metrics (eSR, eControl, eAerial)"""
    eSR = batter_stats['sr'] - avg_metrics.get('avgSR', 0)
    eControl = batter_stats['control_pct'] - avg_metrics.get('avgControl', 0)
    eAerial = batter_stats['aerial_pct'] - avg_metrics.get('avgAerial', 0)
    
    return {
        'eSR': eSR,
        'eControl': eControl,
        'eAerial': eAerial
    }

def calculate_control_percentage(df):
    """Calculate control percentage for filtered data"""
    if df is None or len(df) == 0:
        return 0
    
    balls = len(df)
    if 'with_control' in df.columns:
        controlled = df['with_control'].sum()
        return (controlled / balls * 100) if balls > 0 else 0
    return 0

def calculate_stats_by_group(df, all_matches_df, match_ids, group_column):
    """
    Calculate stats grouped by a specific column.
    Returns DataFrame with all stats and effective metrics.
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    # Get unique groups
    groups = df[group_column].dropna().unique()
    
    # Calculate avg metrics per group for comparison
    avg_metrics_by_group = calculate_avg_metrics_for_matches(all_matches_df, match_ids, group_by=group_column)
    
    results = []
    for group in groups:
        group_df = df[df[group_column] == group]
        stats = calculate_basic_stats(group_df)
        
        # Get average metrics for this group
        if isinstance(avg_metrics_by_group, dict) and group in avg_metrics_by_group:
            avg_metrics = avg_metrics_by_group[group]
        else:
            avg_metrics = avg_metrics_by_group if isinstance(avg_metrics_by_group, dict) else {'avgSR': 0, 'avgControl': 0, 'avgAerial': 0}
        
        effective = calculate_effective_metrics(stats, avg_metrics)
        
        results.append({
            group_column: group,
            'Balls': stats['balls'],
            'Runs': stats['runs'],
            'Average': stats['average'],
            'SR': stats['sr'],
            'eSR': effective['eSR'],
            'Control %': stats['control_pct'],
            'eControl': effective['eControl'],
            'Dot %': stats['dot_pct'],
            'Boundary %': stats['boundary_pct'],
            'Aerial Shots %': stats['aerial_pct'],
            'eAerial': effective['eAerial']
        })
    
    return pd.DataFrame(results)

def calculate_stats_by_line_length(df, all_matches_df, match_ids):
    """Calculate stats for each line-length combination"""
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    # Get all unique line-length combinations
    lines = df['parsed_line'].dropna().unique()
    lengths = df['parsed_length'].dropna().unique()
    
    # Calculate overall avg metrics for comparison
    avg_metrics = calculate_avg_metrics_for_matches(all_matches_df, match_ids)
    
    results = []
    for length in lengths:
        for line in lines:
            combo_df = df[(df['parsed_length'] == length) & (df['parsed_line'] == line)]
            if len(combo_df) > 0:
                stats = calculate_basic_stats(combo_df)
                effective = calculate_effective_metrics(stats, avg_metrics)
                
                results.append({
                    'Length': length.title() if isinstance(length, str) else length,
                    'Line': line.title() if isinstance(line, str) else line,
                    'Balls': stats['balls'],
                    'Runs': stats['runs'],
                    'Average': stats['average'],
                    'SR': stats['sr'],
                    'eSR': effective['eSR'],
                    'Control %': stats['control_pct'],
                    'eControl': effective['eControl'],
                    'Dot %': stats['dot_pct'],
                    'Boundary %': stats['boundary_pct'],
                    'Aerial Shots %': stats['aerial_pct'],
                    'eAerial': effective['eAerial']
                })
    
    return pd.DataFrame(results)

def calculate_control_by_line_length(df):
    """Calculate shot control frequency by line-length combination"""
    if df is None or len(df) == 0 or 'control' not in df.columns:
        return pd.DataFrame()
    
    lines = df['parsed_line'].dropna().unique()
    lengths = df['parsed_length'].dropna().unique()
    control_types = df['control'].dropna().unique()
    
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
                
                for control in control_types:
                    control_count = len(combo_df[combo_df['control'] == control])
                    row[control] = f"{(control_count / total_balls * 100):.2f}%" if total_balls > 0 else "0.00%"
                
                results.append(row)
    
    return pd.DataFrame(results)

def calculate_feet_movement_by_line_length(df):
    """Calculate feet movement frequency by line-length combination"""
    if df is None or len(df) == 0 or 'foot' not in df.columns:
        return pd.DataFrame()
    
    lines = df['parsed_line'].dropna().unique()
    lengths = df['parsed_length'].dropna().unique()
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
                
                for foot in foot_types:
                    foot_count = len(combo_df[combo_df['foot'] == foot])
                    row[foot] = f"{(foot_count / total_balls * 100):.2f}%" if total_balls > 0 else "0.00%"
                
                results.append(row)
    
    return pd.DataFrame(results)

def calculate_dismissal_by_group(df, group_column, include_runout=True):
    """Calculate dismissal frequency by a group column"""
    if df is None or len(df) == 0 or 'dismissalType' not in df.columns:
        return pd.DataFrame()
    
    groups = df[group_column].dropna().unique()
    
    # Filter dismissal types
    if include_runout:
        dismissal_types = [d for d in df['dismissalType'].dropna().unique() if d and d != '']
    else:
        dismissal_types = [d for d in df['dismissalType'].dropna().unique() if d and d != '' and d != 'Run Out']
    
    results = []
    for group in groups:
        group_df = df[df[group_column] == group]
        if len(group_df) > 0:
            row = {group_column: group}
            total_balls = len(group_df)
            
            for dismissal in dismissal_types:
                dismissal_count = len(group_df[group_df['dismissalType'] == dismissal])
                row[dismissal] = f"{(dismissal_count / total_balls * 100):.2f}%" if total_balls > 0 else "0.00%"
            
            results.append(row)
    
    return pd.DataFrame(results)

def calculate_progression_data(df, batter, filters, rolling_min, rolling_max):
    """
    Calculate progression data for innings progression plots.
    Returns data for Strike Rate, Boundary %, Dot %, Aerial % per rolling window.
    """
    if df is None or len(df) == 0:
        return None
    
    # Need to calculate ball number within each innings for the batter
    batter_df = df.copy()
    
    # Sort by fixture and timestamp to get ball order
    if 'timestamp' in batter_df.columns:
        batter_df = batter_df.sort_values(['fixtureId', 'inns', 'timestamp'])
    else:
        batter_df = batter_df.sort_values(['fixtureId', 'inns', 'over', 'ball'])
    
    # Add ball number within innings
    batter_df['ball_in_innings'] = batter_df.groupby(['fixtureId', 'inns']).cumcount() + 1
    
    results = []
    for ball_num in range(rolling_min, rolling_max + 1):
        if ball_num == 0:
            continue
        
        # Get all balls where ball_in_innings == ball_num
        ball_df = batter_df[batter_df['ball_in_innings'] == ball_num]
        
        if len(ball_df) == 0:
            continue
        
        total_balls = len(ball_df)
        total_runs = ball_df['runs_scored'].sum() if 'runs_scored' in ball_df.columns else 0
        total_boundaries = ball_df['is_boundary'].sum() if 'is_boundary' in ball_df.columns else 0
        total_dots = ball_df['is_dot'].sum() if 'is_dot' in ball_df.columns else 0
        total_aerials = ball_df['is_aerial'].sum() if 'is_aerial' in ball_df.columns else 0
        
        sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
        boundary_pct = (total_boundaries / total_balls * 100) if total_balls > 0 else 0
        dot_pct = (total_dots / total_balls * 100) if total_balls > 0 else 0
        aerial_pct = (total_aerials / total_balls * 100) if total_balls > 0 else 0
        
        results.append({
            'Ball': ball_num,
            'SR': sr,
            'Boundary %': boundary_pct,
            'Dot %': dot_pct,
            'Aerial %': aerial_pct,
            'Sample Size': total_balls
        })
    
    return pd.DataFrame(results)

def calculate_pitchmap_data(df, metric_type):
    """
    Calculate pitchmap data for a specific metric.
    metric_type: 'control', 'average', 'sr'
    """
    if df is None or len(df) == 0:
        return {}
    
    lengths = ['full toss', 'yorker', 'half volley', 'length ball', 'back of a length', 'short', 'bouncer']
    lines = ['wide outside off', 'outside off', 'off', 'middle', 'leg', 'down leg']
    
    pitchmap_data = {}
    
    for length in lengths:
        for line in lines:
            combo_df = df[(df['parsed_length'] == length) & (df['parsed_line'] == line)]
            
            if len(combo_df) > 0:
                stats = calculate_basic_stats(combo_df)
                
                if metric_type == 'control':
                    value = stats['control_pct']
                elif metric_type == 'average':
                    value = stats['average']
                elif metric_type == 'sr':
                    value = stats['sr']
                else:
                    value = 0
                
                pitchmap_data[(length, line)] = value
            else:
                pitchmap_data[(length, line)] = None
    
    return pitchmap_data

def format_value(value, decimals=2, show_sign=False, is_percentage=False):
    """Format a numeric value for display"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "-"
    
    if show_sign and value > 0:
        formatted = f"+{value:.{decimals}f}"
    else:
        formatted = f"{value:.{decimals}f}"
    
    if is_percentage:
        formatted += "%"
    
    return formatted

def get_color_for_effective_metric(value):
    """Return color class for effective metrics"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    if value > 0:
        return "positive"
    elif value < 0:
        return "negative"
    return ""


def get_over_bucket(over):
    """Convert over number to over bucket for state definition"""
    if over <= 6:
        return "1-6"
    elif over <= 15:
        return "7-15"
    else:
        return "16-20"


def calculate_run_expectancy_table(df):
    """
    Calculate Run Expectancy (RE) for each state.
    State = (innings, over_bucket, wickets_in_hand)
    
    RE(S) = Expected future runs from state S until innings end.
    """
    if df is None or len(df) == 0:
        return {}
    
    # Create a copy and add state columns
    re_df = df.copy()
    
    # Add over bucket
    re_df['over_bucket'] = re_df['over'].apply(get_over_bucket)
    
    # Calculate wickets_in_hand (10 - cumulative wickets)
    # We need to calculate cumulative wickets within each innings
    re_df = re_df.sort_values(['fixtureId', 'inns', 'over', 'ball'])
    
    # Calculate cumulative wickets per innings
    re_df['is_wicket_num'] = re_df['is_out'].astype(int) if 'is_out' in re_df.columns else 0
    re_df['cum_wickets'] = re_df.groupby(['fixtureId', 'inns'])['is_wicket_num'].cumsum()
    re_df['wickets_in_hand'] = 10 - re_df['cum_wickets'] + re_df['is_wicket_num']  # Add back current ball wicket
    
    # Cap wickets_in_hand between 1 and 10
    re_df['wickets_in_hand'] = re_df['wickets_in_hand'].clip(1, 10)
    
    # For each delivery, calculate future runs until innings end
    # Group by fixture and innings, then calculate cumulative runs from end
    re_df['runs_scored_num'] = pd.to_numeric(re_df['runs_scored'], errors='coerce').fillna(0)
    
    # Calculate total innings runs first
    innings_totals = re_df.groupby(['fixtureId', 'inns'])['runs_scored_num'].transform('sum')
    
    # Calculate cumulative runs up to this point
    re_df['cum_runs'] = re_df.groupby(['fixtureId', 'inns'])['runs_scored_num'].cumsum()
    
    # Future runs = total - cumulative runs before this ball
    re_df['future_runs'] = innings_totals - re_df['cum_runs'] + re_df['runs_scored_num']
    
    # Now calculate average future runs for each state
    re_table = re_df.groupby(['inns', 'over_bucket', 'wickets_in_hand'])['future_runs'].mean().to_dict()
    
    return re_table, re_df


def calculate_run_value(row, re_table, next_wickets_in_hand):
    """
    Calculate Run Value for a single delivery.
    RV = RE(S_next) - RE(S_current)
    
    Dismissals are naturally penalized as they reduce wickets_in_hand.
    """
    current_state = (row['inns'], row['over_bucket'], row['wickets_in_hand'])
    
    # Next state
    next_over_bucket = row['over_bucket']  # Simplified: assume same over bucket
    next_state = (row['inns'], next_over_bucket, next_wickets_in_hand)
    
    current_re = re_table.get(current_state, 0)
    next_re = re_table.get(next_state, 0)
    
    # Run Value = runs scored + change in run expectancy
    runs_scored = row['runs_scored_num'] if pd.notna(row.get('runs_scored_num')) else 0
    
    # RV = runs scored + (next_RE - current_RE)
    # Since we're measuring the value added by this ball
    rv = runs_scored + (next_re - current_re)
    
    return rv


def calculate_risk_reward_by_shot(filtered_df, full_df):
    """
    Calculate Risk-Reward metrics for each shot type.
    
    Returns DataFrame with:
    - Shot Type
    - Expected Run Value (Reward): μ_s = E[RV | shot_type = s]
    - Wicket Probability (Risk): p_s = P(wicket | shot_type = s)
    - Frequency: number of times shot was played
    """
    if filtered_df is None or len(filtered_df) == 0:
        return pd.DataFrame()
    
    # Calculate Run Expectancy table from full dataset
    re_table, re_df = calculate_run_expectancy_table(full_df)
    
    if not re_table:
        return pd.DataFrame()
    
    # Prepare filtered data with state columns
    analysis_df = filtered_df.copy()
    analysis_df['over_bucket'] = analysis_df['over'].apply(get_over_bucket)
    
    # Calculate wickets_in_hand for filtered data
    analysis_df = analysis_df.sort_values(['fixtureId', 'inns', 'over', 'ball'])
    analysis_df['is_wicket_num'] = analysis_df['is_out'].astype(int) if 'is_out' in analysis_df.columns else 0
    analysis_df['cum_wickets'] = analysis_df.groupby(['fixtureId', 'inns'])['is_wicket_num'].cumsum()
    analysis_df['wickets_in_hand'] = 10 - analysis_df['cum_wickets'] + analysis_df['is_wicket_num']
    analysis_df['wickets_in_hand'] = analysis_df['wickets_in_hand'].clip(1, 10)
    analysis_df['runs_scored_num'] = pd.to_numeric(analysis_df['runs_scored'], errors='coerce').fillna(0)
    
    # Calculate Run Value for each delivery
    run_values = []
    for idx, row in analysis_df.iterrows():
        # Calculate next wickets_in_hand (after this ball)
        next_wickets = row['wickets_in_hand'] - row['is_wicket_num']
        next_wickets = max(1, next_wickets)
        
        rv = calculate_run_value(row, re_table, next_wickets)
        run_values.append(rv)
    
    analysis_df['run_value'] = run_values
    
    # Aggregate by shot type
    shot_types = analysis_df['shot_type'].dropna().unique()
    
    results = []
    total_balls = len(analysis_df)
    
    for shot in shot_types:
        if not shot or shot == '':
            continue
        
        shot_df = analysis_df[analysis_df['shot_type'] == shot]
        
        if len(shot_df) == 0:
            continue
        
        balls = len(shot_df)
        
        # Expected Run Value (Reward)
        expected_rv = shot_df['run_value'].mean()
        
        # Wicket Probability (Risk)
        wickets = shot_df['is_wicket_num'].sum()
        wicket_prob = wickets / balls if balls > 0 else 0
        
        # Frequency percentage
        frequency = (balls / total_balls * 100) if total_balls > 0 else 0
        
        results.append({
            'Shot Type': shot,
            'Expected Run Value': expected_rv,
            'Wicket Probability': wicket_prob,
            'Frequency': frequency,
            'Balls': balls
        })
    
    return pd.DataFrame(results)