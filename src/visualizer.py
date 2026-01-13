import plotly.graph_objects as go
import pandas as pd

def plot_comparison(df: pd.DataFrame, x_col: str, y1_col: str, y2_col: str, 
                   y1_label: str, y2_label: str, title: str, ylabel: str, 
                   x_range: tuple = None, plot_mode: str = 'lines', show_fitting: bool = True):
    """
    Plot comparison between two variables using Plotly for interactive zooming.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y1_col: Column name for first y variable
        y2_col: Column name for second y variable
        y1_label: Label for first variable
        y2_label: Label for second variable
        title: Plot title
        ylabel: Y-axis label
        x_range: tuple of (x_min, x_max) to zoom into specific time range, or None for full range
        plot_mode: 'lines', 'markers', or 'lines+markers'
        show_fitting: Whether to show curve fitting for markers mode (default: True)
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Determine marker settings based on mode
    marker_dict = dict(size=6) if 'markers' in plot_mode else None
    
    # Prepare hover template
    custom_data = None
    if 'image_path' in df.columns:
        custom_data = df['image_path']
        hovertemplate = "%{y}<br>路径: %{customdata}"
    elif 'image_name' in df.columns:
        custom_data = df['image_name']
        hovertemplate = "%{y}<br>图片: %{customdata}"
    else:
        hovertemplate = "%{y}"

    # Add first trace (Ground Truth)
    fig.add_trace(go.Scatter(
        x=df[x_col], 
        y=df[y1_col],
        mode=plot_mode,
        name=y1_label,
        line=dict(width=2) if 'lines' in plot_mode else None,
        marker=marker_dict,
        customdata=custom_data,
        hovertemplate=hovertemplate
    ))
    
    # Add curve fitting for first trace (if markers mode and show_fitting)
    if 'markers' in plot_mode and show_fitting and 'lines' not in plot_mode:
        ma1 = df[y1_col].rolling(window=30, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=ma1,
            mode='lines',
            name=f'{y1_label} 拟合',
            line=dict(width=2),
            visible='legendonly'
        ))
    
    # Add second trace (Algorithm Output)
    fig.add_trace(go.Scatter(
        x=df[x_col], 
        y=df[y2_col],
        mode=plot_mode,
        name=y2_label,
        line=dict(width=2, dash='dash') if 'lines' in plot_mode else None,
        marker=dict(size=6, symbol='x') if 'markers' in plot_mode else None,
        customdata=custom_data,
        hovertemplate=hovertemplate
    ))
    
    # Add curve fitting for second trace (if markers mode and show_fitting)
    if 'markers' in plot_mode and show_fitting and 'lines' not in plot_mode:
        ma2 = df[y2_col].rolling(window=30, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=ma2,
            mode='lines',
            name=f'{y2_label} 拟合',
            line=dict(width=2, dash='dash'),
            visible='legendonly'
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
              title: str, ylabel: str, bounds: tuple = None, 
              x_range: tuple = None, plot_mode: str = 'lines', show_fitting: bool = True):
    """
    Plot error over time with moving average and optional bounds using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        err_col: Column name for error values
        title: Plot title
        ylabel: Y-axis label
        bounds: tuple of (lower_bound, upper_bound) or None
        x_range: tuple of (x_min, x_max) to zoom into specific time range, or None for full range
        plot_mode: 'lines', 'markers', or 'lines+markers'
        show_fitting: Whether to show curve fitting (default: True)
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Calculate moving average for curve fitting
    ma = df[err_col].rolling(window=30, min_periods=1).mean()
    
    # Prepare hover template
    custom_data = None
    if 'image_path' in df.columns:
        custom_data = df['image_path']
        hovertemplate = "%{y}<br>路径: %{customdata}"
    elif 'image_name' in df.columns:
        custom_data = df['image_name']
        hovertemplate = "%{y}<br>图片: %{customdata}"
    else:
        hovertemplate = "%{y}"

    # Add error trace
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[err_col],
        mode=plot_mode,
        name='误差',
        line=dict(color='purple', width=1) if 'lines' in plot_mode else None,
        marker=dict(color='purple', size=6) if 'markers' in plot_mode else None,
        customdata=custom_data,
        hovertemplate=hovertemplate
    ))
    
    # Add moving average trace (curve fitting) if enabled
    if show_fitting:
        # For markers-only mode or lines+markers mode, show fitting curve
        if 'markers' in plot_mode:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=ma,
                mode='lines',
                name='拟合曲线',
                line=dict(color='black', width=2),
                visible='legendonly'
            ))
        # For lines-only mode, also show fitting but default hidden
        elif plot_mode == 'lines':
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=ma,
                mode='lines',
                name='拟合曲线',
                line=dict(color='black', width=2),
                visible='legendonly'
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
