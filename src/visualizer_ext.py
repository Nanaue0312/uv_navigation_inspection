"""扩展的可视化功能 - 多曲线对比图表"""
import plotly.graph_objects as go
import pandas as pd


def plot_multiple_errors(df: pd.DataFrame, x_col: str, error_configs: list, 
                        title: str, ylabel: str, 
                        x_range: tuple = None, plot_mode: str = 'lines', show_fitting: bool = True):
    """
    Plot multiple error curves in one chart for comprehensive comparison.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        error_configs: List of dicts, each containing:
            - 'col': column name for error values
            - 'name': display name for the curve
            - 'color': optional color for the curve
        title: Plot title
        ylabel: Y-axis label
        x_range: tuple of (x_min, x_max) to zoom into specific time range, or None for full range
        plot_mode: 'lines', 'markers', or 'lines+markers'
        show_fitting: Whether to show curve fitting (default: True)
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Default color palette
    default_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
    
    # Prepare hover template
    custom_data = None
    if 'image_path' in df.columns:
        custom_data = df['image_path']
        hovertemplate_base = "%{y}<br>路径: %{customdata}"
    elif 'image_name' in df.columns:
        custom_data = df['image_name']
        hovertemplate_base = "%{y}<br>图片: %{customdata}"
    else:
        hovertemplate_base = "%{y}"
    
    # Add each error curve
    for idx, config in enumerate(error_configs):
        err_col = config['col']
        err_name = config['name']
        err_color = config.get('color', default_colors[idx % len(default_colors)])
        
        # Skip if column doesn't exist
        if err_col not in df.columns:
            continue
        
        # Add main error trace
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[err_col],
            mode=plot_mode,
            name=err_name,
            line=dict(color=err_color, width=2) if 'lines' in plot_mode else None,
            marker=dict(color=err_color, size=6) if 'markers' in plot_mode else None,
            customdata=custom_data,
            hovertemplate=hovertemplate_base,
            showlegend=True
        ))
        
        # Add moving average curve if in markers mode and show_fitting is True
        if 'markers' in plot_mode and show_fitting and len(df) > 5:
            ma = df[err_col].rolling(window=30, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=ma,
                mode='lines',
                name=f'{err_name} (拟合)',
                line=dict(color=err_color, width=2, dash='dot'),
                customdata=custom_data,
                hovertemplate=hovertemplate_base,
                showlegend=True
            ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='时间 (s)' if x_col == 'timestamp' else '帧号',
        yaxis_title=ylabel,
        hovermode='x unified',
        template='plotly_white',
        height=600,
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
