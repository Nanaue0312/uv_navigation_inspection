import plotly.graph_objects as go
import pandas as pd
import numpy as np


def _apply_fitting(df: pd.DataFrame, x_col: str, y_col: str, 
                   method: str = 'moving_average', window: int = 10, degree: int = 3):
    """
    Apply curve fitting to data.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y values to fit
        method: 'moving_average', 'polynomial', 'savgol', or 'ewma'
        window: Window size for moving average (default: 10)
        degree: Polynomial degree for least squares fitting (default: 3)
    
    Returns:
        Fitted y values as a Series or array
    """
    if method == 'moving_average':
        # 滑动平均法
        return df[y_col].rolling(window=window, min_periods=1, center=True).mean()
    elif method == 'savgol':
        # Savitzky-Golay 滤波器 - 保留峰值特征
        from scipy.signal import savgol_filter
        y = df[y_col].values
        
        # 去除 NaN 值
        valid_mask = ~np.isnan(y)
        if valid_mask.sum() < window:
            # 数据点不足，降级到滑动平均
            return df[y_col].rolling(window=max(3, window//2), min_periods=1, center=True).mean()
        
        # 确保窗口是奇数
        window_size = window if window % 2 == 1 else window + 1
        window_size = min(window_size, valid_mask.sum())
        if window_size % 2 == 0:
            window_size -= 1
        
        # polyorder 必须小于 window_size
        poly_order = min(degree, window_size - 1)
        
        try:
            # 对有效数据进行滤波
            y_copy = y.copy()
            y_copy[valid_mask] = savgol_filter(y[valid_mask], window_size, poly_order)
            return pd.Series(y_copy, index=df.index)
        except:
            # 如果失败，降级到滑动平均
            return df[y_col].rolling(window=window, min_periods=1, center=True).mean()
    elif method == 'ewma':
        # 指数加权移动平均 - 对近期数据赋予更高权重
        alpha = 2.0 / (window + 1)  # 转换为衰减因子
        return df[y_col].ewm(alpha=alpha, adjust=False, ignore_na=True).mean()
    elif method == 'polynomial':
        # 最小二乘多项式拟合
        x = np.arange(len(df))  # Use index as x for polynomial fitting
        y = df[y_col].values
        
        # 去除 NaN 值
        valid_mask = ~np.isnan(y)
        if valid_mask.sum() < degree + 1:
            # 数据点不足，降级到滑动平均
            return df[y_col].rolling(window=window, min_periods=1, center=True).mean()
        
        x_valid = x[valid_mask]
        y_valid = y[valid_mask]
        
        # 多项式拟合
        coeffs = np.polyfit(x_valid, y_valid, degree)
        poly = np.poly1d(coeffs)
        
        # 对所有点进行预测
        fitted = poly(x)
        return pd.Series(fitted, index=df.index)
    else:
        # 默认使用滑动平均
        return df[y_col].rolling(window=window, min_periods=1, center=True).mean()

def plot_comparison(df: pd.DataFrame, x_col: str, y1_col: str, y2_col: str, 
                   y1_label: str, y2_label: str, title: str, ylabel: str, 
                   x_range: tuple = None, plot_mode: str = 'lines', show_fitting: bool = True,
                   fitting_method: str = 'moving_average', fitting_window: int = 10, poly_degree: int = 3):
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
        fitting_method: 'moving_average' or 'polynomial' (default: 'moving_average')
        fitting_window: Window size for moving average (default: 10)
        poly_degree: Polynomial degree for least squares fitting (default: 3)
    
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
        # 添加滑动平均拟合
        fitted1_ma = _apply_fitting(df, x_col, y1_col, 'moving_average', fitting_window, poly_degree)
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=fitted1_ma,
            mode='lines',
            name=f'{y1_label} 拟合(滑动平均)',
            line=dict(width=2),
            visible=True  # 默认显示
        ))
        
        # 添加最小二乘多项式拟合
        fitted1_poly = _apply_fitting(df, x_col, y1_col, 'polynomial', fitting_window, poly_degree)
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=fitted1_poly,
            mode='lines',
            name=f'{y1_label} 拟合(多项式)',
            line=dict(width=2, dash='dot'),
            visible=True  # 默认显示
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
        # 添加滑动平均拟合
        fitted2_ma = _apply_fitting(df, x_col, y2_col, 'moving_average', fitting_window, poly_degree)
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=fitted2_ma,
            mode='lines',
            name=f'{y2_label} 拟合(滑动平均)',
            line=dict(width=2, dash='dash'),
            visible=True  # 默认显示
        ))
        
        # 添加最小二乘多项式拟合
        fitted2_poly = _apply_fitting(df, x_col, y2_col, 'polynomial', fitting_window, poly_degree)
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=fitted2_poly,
            mode='lines',
            name=f'{y2_label} 拟合(多项式)',
            line=dict(width=2, dash='dashdot'),
            visible=True  # 默认显示
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
              x_range: tuple = None, plot_mode: str = 'lines', show_fitting: bool = True,
              fitting_method: str = 'moving_average', fitting_window: int = 10, poly_degree: int = 3):
    """
    Plot error over time with curve fitting and optional bounds using Plotly.
    
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
        fitting_method: 'moving_average' or 'polynomial' (default: 'moving_average')
        fitting_window: Window size for moving average (default: 10)
        poly_degree: Polynomial degree for least squares fitting (default: 3)
    
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Calculate curve fitting - both methods
    fitted_ma = _apply_fitting(df, x_col, err_col, 'moving_average', fitting_window, poly_degree)
    # 对误差数据使用 Savitzky-Golay 滤波代替多项式拟合
    fitted_savgol = _apply_fitting(df, x_col, err_col, 'savgol', fitting_window, poly_degree)
    
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
    
    # Add curve fitting traces if enabled
    if show_fitting:
        # For markers-only mode or lines+markers mode, show fitting curves
        if 'markers' in plot_mode:
            # 添加滑动平均拟合
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=fitted_ma,
                mode='lines',
                name='拟合曲线(滑动平均)',
                line=dict(color='black', width=2),
                visible=True  # 默认显示
            ))
            # 添加 Savitzky-Golay 滤波拟合（更适合误差数据）
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=fitted_savgol,
                mode='lines',
                name='拟合曲线(SavGol滤波)',
                line=dict(color='darkgreen', width=2, dash='dot'),
                visible=True  # 默认显示
            ))
        # For lines-only mode, also show fitting but default hidden
        elif plot_mode == 'lines':
            # 添加滑动平均拟合
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=fitted_ma,
                mode='lines',
                name='拟合曲线(滑动平均)',
                line=dict(color='black', width=2),
                visible='legendonly'
            ))
            # 添加 Savitzky-Golay 滤波拟合
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=fitted_savgol,
                mode='lines',
                name='拟合曲线(SavGol滤波)',
                line=dict(color='darkgreen', width=2, dash='dot'),
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
