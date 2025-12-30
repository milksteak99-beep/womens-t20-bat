import streamlit as st
from utils.filters import create_batter_selector, create_filter_widgets

def render_sidebar(df, page_type="default", key_prefix=""):
    """Render the sidebar with batter selector and filters"""
    with st.sidebar:
        st.markdown("## Batter Selection")
        
        # Batter selector with session state preservation
        selected_batter = create_batter_selector(df, key_prefix)
        
        # Update session state
        if selected_batter:
            st.session_state.selected_batter = selected_batter
        
        st.markdown("---")
        
        # Filters
        filters = create_filter_widgets(df, page_type, key_prefix)
        
        return selected_batter, filters
