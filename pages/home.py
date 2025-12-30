import streamlit as st
from config.settings import SOCIAL_LINKS
from components.footer import render_footer

def render_home_page():
    """Render the introductory home page"""
    
    # Main content area
    st.markdown("""
        <div class="intro-container">
            <div class="intro-text">
                <p>
                    This app analyzes ball-by-ball data for <strong>1,98,787 deliveries</strong>, 
                    involving <strong>783 batters</strong> and <strong>552 bowlers</strong> across 
                    <strong>874 matches</strong> in women's T20 cricket played between 
                    <strong>July 26, 2019</strong> to <strong>October 30, 2025</strong>.
                </p>
                <p>
                    Select a batter and suitable filters to view raw stats, pitchmaps, 
                    wagon wheels, shots analysis and more.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Footer with developer info
    render_footer()
