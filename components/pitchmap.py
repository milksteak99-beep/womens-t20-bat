import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config.settings import (
    LENGTHS, LENGTHS_DISPLAY, LENGTH_HEIGHTS,
    LINES_RHB, LINES_LHB, LINES_DISPLAY,
    get_control_color, get_average_color, get_sr_color
)

def create_pitchmap_with_legend(pitchmap_data, metric_type, batter_hand, title):
    """
    Create a pitchmap with legend on the right side using subplots.
    """
    # Determine line order based on batter hand
    lines = LINES_RHB if batter_hand == "Right" else LINES_LHB
    
    # Get color function and settings based on metric type
    if metric_type == 'control':
        get_color = get_control_color
        suffix = ""  # No % symbol
        legend_ranges = ['85-100', '70-85', '55-70', '40-55', '25-40', '0-25']
    elif metric_type == 'average':
        get_color = get_average_color
        suffix = ""
        legend_ranges = ['60+', '45-60', '30-45', '20-30', '10-20', '0-10']
    else:  # sr
        get_color = get_sr_color
        suffix = ""
        legend_ranges = ['160+', '130-160', '100-130', '80-100', '50-80', '0-50']
    
    legend_colors = [
        'rgba(100, 200, 80, 0.8)',
        'rgba(180, 220, 80, 0.8)',
        'rgba(240, 220, 80, 0.8)',
        'rgba(250, 170, 80, 0.8)',
        'rgba(240, 120, 80, 0.8)',
        'rgba(220, 80, 80, 0.8)'
    ]
    
    # Create subplot with pitchmap on left (wider) and legend on right (narrower)
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.85, 0.15],
        horizontal_spacing=0.02
    )
    
    # Calculate positions for pitchmap
    total_height = sum(LENGTH_HEIGHTS)
    y_positions = []
    current_y = total_height
    for height in LENGTH_HEIGHTS:
        current_y -= height
        y_positions.append(current_y)
    
    # Add pitchmap rectangles
    for length_idx, (length, length_display, height) in enumerate(zip(LENGTHS, LENGTHS_DISPLAY, LENGTH_HEIGHTS)):
        y_bottom = y_positions[length_idx]
        y_top = y_bottom + height
        
        for line_idx, line in enumerate(lines):
            x_left = line_idx
            x_right = line_idx + 1
            
            # Get value for this cell
            value = pitchmap_data.get((length, line), None)
            
            # Get color - use neutral color for None/blank values
            if value is None:
                color = "rgba(50, 50, 50, 0.6)"
                display_value = "-"
            else:
                color = get_color(value)
                display_value = f"{value:.1f}{suffix}"
            
            # Add rectangle
            fig.add_shape(
                type="rect",
                x0=x_left, y0=y_bottom,
                x1=x_right, y1=y_top,
                fillcolor=color,
                line=dict(color="rgba(255,255,255,0.4)", width=1),
                row=1, col=1
            )
            
            # Add text annotation - regular font, not bold
            fig.add_annotation(
                x=(x_left + x_right) / 2,
                y=(y_bottom + y_top) / 2,
                text=display_value,
                showarrow=False,
                font=dict(color="white", size=11, family="Arial"),
                row=1, col=1
            )
    
    # Add length labels on the left
    for length_idx, (length_display, height) in enumerate(zip(LENGTHS_DISPLAY, LENGTH_HEIGHTS)):
        y_bottom = y_positions[length_idx]
        y_center = y_bottom + height / 2
        fig.add_annotation(
            x=-0.3,
            y=y_center,
            text=length_display,
            showarrow=False,
            font=dict(color="white", size=9),
            xanchor="right",
            xref="x1",
            yref="y1"
        )
    
    # Add line labels on top
    line_displays = LINES_DISPLAY if batter_hand == "Right" else LINES_DISPLAY[::-1]
    for line_idx, line_display in enumerate(line_displays):
        fig.add_annotation(
            x=line_idx + 0.5,
            y=total_height + 0.3,
            text=line_display,
            showarrow=False,
            font=dict(color="white", size=8),
            textangle=-45,
            xref="x1",
            yref="y1"
        )
    
    # Add legend on the right side (col=2)
    box_height = total_height / len(legend_ranges)
    for i, (range_text, color) in enumerate(zip(legend_ranges, legend_colors)):
        y_pos = total_height - (i + 1) * box_height
        
        # Add colored rectangle for legend
        fig.add_shape(
            type="rect",
            x0=0, y0=y_pos,
            x1=0.4, y1=y_pos + box_height * 0.85,
            fillcolor=color,
            line=dict(color="rgba(255,255,255,0.3)", width=1),
            row=1, col=2
        )
        
        # Add range text
        fig.add_annotation(
            x=0.5,
            y=y_pos + box_height * 0.4,
            text=range_text,
            showarrow=False,
            font=dict(color="white", size=9),
            xanchor="left",
            xref="x2",
            yref="y2"
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(color="white", size=16),
            x=0.4
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=90, r=20, t=80, b=20),
        height=500,
        showlegend=False
    )
    
    # Update x and y axes for pitchmap (col 1)
    fig.update_xaxes(
        showgrid=False,
        showticklabels=False,
        range=[-1.2, 6.5],
        fixedrange=True,
        row=1, col=1
    )
    fig.update_yaxes(
        showgrid=False,
        showticklabels=False,
        range=[-0.5, total_height + 1.5],
        fixedrange=True,
        row=1, col=1
    )
    
    # Update x and y axes for legend (col 2)
    fig.update_xaxes(
        showgrid=False,
        showticklabels=False,
        range=[-0.2, 2],
        fixedrange=True,
        row=1, col=2
    )
    fig.update_yaxes(
        showgrid=False,
        showticklabels=False,
        range=[-0.5, total_height + 0.5],
        fixedrange=True,
        row=1, col=2
    )
    
    return fig

def render_pitchmaps_section(control_data, average_data, sr_data, batter_hand):
    """Render all three pitchmaps with their legends on the right"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fig_control = create_pitchmap_with_legend(control_data, 'control', batter_hand, 'Control %')
        st.plotly_chart(fig_control, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        fig_average = create_pitchmap_with_legend(average_data, 'average', batter_hand, 'Average')
        st.plotly_chart(fig_average, use_container_width=True, config={'displayModeBar': False})
    
    with col3:
        fig_sr = create_pitchmap_with_legend(sr_data, 'sr', batter_hand, 'Strike Rate')
        st.plotly_chart(fig_sr, use_container_width=True, config={'displayModeBar': False})