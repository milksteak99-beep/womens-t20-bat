# App-wide settings and configurations

APP_TITLE = "Women's T20s: Batting Analysis"

# Date range for the dataset
MIN_DATE = "2019-07-26"
MAX_DATE = "2025-10-30"

# Social links
SOCIAL_LINKS = {
    "twitter": "https://x.com/rhitankar?s=21",
    "github": "https://github.com/rhitankar8616",
    "linkedin": "https://www.linkedin.com/in/rhitankar-bandyopadhyay-a2099227b/"
}

# Navigation pages
PAGES = [
    "Line-Length wise",
    "Bowler wise",
    "Shots Analysis",
    "Shot Areas",
    "Ball type specific",
    "Wagon Wheels",
    "Innings Progression",
    "Feet Movement",
    "Dismissals"
]

# Pitchmap configurations
LENGTHS = ["full toss", "yorker", "half volley", "length ball", "back of a length", "short", "bouncer"]
LENGTHS_DISPLAY = ["Full Toss", "Yorker", "Half Volley", "Length Ball", "Back of a Length", "Short", "Bouncer"]
LENGTH_HEIGHTS = [1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 2.0]

LINES_RHB = ["wide outside off", "outside off", "off", "middle", "leg", "down leg"]
LINES_LHB = ["down leg", "leg", "middle", "off", "outside off", "wide outside off"]
LINES_DISPLAY = ["Wide Outside Off", "Outside Off", "Off", "Middle", "Leg", "Down Leg"]

# Color scales for pitchmaps (red to green gradient)
def get_control_color(value):
    """Color scale for Control % (0-100)"""
    if value is None or value == 0:
        return "rgba(180, 60, 60, 0.8)"  # Dark red
    elif value < 25:
        return "rgba(220, 80, 80, 0.8)"  # Red
    elif value < 40:
        return "rgba(240, 120, 80, 0.8)"  # Orange-red
    elif value < 55:
        return "rgba(250, 170, 80, 0.8)"  # Orange
    elif value < 70:
        return "rgba(240, 220, 80, 0.8)"  # Yellow
    elif value < 85:
        return "rgba(180, 220, 80, 0.8)"  # Yellow-green
    else:
        return "rgba(100, 200, 80, 0.8)"  # Green

def get_average_color(value):
    """Color scale for Average (0-80+)"""
    if value is None or value == 0:
        return "rgba(180, 60, 60, 0.8)"
    elif value < 10:
        return "rgba(220, 80, 80, 0.8)"
    elif value < 20:
        return "rgba(240, 120, 80, 0.8)"
    elif value < 30:
        return "rgba(250, 170, 80, 0.8)"
    elif value < 45:
        return "rgba(240, 220, 80, 0.8)"
    elif value < 60:
        return "rgba(180, 220, 80, 0.8)"
    else:
        return "rgba(100, 200, 80, 0.8)"

def get_sr_color(value):
    """Color scale for Strike Rate (0-200+)"""
    if value is None or value == 0:
        return "rgba(180, 60, 60, 0.8)"
    elif value < 50:
        return "rgba(220, 80, 80, 0.8)"
    elif value < 80:
        return "rgba(240, 120, 80, 0.8)"
    elif value < 100:
        return "rgba(250, 170, 80, 0.8)"
    elif value < 130:
        return "rgba(240, 220, 80, 0.8)"
    elif value < 160:
        return "rgba(180, 220, 80, 0.8)"
    else:
        return "rgba(100, 200, 80, 0.8)"

# Effective metrics definitions
EFFECTIVE_METRICS_NOTE = """
**eSR**: Measure of the selected batter's effective SR in comparison to an average batter.

**eControl**: Measure of the selected batter's effective Control in comparison to an average batter.

**eAerial**: Measure of the selected batter's effective Aerial shots frequency in comparison to an average batter.

*(An average batter is a crude quantification of all batters involved in the matches for which the selected batter and set of filters have been chosen.)*
"""

# Column mappings for clarity
COLUMN_MAPPINGS = {
    "batsman": "batsman",
    "bowler": "bowler",
    "batting_team": "battingTeam",
    "bowling_team": "bowlingTeam",
    "competition": "competition",
    "ground": "ground",
    "country": "country",
    "over": "over",
    "ball": "ball",
    "innings": "inns",
    "runs_scored": "runs_scored",
    "is_wicket": "is_wicket",
    "dismissal_type": "dismissalType",
    "parsed_length": "parsed_length",
    "parsed_line": "parsed_line",
    "parsed_control": "parsed_control",
    "control": "control",
    "elevation": "elevation",
    "shot_type": "shot_type",
    "fielding_position": "fielding_position",
    "foot": "foot",
    "variation": "variation",
    "parsed_len_var": "parsed_len.var",
    "bowler_type": "bowlerType",
    "bowler_hand": "bowlerHand",
    "bowling_angle": "bowlingAngle",
    "batsman_hand": "batsmanHand",
    "timestamp": "timestamp",
    "match_date": "matchDate",
    "fixture_id": "fixtureId"
}
