import streamlit as st
from config.settings import APP_TITLE, PAGES

def render_header():
    """Render the main header"""
    st.markdown(f"""
        <div class="main-header">
            <h1>{APP_TITLE}</h1>
        </div>
    """, unsafe_allow_html=True)

def render_navigation(current_page=None):
    """Render the navigation buttons"""
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    # Create columns for navigation buttons
    cols = st.columns(len(PAGES))
    
    selected_page = current_page
    
    for idx, (col, page) in enumerate(zip(cols, PAGES)):
        with col:
            button_class = "nav-button-active" if page == current_page else "nav-button"
            if st.button(page, key=f"nav_{idx}", use_container_width=True):
                selected_page = page
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return selected_page

def render_navigation_radio():
    """Render navigation as radio buttons in sidebar"""
    return st.radio(
        "📊 Select Analysis",
        options=PAGES,
        index=0,
        key="main_navigation"
    )
