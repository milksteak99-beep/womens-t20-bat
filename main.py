import streamlit as st
import os

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Women's T20s: Batting Analysis",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import components and pages
from config.settings import APP_TITLE, PAGES
from utils.data_loader import load_data
from components.footer import render_footer
from pages.home import render_home_page
from pages.line_length import render_line_length_page
from pages.bowler_wise import render_bowler_wise_page
from pages.shots_analysis import render_shots_analysis_page
from pages.shot_areas import render_shot_areas_page
from pages.ball_type import render_ball_type_page
from pages.wagon_wheels import render_wagon_wheels_page
from pages.innings_progression import render_innings_progression_page
from pages.feet_movement import render_feet_movement_page
from pages.dismissals import render_dismissals_page

# Load custom CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Additional inline CSS for dark theme
    st.markdown("""
        <style>
        /* Force dark background */
        .stApp {
            background-color: #0f172a;
        }
        
        /* HIDE SIDEBAR NAVIGATION - Multiple selectors for different Streamlit versions */
        [data-testid="stSidebarNav"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            position: absolute !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        section[data-testid="stSidebar"] > div:first-child > div:first-child > div:first-child {
            display: none !important;
        }
        
        /* Hide the page links in sidebar */
        .css-17lntkn {
            display: none !important;
        }
        
        .css-1oe5cao {
            display: none !important;
        }
        
        /* Hide any nav elements */
        nav[data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #1e293b;
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: #f8fafc;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #f8fafc !important;
        }
        
        /* Regular text */
        p, span, label, .stMarkdown {
            color: #e2e8f0;
        }
        
        /* Selectbox and multiselect */
        .stSelectbox label, .stMultiSelect label {
            color: #f8fafc !important;
        }
        
        div[data-baseweb="select"] > div {
            background-color: #1e293b;
            border-color: #334155;
        }
        
        /* Slider */
        .stSlider label {
            color: #f8fafc !important;
        }
        
        /* Date input */
        .stDateInput label {
            color: #f8fafc !important;
        }
        
        /* Info boxes */
        .stAlert {
            background-color: #1e293b;
            border: 1px solid #334155;
        }
        
        /* Radio buttons */
        .stRadio label {
            color: #f8fafc !important;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #1e293b;
        }
        ::-webkit-scrollbar-thumb {
            background: #475569;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #64748b;
        }
        
        /* Table positive/negative values */
        .positive-value {
            color: #4ade80 !important;
            font-weight: 600;
        }
        .negative-value {
            color: #f87171 !important;
            font-weight: 600;
        }
        
        /* Metric note box */
        .metrics-note {
            background-color: #1e293b;
            border-left: 4px solid #3b82f6;
            border-radius: 0 8px 8px 0;
            padding: 1rem;
            margin: 1rem 0;
            font-size: 0.85rem;
        }
        .metrics-note p {
            margin: 0.3rem 0;
            color: #cbd5e1;
        }
        .metrics-note .note-sub {
            color: #94a3b8;
            font-style: italic;
            margin-top: 0.8rem;
        }
        
        /* Styled table */
        .table-container {
            overflow-x: auto;
            margin: 1rem 0;
            border-radius: 8px;
            border: 1px solid #334155;
        }
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            background-color: #1e293b;
        }
        .styled-table thead tr {
            background-color: #0f172a;
            color: #f8fafc;
            text-align: left;
        }
        .styled-table th {
            padding: 12px 15px;
            font-weight: 600;
            border-bottom: 2px solid #3b82f6;
            white-space: nowrap;
            color: #f8fafc;
            cursor: pointer;
        }
        .styled-table th:hover {
            background-color: #334155;
        }
        .styled-table td {
            padding: 10px 15px;
            border-bottom: 1px solid #334155;
            color: #e2e8f0;
            white-space: nowrap;
        }
        .styled-table tbody tr:hover {
            background-color: #334155;
        }
        .styled-table tbody tr:nth-of-type(even) {
            background-color: #1e293b;
        }
        .styled-table tbody tr:nth-of-type(odd) {
            background-color: #0f172a;
        }
        
        /* Batter info box */
        .batter-info {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #3b82f6;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .batter-info h2 {
            color: #f8fafc;
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
        }
        .batter-info p {
            color: #94a3b8;
            margin: 0;
            font-size: 0.95rem;
        }
        .batter-info .stats-row {
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            margin-top: 0.8rem;
        }
        .batter-info .stat-item {
            display: flex;
            flex-direction: column;
        }
        .batter-info .stat-label {
            color: #64748b;
            font-size: 0.8rem;
        }
        .batter-info .stat-value {
            color: #f8fafc;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            padding: 1.5rem 0;
            margin-top: 2rem;
            border-top: 1px solid #334155;
        }
        .footer-text {
            color: #64748b;
            font-size: 0.85rem;
            margin-bottom: 0.5rem;
        }
        .social-links {
            display: flex;
            justify-content: center;
            gap: 0.8rem;
        }
        .social-link {
            color: #64748b;
            transition: color 0.2s ease;
        }
        .social-link:hover {
            color: #3b82f6;
        }
        
        /* Coming soon styling */
        .coming-soon-container {
            text-align: center;
            padding: 4rem 2rem;
            max-width: 600px;
            margin: 0 auto;
        }
        .coming-soon-title {
            color: #f8fafc;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .coming-soon-text {
            color: #3b82f6;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        .coming-soon-subtext {
            color: #94a3b8;
            font-size: 1rem;
            line-height: 1.6;
        }
        
        /* Intro page styling */
        .intro-container {
            text-align: center;
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
        }
        .intro-text {
            font-size: 1.1rem;
            line-height: 1.8;
            color: #e2e8f0;
        }
        .intro-text strong {
            color: #60a5fa;
        }
        .intro-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #3b82f6, transparent);
            margin: 2rem 0;
        }
        .developer-section {
            margin-top: 2rem;
        }
        .developer-text {
            color: #94a3b8;
            font-size: 0.95rem;
            margin-bottom: 0.8rem;
        }
        .social-links-home {
            display: flex;
            justify-content: center;
            gap: 1rem;
        }
        .social-link-home {
            color: #94a3b8;
            transition: color 0.2s ease, transform 0.2s ease;
        }
        .social-link-home:hover {
            color: #3b82f6;
            transform: translateY(-2px);
        }
        
        /* Info note styling */
        .info-note {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 0.8rem 1rem;
            margin: 1rem 0;
            color: #94a3b8;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    # Load CSS
    load_css()
    
    # Main header
    st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem 0; margin-bottom: 1rem; border-bottom: 2px solid #3b82f6;">
            <h1 style="color: #f8fafc; font-size: 2.2rem; font-weight: 700; margin: 0;">{APP_TITLE}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Initialize session state for current page and selected batter
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None
    if 'selected_batter' not in st.session_state:
        st.session_state.selected_batter = None
    
    # Navigation buttons
    cols = st.columns(len(PAGES))
    for idx, (col, page) in enumerate(zip(cols, PAGES)):
        with col:
            is_active = st.session_state.current_page == page
            button_style = "primary" if is_active else "secondary"
            if st.button(page, key=f"nav_{page}", use_container_width=True, type=button_style):
                st.session_state.current_page = page
                st.rerun()
    
    # Check if data is loaded
    if df is None:
        st.error("Data file not found!")
        st.info("Please place your `wt20.csv` file in the `data` folder and refresh the page.")
        st.markdown("""
            ### Expected file location:
```
            wt20-bat/
            └── data/
                └── wt20.csv
```
        """)
        return
    
    # Render the appropriate page
    current_page = st.session_state.current_page
    
    if current_page is None:
        render_home_page()
    elif current_page == "Line-Length wise":
        render_line_length_page(df)
    elif current_page == "Bowler wise":
        render_bowler_wise_page(df)
    elif current_page == "Shots Analysis":
        render_shots_analysis_page(df)
    elif current_page == "Shot Areas":
        render_shot_areas_page(df)
    elif current_page == "Ball type specific":
        render_ball_type_page(df)
    elif current_page == "Wagon Wheels":
        render_wagon_wheels_page(df)
    elif current_page == "Innings Progression":
        render_innings_progression_page(df)
    elif current_page == "Feet Movement":
        render_feet_movement_page(df)
    elif current_page == "Dismissals":
        render_dismissals_page(df)
    else:
        render_home_page()

if __name__ == "__main__":
    main()