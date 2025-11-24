import plotly.graph_objects as go
import pandas as pd

def plot_comparison(df: pd.DataFrame, x_col: str, y1_col: str, y2_col: str, 
                   y1_label: str, y2_label: str, title: str, ylabel: str, x_range: tuple = None):
    """
    Plot comparison between two variables using Plotly for interactive zooming.
    x_range: tuple of (x_min, x_max) to zoom into specific time range, or None for full range
    Returns a Plotly Figure object.
    """
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=df[x_col], 
        y=df[y1_col],
        mode='lines',
        name=y1_label,
        line=dict(width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df[x_col], 
        y=df[y2_col],
        mode='lines',
        name=y2_label,
        line=dict(width=2, dash='dash')
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='时间 (s)',
        yaxis_title=ylabel,
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1
        ),
        dragmode='pan'
    )
    
    # Set x-axis range if specified
    if x_range:
        fig.update_xaxes(range=list(x_range))
    
    return fig

def plot_error(df: pd.DataFrame, x_col: str, err_col: str, 
              title: str, ylabel: str, bounds: tuple = None, x_range: tuple = None):
    """
    Plot error over time with moving average and optional bounds using Plotly.
    bounds: tuple of (lower_bound, upper_bound) or None
    x_range: tuple of (x_min, x_max) to zoom into specific time range, or None for full range
    Returns a Plotly Figure object.
    """
    fig = go.Figure()
    
    # Calculate moving average
    ma = df[err_col].rolling(window=30, min_periods=1).mean()
    
    # Add error trace
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[err_col],
        mode='lines',
        name='误差',
        line=dict(color='purple', width=1)
    ))
    
    # Add moving average trace
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=ma,
        mode='lines',
        name='拟合曲线',
        line=dict(color='black', width=2)
    ))
    
    # Add bounds if specified
    if bounds:
        lower_bound, upper_bound = bounds
        
        # Upper bound
        fig.add_trace(go.Scatter(
            x=[df[x_col].min(), df[x_col].max()],
            y=[upper_bound, upper_bound],
            mode='lines',
            name='上限',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        # Lower bound
        fig.add_trace(go.Scatter(
            x=[df[x_col].min(), df[x_col].max()],
            y=[lower_bound, lower_bound],
            mode='lines',
            name='下限',
            line=dict(color='blue', width=2, dash='dash')
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='时间 (s)',
        yaxis_title=ylabel,
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1
        ),
        dragmode='pan'
    )
    
    # Set x-axis range if specified
    if x_range:
        fig.update_xaxes(range=list(x_range))
    
    return fig
