import streamlit as st
import numpy as np
import pandas as pd
from src.data_loader import load_data
from src.processor import process_frames
from src.visualizer import plot_comparison, plot_error
from src.visualizer_ext import plot_multiple_errors

st.set_page_config(page_title="算法性能评估工具", layout="wide")

def show_help_page():
    """显示字段说明帮助页面"""
    st.title("数据字段说明")
    st.markdown("本页面详细说明分析数据中各个字段的含义和用途。")
    
    # 基本信息
    st.header("基本信息")
    help_data_basic = [
        ("No", "当前行行号"),
        ("image_path", "对应图片的路径（相对于数据集根目录），用于关联数据与对应的图像文件"),
    ]
    for field, desc in help_data_basic:
        st.markdown(f"**{field}**: {desc}")
    
    # 无人机姿态参数
    st.header("无人机姿态参数（欧拉角）")
    help_data_drone = [
        ("drone_roll_deg", "无人机的横滚角，是无人机姿态（欧拉角）的参数之一，单位为度"),
        ("drone_pitch_deg", "无人机的俯仰角，是无人机姿态（欧拉角）的参数之一，单位为度"),
        ("drone_yaw_deg", "无人机的航向角，是无人机姿态（欧拉角）的参数之一，单位为度"),
    ]
    for field, desc in help_data_drone:
        st.markdown(f"**{field}**: {desc}")
    
    # 相机安装参数
    st.header("相机安装参数")
    help_data_camera = [
        ("cam_mount_pitch_deg", "相机安装在无人机上的俯仰角（相机安装参数），单位为度，设置为 0 以简化处理（让相机与飞机状态重合）"),
        ("cam_offset_z_m", "相机安装在无人机上的高度偏移量（相机安装参数），单位为米，设置为 0 以简化处理（让相机与飞机状态重合）"),
        ("gain_percent", "相机的增益百分比，取值范围为 0-100，用于描述相机的成像参数（未使用此参数）"),
    ]
    for field, desc in help_data_camera:
        st.markdown(f"**{field}**: {desc}")
    
    # 无人机位置参数（NED坐标系）
    st.header("无人机位置参数（NED坐标系）")
    st.info("NED坐标系：N(North-北向/前向)、E(East-东向/右向)、D(Down-下向)")
    help_data_drone_pos = [
        ("drone_x_ned_m", "无人机在 NED 坐标系下的 X 轴坐标（对应北向 / 前向），单位为米"),
        ("drone_y_ned_m", "无人机在 NED 坐标系下的 Y 轴坐标（对应东向 / 右向），单位为米"),
        ("drone_z_ned_m", "无人机在 NED 坐标系下的 Z 轴坐标（对应下向），单位为米"),
    ]
    for field, desc in help_data_drone_pos:
        st.markdown(f"**{field}**: {desc}")
    
    # 目标位置参数（NED坐标系）
    st.header("目标位置参数（NED坐标系）")
    help_data_target_pos = [
        ("target_x_ned_m", "目标在 NED 坐标系下的 X 轴坐标（对应北向 / 前向），单位为米"),
        ("target_y_ned_m", "目标在 NED 坐标系下的 Y 轴坐标（对应东向 / 右向），单位为米"),
        ("target_z_ned_m", "目标在 NED 坐标系下的 Z 轴坐标（对应下向），单位为米"),
    ]
    for field, desc in help_data_target_pos:
        st.markdown(f"**{field}**: {desc}")
    
    # 目标姿态参数
    st.header("目标姿态参数（欧拉角）")
    help_data_target_att = [
        ("target_roll_deg", "目标的横滚角，是目标姿态（欧拉角）的参数之一，单位为度"),
        ("target_pitch_deg", "目标的俯仰角，是目标姿态（欧拉角）的参数之一，单位为度"),
        ("target_yaw_deg", "目标的航向角，是目标姿态（欧拉角）的参数之一，单位为度"),
    ]
    for field, desc in help_data_target_att:
        st.markdown(f"**{field}**: {desc}")
    
    # 距离测量
    st.header("距离测量")
    help_data_distance = [
        ("真值距离 (m)", "无人机与目标之间实际距离的真实值，单位为米"),
        ("算法距离 (m)", "通过算法计算得到的无人机与目标之间的距离，单位为米"),
        ("直接距离误差 (m)", '"算法距离" 与 "真值距离" 的差值，用于评估算法的距离计算精度'),
    ]
    for field, desc in help_data_distance:
        st.markdown(f"**{field}**: {desc}")
    
    # 侧向位置
    st.header("侧向位置测量")
    help_data_lateral = [
        ("真值侧向 (m)", "无人机与目标在侧向（通常对应 NED 坐标系 Y 轴）相对位置的真实值，单位为米"),
        ("算法侧向 (m)", "通过算法计算得到的无人机与目标在侧向的相对位置，单位为米"),
        ("侧向误差 (m)", '"算法侧向" 与 "真值侧向" 的差值，用于评估算法的侧向位置计算精度'),
    ]
    for field, desc in help_data_lateral:
        st.markdown(f"**{field}**: {desc}")
    
    # 纵向位置
    st.header("纵向位置测量")
    help_data_longitudinal = [
        ("真值纵向 (m)", "无人机与目标在纵向（通常对应 NED 坐标系 X 轴）相对位置的真实值，单位为米"),
        ("算法纵向 (m)", "通过算法计算得到的无人机与目标在纵向的相对位置，单位为米"),
        ("纵向误差 (m)", '"算法纵向" 与 "真值纵向" 的差值，用于评估算法的纵向位置计算精度'),
    ]
    for field, desc in help_data_longitudinal:
        st.markdown(f"**{field}**: {desc}")
    
    # 高度位置
    st.header("高度位置测量")
    help_data_height = [
        ("真值高度 (m)", "无人机与目标在高度方向（通常对应 NED 坐标系 Z 轴）相对位置的真实值，单位为米"),
        ("算法高度 (m)", "通过算法计算得到的无人机与目标在高度方向的相对位置，单位为米"),
        ("高度误差 (m)", '"算法高度" 与 "真值高度" 的差值，用于评估算法的高度计算精度'),
    ]
    for field, desc in help_data_height:
        st.markdown(f"**{field}**: {desc}")
    
    # 偏航角
    st.header("偏航光轴偏差角测量")
    help_data_yaw = [
        ("真值偏航光轴偏差角(°)", "目标偏航角的真实变化量"),
        ("算法偏航光轴偏差角(°)", "算法计算得到的目标偏航角变化量"),
        ("偏航误差 (°)", "算法计算的偏航角与真实偏航角的差值，单位为度，用于评估姿态计算精度"),
    ]
    for field, desc in help_data_yaw:
        st.markdown(f"**{field}**: {desc}")
    
    # 俯仰角
    st.header("俯仰光轴偏差角测量")
    help_data_pitch = [
        ("真值俯仰光轴偏差角(°)", "目标俯仰角的真实变化量"),
        ("算法俯仰光轴偏差角(°)", "算法计算得到的目标俯仰角变化量"),
        ("俯仰误差 (°)", "算法计算的俯仰角与真实俯仰角的差值，单位为度，用于评估姿态计算精度"),
    ]
    for field, desc in help_data_pitch:
        st.markdown(f"**{field}**: {desc}")
    
    # 置信度
    st.header("算法输出质量")
    st.markdown("**置信度**: 算法输出结果的可靠程度（通常为 0-1），置信度越高代表结果越可靠")

def main():
    st.title("紫外定位数据分析")
    st.markdown("上传 `analysis_data.json` 文件以生成性能评估图表。")
    
    uploaded_file = st.file_uploader("选择数据文件 (JSON)", type=['json'])
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
            data = load_data(content)
            
            # Extract data components
            metadata = data.get('metadata', {})
            statistics = data.get('statistics', {})
            frames = data.get('frames', [])
            
            if not frames:
                st.error("未在文件中找到帧数据 (frames)。")
                return
            
            # Display metadata in sidebar
            with st.sidebar:
                st.header("仿真信息")
                sim_config = metadata.get('simulation_config', {})
                scenario = metadata.get('scenario', {})
                
                st.subheader("基本信息")
                st.text(f"仿真ID: {metadata.get('simulation_id', 'N/A')}")
                st.text(f"格式版本: {metadata.get('format_version', 'N/A')}")
                st.text(f"软件版本: {metadata.get('software_version', 'N/A')}")
                
                st.subheader("场景配置")
                st.text(f"仿真时长: {sim_config.get('duration_seconds', 'N/A')} s")
                st.text(f"帧率: {sim_config.get('frame_rate', 'N/A')} fps")
                st.text(f"下滑道: {scenario.get('glide_path', 'N/A')}")
                st.text(f"海况: {scenario.get('sea_state', 'N/A')}")
                
                # 添加帮助按钮
                # st.markdown("---")
                # if st.button("查看字段说明帮助", width='stretch', type="secondary"):
                #     st.session_state.show_help = True
                #     st.rerun()
                
                # Plot mode selection
                st.subheader("图表显示模式")
                plot_mode = st.radio(
                    "选择显示方式",
                    options=['lines', 'markers', 'lines+markers'],
                    format_func=lambda x: {'lines': '折线图', 
                                          'markers': '散点图', 
                                          'lines+markers': '折线+散点'}[x],
                    index=2,
                    key='plot_mode'
                )
                
                # Curve fitting toggle
                show_fitting = st.toggle(
                    "显示曲线拟合", 
                    value=False, 
                    help="同时显示滑动平均和SavGol滤波拟合（更适合误差数据）"
                )
                
                # Curve fitting parameters
                if show_fitting:
                    fitting_window = st.slider(
                        "拟合窗口大小",
                        min_value=3,
                        max_value=50,
                        value=10,
                        step=1,
                        help="窗口越小越贴近原始数据，越大越平滑"
                    )
                else:
                    fitting_window = 10
                
                # 固定参数（不再对用户暴露）
                poly_degree = 3  # SavGol滤波和多项式拟合的默认次数
                # 保留兼容性参数
                fitting_method = 'moving_average'  # 不再使用，但保留参数传递
                
                st.subheader("数据过滤")
                filter_low_conf = st.toggle("过滤低置信度/异常数据", value=True, help="开启后将隐藏置信度<0.5或算法输出为0的异常点")
                
                # Error bound configuration with input fields
                st.subheader("误差上限/下限配置")
                
                # Initialize session state defaults if not already set
                if 'dist_lower' not in st.session_state:
                    st.session_state.dist_lower = -1.6
                if 'dist_upper' not in st.session_state:
                    st.session_state.dist_upper = 1.6
                if 'lat_lower' not in st.session_state:
                    st.session_state.lat_lower = -1.6
                if 'lat_upper' not in st.session_state:
                    st.session_state.lat_upper = 1.6
                if 'lon_lower' not in st.session_state:
                    st.session_state.lon_lower = -1.6
                if 'lon_upper' not in st.session_state:
                    st.session_state.lon_upper = 1.6
                if 'height_lower' not in st.session_state:
                    st.session_state.height_lower = -1.6
                if 'height_upper' not in st.session_state:
                    st.session_state.height_upper = 1.6
                if 'dyaw_lower' not in st.session_state:
                    st.session_state.dyaw_lower = -1.5
                if 'dyaw_upper' not in st.session_state:
                    st.session_state.dyaw_upper = 1.5
                if 'dpitch_lower' not in st.session_state:
                    st.session_state.dpitch_lower = -1.5
                if 'dpitch_upper' not in st.session_state:
                    st.session_state.dpitch_upper = 1.5
                
                # Callback functions for preset buttons
                def set_distance_preset(val):
                    st.session_state.dist_lower = -val
                    st.session_state.dist_upper = val
                    st.session_state.lat_lower = -val
                    st.session_state.lat_upper = val
                    st.session_state.lon_lower = -val
                    st.session_state.lon_upper = val
                    st.session_state.height_lower = -val
                    st.session_state.height_upper = val
                
                def set_angle_preset(val):
                    st.session_state.dyaw_lower = -val
                    st.session_state.dyaw_upper = val
                    st.session_state.dpitch_lower = -val
                    st.session_state.dpitch_upper = val
                
                # Quick preset buttons - optimized layout
                st.markdown("**快速配置**")
                
                # Distance error presets - first row
                st.caption("直接距离误差 (m)")
                preset_cols_dist = st.columns(6)
                distance_presets = [3.0, 2.0, 1.6, 1.0, 0.5, 0.2]
                for idx, preset_val in enumerate(distance_presets):
                    with preset_cols_dist[idx]:
                        st.button(
                            f"±{preset_val}",
                            key=f"dist_preset_{preset_val}",
                            help=f"设置所有直接距离误差为 ±{preset_val}m",
                            on_click=set_distance_preset,
                            args=(preset_val,),
                            use_container_width=True,
                        )
                
                # Angle error presets - second row
                st.caption("角度误差 (deg)")
                preset_cols_angle = st.columns(6)
                angle_presets = [4.0, 3.0, 2.0, 1.5, 1.0, 0.5]
                for idx, preset_val in enumerate(angle_presets):
                    with preset_cols_angle[idx]:
                        st.button(
                            f"±{preset_val}",
                            key=f"angle_preset_{preset_val}",
                            help=f"设置所有角度误差为 ±{preset_val}°",
                            on_click=set_angle_preset,
                            args=(preset_val,),
                            use_container_width=True,
                        )
                
                st.divider()
                
                st.markdown("**直接距离误差 (m)**")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.number_input("下限", step=0.1, format="%.1f", key="dist_lower")
                with col_d2:
                    st.number_input("上限", step=0.1, format="%.1f", key="dist_upper")
                dist_lower = st.session_state.dist_lower
                dist_upper = st.session_state.dist_upper
                
                st.markdown("**侧向误差 (m)**")
                col_l1, col_l2 = st.columns(2)
                with col_l1:
                    st.number_input("下限", step=0.1, format="%.1f", key="lat_lower")
                with col_l2:
                    st.number_input("上限", step=0.1, format="%.1f", key="lat_upper")
                lat_lower = st.session_state.lat_lower
                lat_upper = st.session_state.lat_upper
                
                st.markdown("**纵向误差 (m)**")
                col_ln1, col_ln2 = st.columns(2)
                with col_ln1:
                    st.number_input("下限", step=0.1, format="%.1f", key="lon_lower")
                with col_ln2:
                    st.number_input("上限", step=0.1, format="%.1f", key="lon_upper")
                lon_lower = st.session_state.lon_lower
                lon_upper = st.session_state.lon_upper
                
                st.markdown("**高度误差 (m)**")
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.number_input("下限", step=0.1, format="%.1f", key="height_lower")
                with col_h2:
                    st.number_input("上限", step=0.1, format="%.1f", key="height_upper")
                height_lower = st.session_state.height_lower
                height_upper = st.session_state.height_upper
                
                st.markdown("**偏航光轴偏差角 (deg)**")
                col_yaw1, col_yaw2 = st.columns(2)
                with col_yaw1:
                    st.number_input("下限", step=0.1, format="%.1f", key="dyaw_lower")
                with col_yaw2:
                    st.number_input("上限", step=0.1, format="%.1f", key="dyaw_upper")
                dyaw_lower = st.session_state.dyaw_lower
                dyaw_upper = st.session_state.dyaw_upper
                
                st.markdown("**俯仰光轴偏差角 (deg)**")
                col_pitch1, col_pitch2 = st.columns(2)
                with col_pitch1:
                    st.number_input("下限", step=0.1, format="%.1f", key="dpitch_lower")
                with col_pitch2:
                    st.number_input("上限", step=0.1, format="%.1f", key="dpitch_upper")
                dpitch_lower = st.session_state.dpitch_lower
                dpitch_upper = st.session_state.dpitch_upper


            # 原始完整数据（不做修改）
            original_df = process_frames(frames)
            # 用于绘图和统计的可过滤副本
            filtered_df = original_df.copy()

            # Apply filtering if enabled (only affects plots/stats)
            if filter_low_conf:
                initial_len = len(filtered_df)
                # Filter out low confidence or zero distance points
                # Ensure we don't crash if columns are missing, though processor guarantees them
                if 'algo_confidence' in filtered_df.columns:
                    mask = (filtered_df['algo_confidence'] > 0.85) & (filtered_df['algo_distance'] > 0.1)
                    filtered_df = filtered_df[mask]
                filtered_len = len(filtered_df)
                if initial_len > filtered_len:
                    st.sidebar.info(f"已过滤 {initial_len - filtered_len} 个异常点（仅用于图表与统计显示）")
                elif filtered_len == 0:
                    st.sidebar.warning("过滤后用于图表的数据为空！")
            
            # 概要统计部分已删除（应用户要求）
            exec_stats = statistics.get('execution', {})
            algo_perf = statistics.get('algorithm_performance', {})
            err_stats = statistics.get('error_statistics', {})
            conv_metrics = statistics.get('convergence_metrics', {})
            
            # 距离区间误差阈值统计 - 暂时隐藏
            # st.header("📋 RMS达标统计")
            # st.markdown("统计不同距离区间下，误差满足1σ值的样本比例")
            
            # # 计算统计指标
            # stats_data = []
            
            # # 1. 距离>1500m
            # df_1500 = filtered_df[filtered_df['gt_distance'] > 1500].copy()
            # if len(df_1500) > 0:
            #     mask_1500 = (df_1500['dyaw_error'].abs() <= 2) & (df_1500['dpitch_error'].abs() <= 2)
            #     sigma_1500 = (mask_1500.sum() / len(df_1500)) * 100
            #     stats_data.append({
            #         '距离区间': '> 1500m',
            #         '样本数': len(df_1500),
            #         '偏航角阈值(°)': '≤2',
            #         '俯仰角阈值(°)': '≤2',
            #         '位置误差阈值(m)': '-',
            #         '达标率(%)': f'{sigma_1500:.2f}'
            #     })
            # else:
            #     stats_data.append({
            #         '距离区间': '> 1500m',
            #         '样本数': 0,
            #         '偏航角阈值(°)': '≤2',
            #         '俯仰角阈值(°)': '≤2',
            #         '位置误差阈值(m)': '-',
            #         '达标率(%)': 'N/A'
            #     })
            
            # # 2. 距离>200m
            # df_200 = filtered_df[filtered_df['gt_distance'] > 200].copy()
            # if len(df_200) > 0:
            #     mask_200 = (
            #         (df_200['dyaw_error'].abs() <= 1.5) & 
            #         (df_200['dpitch_error'].abs() <= 1.5) &
            #         (df_200['distance_error'].abs() <= 1.6) &
            #         (df_200['lateral_error'].abs() <= 1.6) &
            #         (df_200['longitudinal_error'].abs() <= 1.6) &
            #         (df_200['height_error'].abs() <= 1.6)
            #     )
            #     sigma_200 = (mask_200.sum() / len(df_200)) * 100
            #     stats_data.append({
            #         '距离区间': '> 200m',
            #         '样本数': len(df_200),
            #         '偏航角阈值(°)': '≤1.5',
            #         '俯仰角阈值(°)': '≤1.5',
            #         '位置误差阈值(m)': '≤1.6',
            #         '达标率(%)': f'{sigma_200:.2f}'
            #     })
            # else:
            #     stats_data.append({
            #         '距离区间': '> 200m',
            #         '样本数': 0,
            #         '偏航角阈值(°)': '≤1.5',
            #         '俯仰角阈值(°)': '≤1.5',
            #         '位置误差阈值(m)': '≤1.6',
            #         '达标率(%)': 'N/A'
            #     })
            
            # # 3. 距离>10m
            # df_10 = filtered_df[filtered_df['gt_distance'] > 10].copy()
            # if len(df_10) > 0:
            #     mask_10 = (
            #         (df_10['dyaw_error'].abs() <= 1) & 
            #         (df_10['dpitch_error'].abs() <= 1) &
            #         (df_10['distance_error'].abs() <= 0.5) &
            #         (df_10['lateral_error'].abs() <= 0.5) &
            #         (df_10['longitudinal_error'].abs() <= 0.5) &
            #         (df_10['height_error'].abs() <= 0.5)
            #     )
            #     sigma_10 = (mask_10.sum() / len(df_10)) * 100
            #     stats_data.append({
            #         '距离区间': '> 10m',
            #         '样本数': len(df_10),
            #         '偏航角阈值(°)': '≤1',
            #         '俯仰角阈值(°)': '≤1',
            #         '位置误差阈值(m)': '≤0.5',
            #         '达标率(%)': f'{sigma_10:.2f}'
            #     })
            # else:
            #     stats_data.append({
            #         '距离区间': '> 10m',
            #         '样本数': 0,
            #         '偏航角阈值(°)': '≤1',
            #         '俯仰角阈值(°)': '≤1',
            #         '位置误差阈值(m)': '≤0.5',
            #         '达标率(%)': 'N/A'
            #     })
            
            # # 显示统计表格
            # stats_df = pd.DataFrame(stats_data)
            # st.dataframe(stats_df, width='stretch', hide_index=True)
            
            # st.markdown("""
            # **说明**：
            # - **达标率(%)**: 在该距离区间内，同时满足所有误差阈值条件的样本占比
            # - **位置误差**: 包括距离、侧向、纵向、高度四个维度的误差
            # - 只有当样本同时满足角度误差和位置误差的所有条件时，才计入达标样本
            # """)
            
            # 详细统计信息已应用户要求删除
            
            # Tabs for analysis
            tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["综合分析", "距离分析(d)", "侧向分析(x)", "纵向分析(y)", "高度分析(z)", "偏航光轴偏差角(dy)", "俯仰光轴偏差角(dp)", "原始数据"])
            
            with tab0:
                st.subheader("综合分析")
                
                # ========== 位置综合分析 ==========
                st.markdown("### 📍 位置误差综合分析")
                
                # 配置5个位置误差曲线 - 使用高对比度颜色
                position_error_configs = [
                    {'col': 'distance_error', 'name': '直接距离误差', 'color': '#E63946'},      # 鲜红色
                    {'col': 'position_error_3d', 'name': '分量合成误差', 'color': '#06A77D'},   # 青绿色
                    {'col': 'lateral_error', 'name': '侧向误差', 'color': '#1D3557'},           # 深蓝色
                    {'col': 'longitudinal_error', 'name': '纵向误差', 'color': '#F77F00'},      # 橙色
                    {'col': 'height_error', 'name': '高度误差', 'color': '#9D4EDD'},            # 紫色
                ]
                
                # 绘制位置误差综合对比图
                fig_pos = plot_multiple_errors(
                    filtered_df, 
                    'timestamp', 
                    position_error_configs,
                    '位置误差综合对比', 
                    '误差 (m)',
                    bounds=(dist_lower, dist_upper),
                    plot_mode=plot_mode,
                    show_fitting=show_fitting,
                    fitting_method=fitting_method,
                    fitting_window=fitting_window,
                    poly_degree=poly_degree
                )
                st.plotly_chart(fig_pos, use_container_width=True, config={'scrollZoom': False})
                
                # 位置误差统计表格
                st.markdown("#### 📊 位置误差统计汇总")
                dist_errors = filtered_df['distance_error'].dropna() if 'distance_error' in filtered_df.columns else pd.Series([0])
                pos_3d_errors = filtered_df['position_error_3d'].dropna() if 'position_error_3d' in filtered_df.columns else pd.Series([0])
                lat_errors = filtered_df['lateral_error'].dropna() if 'lateral_error' in filtered_df.columns else pd.Series([0])
                lon_errors = filtered_df['longitudinal_error'].dropna() if 'longitudinal_error' in filtered_df.columns else pd.Series([0])
                height_errors = filtered_df['height_error'].dropna() if 'height_error' in filtered_df.columns else pd.Series([0])
                
                error_stats_data = {
                    '误差类型': ['直接距离误差', '分量合成误差', '侧向误差', '纵向误差', '高度误差'],
                    '最大值 (m)': [
                        f"{dist_errors.max():.4f}" if len(dist_errors) > 0 else "N/A",
                        f"{pos_3d_errors.max():.4f}" if len(pos_3d_errors) > 0 else "N/A",
                        f"{lat_errors.max():.4f}" if len(lat_errors) > 0 else "N/A",
                        f"{lon_errors.max():.4f}" if len(lon_errors) > 0 else "N/A",
                        f"{height_errors.max():.4f}" if len(height_errors) > 0 else "N/A",
                    ],
                    '最小值 (m)': [
                        f"{dist_errors.min():.4f}" if len(dist_errors) > 0 else "N/A",
                        f"{pos_3d_errors.min():.4f}" if len(pos_3d_errors) > 0 else "N/A",
                        f"{lat_errors.min():.4f}" if len(lat_errors) > 0 else "N/A",
                        f"{lon_errors.min():.4f}" if len(lon_errors) > 0 else "N/A",
                        f"{height_errors.min():.4f}" if len(height_errors) > 0 else "N/A",
                    ],
                    '均值 (m)': [
                        f"{dist_errors.mean():.4f}" if len(dist_errors) > 0 else "N/A",
                        f"{pos_3d_errors.mean():.4f}" if len(pos_3d_errors) > 0 else "N/A",
                        f"{lat_errors.mean():.4f}" if len(lat_errors) > 0 else "N/A",
                        f"{lon_errors.mean():.4f}" if len(lon_errors) > 0 else "N/A",
                        f"{height_errors.mean():.4f}" if len(height_errors) > 0 else "N/A",
                    ],
                    'RMS (m)': [
                        f"{np.sqrt((dist_errors**2).mean()):.4f}" if len(dist_errors) > 0 else "N/A",
                        f"{np.sqrt((pos_3d_errors**2).mean()):.4f}" if len(pos_3d_errors) > 0 else "N/A",
                        f"{np.sqrt((lat_errors**2).mean()):.4f}" if len(lat_errors) > 0 else "N/A",
                        f"{np.sqrt((lon_errors**2).mean()):.4f}" if len(lon_errors) > 0 else "N/A",
                        f"{np.sqrt((height_errors**2).mean()):.4f}" if len(height_errors) > 0 else "N/A",
                    ],
                }
                error_stats_df = pd.DataFrame(error_stats_data)
                st.dataframe(error_stats_df, use_container_width=True, hide_index=True)
                
                st.divider()
                
                # ========== 角度综合分析 ==========
                st.markdown("### 📐 角度误差综合分析")
                
                # 配置2个角度误差曲线 - 使用高对比度颜色
                angle_error_configs = [
                    {'col': 'dyaw_error', 'name': '偏航光轴偏差角误差', 'color': '#D62828'},      # 深红色
                    {'col': 'dpitch_error', 'name': '俯仰光轴偏差角误差', 'color': '#0077B6'},    # 深蓝色
                ]
                
                # 绘制角度误差综合对比图
                fig_angle = plot_multiple_errors(
                    filtered_df, 
                    'timestamp', 
                    angle_error_configs,
                    '角度误差综合对比', 
                    '误差 (deg)',
                    bounds=(dyaw_lower, dyaw_upper),
                    plot_mode=plot_mode,
                    show_fitting=show_fitting,
                    fitting_method=fitting_method,
                    fitting_window=fitting_window,
                    poly_degree=poly_degree
                )
                st.plotly_chart(fig_angle, use_container_width=True, config={'scrollZoom': False})
                
                # 角度误差统计表格
                st.markdown("#### 📊 角度误差统计汇总")
                dyaw_errors = filtered_df['dyaw_error'].dropna() if 'dyaw_error' in filtered_df.columns else pd.Series([0])
                dpitch_errors = filtered_df['dpitch_error'].dropna() if 'dpitch_error' in filtered_df.columns else pd.Series([0])
                
                angle_error_stats_data = {
                    '误差类型': ['偏航光轴偏差角误差', '俯仰光轴偏差角误差'],
                    '最大值 (deg)': [
                        f"{dyaw_errors.max():.4f}" if len(dyaw_errors) > 0 else "N/A",
                        f"{dpitch_errors.max():.4f}" if len(dpitch_errors) > 0 else "N/A",
                    ],
                    '最小值 (deg)': [
                        f"{dyaw_errors.min():.4f}" if len(dyaw_errors) > 0 else "N/A",
                        f"{dpitch_errors.min():.4f}" if len(dpitch_errors) > 0 else "N/A",
                    ],
                    '均值 (deg)': [
                        f"{dyaw_errors.mean():.4f}" if len(dyaw_errors) > 0 else "N/A",
                        f"{dpitch_errors.mean():.4f}" if len(dpitch_errors) > 0 else "N/A",
                    ],
                    'RMS (deg)': [
                        f"{np.sqrt((dyaw_errors**2).mean()):.4f}" if len(dyaw_errors) > 0 else "N/A",
                        f"{np.sqrt((dpitch_errors**2).mean()):.4f}" if len(dpitch_errors) > 0 else "N/A",
                    ],
                }
                angle_error_stats_df = pd.DataFrame(angle_error_stats_data)
                st.dataframe(angle_error_stats_df, use_container_width=True, hide_index=True)
            
            with tab1:
                st.subheader("距离分析")
                fig1 = plot_comparison(filtered_df, 'timestamp', 'gt_distance', 'algo_distance', 
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)', 
                                     '理论值与实际值距离对比', '距离 (m)', plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig1, use_container_width=True, config={'scrollZoom': False})
                
                # 合并距离误差和分量合成误差到一个图表
                distance_error_configs = [
                    {'col': 'distance_error', 'name': '直接距离误差', 'color': '#E63946'},
                ]
                if 'position_error_3d' in filtered_df.columns:
                    distance_error_configs.append({'col': 'position_error_3d', 'name': '分量合成误差', 'color': '#06A77D'})
                
                fig_dist_combined = plot_multiple_errors(
                    filtered_df, 
                    'timestamp', 
                    distance_error_configs,
                    '距离误差（实际值 - 理论值）', 
                    '误差 (m)',
                    bounds=(dist_lower, dist_upper),
                    plot_mode=plot_mode,
                    show_fitting=show_fitting,
                    fitting_method=fitting_method,
                    fitting_window=fitting_window,
                    poly_degree=poly_degree
                )
                st.plotly_chart(fig_dist_combined, use_container_width=True, config={'scrollZoom': False})
                
                # 统计指标显示
                st.markdown("#### 📊 误差统计指标")
                dist_errors = filtered_df['distance_error'].dropna()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("最大误差", f"{dist_errors.max():.4f} m")
                with stat_col2:
                    st.metric("最小误差", f"{dist_errors.min():.4f} m")
                with stat_col3:
                    rms = np.sqrt((dist_errors**2).mean())
                    st.metric("RMS (均方根误差)", f"{rms:.4f} m")
                
                # 添加 3D 位置误差统计
                if 'position_error_3d' in filtered_df.columns:
                    st.markdown("#### 📊 3D位置误差统计")
                    pos_3d_errors = filtered_df['position_error_3d'].dropna()
                    if len(pos_3d_errors) > 0:
                        stat_col1, stat_col2, stat_col3 = st.columns(3)
                        with stat_col1:
                            st.metric("最大3D误差", f"{pos_3d_errors.max():.4f} m")
                        with stat_col2:
                            st.metric("最小3D误差", f"{pos_3d_errors.min():.4f} m")
                        with stat_col3:
                            rms_3d = np.sqrt((pos_3d_errors**2).mean())
                            st.metric("3D RMS", f"{rms_3d:.4f} m")
                
            with tab2:
                st.subheader("侧向位置分析")
                fig3 = plot_comparison(filtered_df, 'timestamp', 'gt_lateral', 'algo_lateral',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值侧向对比', '侧向距离 (m)', plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig3, use_container_width=True, config={'scrollZoom': False})
                
                fig4 = plot_error(filtered_df, 'timestamp', 'lateral_error',
                                '侧向误差（实际值 - 理论值）', '误差 (m)', bounds=(lat_lower, lat_upper), plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig4, use_container_width=True, config={'scrollZoom': False})
                
                # 统计指标显示
                st.markdown("#### 📊 误差统计指标")
                lat_errors = filtered_df['lateral_error'].dropna()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("最大误差", f"{lat_errors.max():.4f} m")
                with stat_col2:
                    st.metric("最小误差", f"{lat_errors.min():.4f} m")
                with stat_col3:
                    rms = np.sqrt((lat_errors**2).mean())
                    st.metric("RMS (均方根误差)", f"{rms:.4f} m")
                
            with tab3:
                st.subheader("纵向位置分析")
                fig5 = plot_comparison(filtered_df, 'timestamp', 'gt_longitudinal', 'algo_longitudinal',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值纵向对比', '纵向距离 (m)', plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig5, use_container_width=True, config={'scrollZoom': False})
                
                fig6 = plot_error(filtered_df, 'timestamp', 'longitudinal_error',
                                '纵向误差（实际值 - 理论值）', '误差 (m)', bounds=(lon_lower, lon_upper), plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig6, use_container_width=True, config={'scrollZoom': False})
                
                # 统计指标显示
                st.markdown("#### 📊 误差统计指标")
                lon_errors = filtered_df['longitudinal_error'].dropna()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("最大误差", f"{lon_errors.max():.4f} m")
                with stat_col2:
                    st.metric("最小误差", f"{lon_errors.min():.4f} m")
                with stat_col3:
                    rms = np.sqrt((lon_errors**2).mean())
                    st.metric("RMS (均方根误差)", f"{rms:.4f} m")
                
            with tab4:
                st.subheader("高度分析")
                fig7 = plot_comparison(filtered_df, 'timestamp', 'gt_height', 'algo_height',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值高度对比', '高度 (m)', plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig7, use_container_width=True, config={'scrollZoom': False})
                
                fig8 = plot_error(filtered_df, 'timestamp', 'height_error',
                                '高度误差（实际值 - 理论值）', '误差 (m)', bounds=(height_lower, height_upper), plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig8, use_container_width=True, config={'scrollZoom': False})
                
                # 统计指标显示
                st.markdown("#### 📊 误差统计指标")
                height_errors = filtered_df['height_error'].dropna()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("最大误差", f"{height_errors.max():.4f} m")
                with stat_col2:
                    st.metric("最小误差", f"{height_errors.min():.4f} m")
                with stat_col3:
                    rms = np.sqrt((height_errors**2).mean())
                    st.metric("RMS (均方根误差)", f"{rms:.4f} m")
                
            with tab5:
                st.subheader("偏航光轴偏差角分析 (Dyaw)")
                st.markdown("**光轴偏差角**：算法输出的光轴偏差角与真实值对比，单位为度")
                
                # 显示真值与算法输出的对比
                fig9 = plot_comparison(filtered_df, 'timestamp', 'gt_dyaw', 'algo_dyaw',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值偏航光轴偏差角对比', '偏差角 (deg)', plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig9, use_container_width=True, config={'scrollZoom': False})
                
                # 显示误差图
                fig9_err = plot_error(filtered_df, 'timestamp', 'dyaw_error',
                                '偏航光轴偏差角误差（实际值 - 理论值）', '误差 (deg)', bounds=(dyaw_lower, dyaw_upper), plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig9_err, use_container_width=True, config={'scrollZoom': False})
                
                # 统计指标显示
                st.markdown("#### 📊 误差统计指标")
                dyaw_errors = filtered_df['dyaw_error'].dropna()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("最大误差", f"{dyaw_errors.max():.4f} deg")
                with stat_col2:
                    st.metric("最小误差", f"{dyaw_errors.min():.4f} deg")
                with stat_col3:
                    rms = np.sqrt((dyaw_errors**2).mean())
                    st.metric("RMS (均方根误差)", f"{rms:.4f} deg")
                
            with tab6:
                st.subheader("俯仰光轴偏差角分析 (Dpitch)")
                st.markdown("**光轴偏差角**：算法输出的光轴偏差角与真实值对比，单位为度")
                
                # 显示真值与算法输出的对比
                fig10 = plot_comparison(filtered_df, 'timestamp', 'gt_dpitch', 'algo_dpitch',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值俯仰光轴偏差角对比', '偏差角 (deg)', plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig10, use_container_width=True, config={'scrollZoom': False})
                
                # 显示误差图
                fig10_err = plot_error(filtered_df, 'timestamp', 'dpitch_error',
                                 '俯仰光轴偏差角误差（实际值 - 理论值）', '误差 (deg)', bounds=(dpitch_lower, dpitch_upper), plot_mode=plot_mode, show_fitting=show_fitting, fitting_method=fitting_method, fitting_window=fitting_window, poly_degree=poly_degree)
                st.plotly_chart(fig10_err, use_container_width=True, config={'scrollZoom': False})

                # 统计指标显示
                st.markdown("#### 📊 误差统计指标")
                dpitch_errors = filtered_df['dpitch_error'].dropna()
                stat_col1, stat_col2, stat_col3 = st.columns(3)
                with stat_col1:
                    st.metric("最大误差", f"{dpitch_errors.max():.4f} deg")
                with stat_col2:
                    st.metric("最小误差", f"{dpitch_errors.min():.4f} deg")
                with stat_col3:
                    rms = np.sqrt((dpitch_errors**2).mean())
                    st.metric("RMS (均方根误差)", f"{rms:.4f} deg")

            with tab7:
                st.subheader("📋 原始数据表格")
                st.markdown("""
                **颜色说明**：
                - 🟡 **黄色背景**：该行存在超出误差阈值的数据
                - 🔴 **红色背景**：该行置信度过低 (< 0.5)
                """)
                
                # 允许用户上传 CSV 并将数据横向拼接（扩充列数，不扩充行数）
                uploaded_csv = st.file_uploader("上传 CSV 文件并横向拼接", type=['csv'], key='upload_csv')
                # 基于 original_df 构建用于显示的合并表格（默认未改动）
                combined_original = original_df.copy()
                if uploaded_csv is not None:
                    try:
                        uploaded_df = pd.read_csv(uploaded_csv)
                        # 清理列名空白
                        uploaded_df.columns = uploaded_df.columns.str.strip()
                        original_df.columns = original_df.columns.str.strip()

                        # 首选的对齐键（优先级）：image_path, image_name, frame_id, timestamp
                        preferred_keys = ['image_path', 'image_name', 'frame_id', 'timestamp']
                        key = next((k for k in preferred_keys if k in uploaded_df.columns and k in original_df.columns), None)

                        if key is not None:
                            # 若找到公共键，按该键左连接（original_df 为左表），保留原始所有行，新增列来自 uploaded_df
                            # 对上传列与原始重复的列添加后缀 '_csv' 以避免覆盖
                            overlap = set(uploaded_df.columns) & set(original_df.columns)
                            rename_map = {col: f"{col}_csv" for col in overlap if col != key}
                            uploaded_renamed = uploaded_df.rename(columns=rename_map)

                            # 转换数值列
                            for col in uploaded_renamed.columns:
                                if col in original_df.columns and pd.api.types.is_numeric_dtype(original_df[col]):
                                    uploaded_renamed[col] = pd.to_numeric(uploaded_renamed[col], errors='coerce')

                            combined_original = original_df.merge(uploaded_renamed, on=key, how='left')
                            added_cols = [c for c in combined_original.columns if c not in original_df.columns]
                            st.success(f"已完成拼接")

                        else:
                            # 若未找到公共键，但行数一致则按索引横向拼接
                            if len(uploaded_df) == len(original_df):
                                # 重命名重复列
                                overlap = set(uploaded_df.columns) & set(original_df.columns)
                                rename_map = {col: f"{col}_csv" for col in overlap}
                                uploaded_renamed = uploaded_df.rename(columns=rename_map)

                                # 转换数值列
                                for col in uploaded_renamed.columns:
                                    if col in original_df.columns and pd.api.types.is_numeric_dtype(original_df[col]):
                                        uploaded_renamed[col] = pd.to_numeric(uploaded_renamed[col], errors='coerce')

                                # 按索引合并（左表为 original_df）
                                uploaded_renamed = uploaded_renamed.reset_index(drop=True)
                                combined_original = pd.concat([original_df.reset_index(drop=True), uploaded_renamed], axis=1)
                                added_cols = [c for c in uploaded_renamed.columns if c not in original_df.columns]
                                st.success(f"行数匹配，已按索引横向拼接；新增列: {len(added_cols)} 个（示例: {added_cols[:5]})。")
                            else:
                                st.warning("无法自动横向对齐：未找到公共键（image_path/frame_id/timestamp 等）且上传 CSV 行数与原始数据不匹配。请提供带有匹配键的 CSV 或确保行数一致。")
                    except Exception as e:
                        st.error(f"处理上传的 CSV 时出错: {e}")

                # 准备显示用的数据框（未做过滤）
                display_df = combined_original.copy()
                
                # 选择要显示的列并重命名：已知列优先，其次显示上传 CSV 带来的新增列
                display_columns = {
                    'frame_id': '帧号',
                    'timestamp': '时间(s)',
                    'gt_distance': '真值距离(m)',
                    'algo_distance': '算法距离(m)',
                    'distance_error': '直接距离误差(m)',
                    'position_error_3d': '分量合成误差(m)',
                    'gt_lateral': '真值侧向(m)',
                    'algo_lateral': '算法侧向(m)',
                    'lateral_error': '侧向误差(m)',
                    'gt_longitudinal': '真值纵向(m)',
                    'algo_longitudinal': '算法纵向(m)',
                    'longitudinal_error': '纵向误差(m)',
                    'gt_height': '真值高度(m)',
                    'algo_height': '算法高度(m)',
                    'height_error': '高度误差(m)',
                    # 偏差角列顺序：真值 → 算法 → 误差
                    'gt_dyaw': '真值偏航偏差(°)',
                    'algo_dyaw': '算法偏航偏差(°)',
                    'dyaw_error': '偏航误差(°)',
                    'gt_dpitch': '真值俯仰偏差(°)',
                    'algo_dpitch': '算法俯仰偏差(°)',
                    'dpitch_error': '俯仰误差(°)',
                    'algo_confidence': '置信度',
                    'image_path': 'image_path',
                    'image_name': '图片名称'
                }

                # 将上传的新增列放在最左侧，已知列次之，其他列最后
                added_cols = [col for col in display_df.columns if col not in original_df.columns]
                # 已知列（在 display_columns 中）按预定义顺序保留
                known_cols = [col for col in display_columns.keys() if col in display_df.columns]
                # 其余列：去掉已置左的新增列和已知列
                other_cols = [col for col in display_df.columns if col not in known_cols and col not in added_cols]
                ordered_cols = added_cols + known_cols + other_cols

                # 隐藏不希望在“原始数据”表格中展示的列
                # - gt_yaw/gt_pitch: 姿态角（rad），一般不需要在原始表格里展示
                # - timestamp: 按需求隐藏时间列
                # - image_name: 按需求隐藏图片名称（保留图片路径）
                hidden_cols = {'gt_yaw', 'gt_pitch', 'timestamp', 'image_name'}
                ordered_cols = [c for c in ordered_cols if c not in hidden_cols]

                # 去重且保持顺序（以防意外重复）
                seen = set()
                ordered_cols = [x for x in ordered_cols if not (x in seen or seen.add(x))]

                # 将图片路径始终放在最前（后续会插入一个“无列名”的序号列作为第一列）
                if 'image_path' in ordered_cols:
                    ordered_cols = ['image_path'] + [c for c in ordered_cols if c != 'image_path']

                display_df = display_df[ordered_cols].copy()
                # 仅重命名我们识别的已知列
                display_df.rename(columns={k: v for k, v in display_columns.items() if k in known_cols}, inplace=True)

                # 使用 DataFrame 索引作为序号列（Streamlit 左侧索引列），并命名为 No
                display_df.index = range(1, len(display_df) + 1)
                display_df.index.name = 'No'
                
                # 定义样式函数
                def highlight_row(row):
                    # 获取原始列名对应的显示列名
                    conf_col = '置信度'
                    dist_err_col = '直接距离误差(m)'
                    lat_err_col = '侧向误差(m)'
                    lon_err_col = '纵向误差(m)'
                    height_err_col = '高度误差(m)'
                    dyaw_err_col = '偏航误差(°)'
                    dpitch_err_col = '俯仰误差(°)'
                    
                    styles = [''] * len(row)
                    
                    # 检查置信度 (红色优先级最高)
                    if conf_col in row.index and row[conf_col] < 0.5:
                        return ['background-color: #ffcccc'] * len(row)  # 红色
                    
                    # 检查误差是否超限 (黄色)
                    out_of_bound = False
                    if dist_err_col in row.index and (row[dist_err_col] < dist_lower or row[dist_err_col] > dist_upper):
                        out_of_bound = True
                    if lat_err_col in row.index and (row[lat_err_col] < lat_lower or row[lat_err_col] > lat_upper):
                        out_of_bound = True
                    if lon_err_col in row.index and (row[lon_err_col] < lon_lower or row[lon_err_col] > lon_upper):
                        out_of_bound = True
                    if height_err_col in row.index and (row[height_err_col] < height_lower or row[height_err_col] > height_upper):
                        out_of_bound = True
                    if dyaw_err_col in row.index and (row[dyaw_err_col] < dyaw_lower or row[dyaw_err_col] > dyaw_upper):
                        out_of_bound = True
                    if dpitch_err_col in row.index and (row[dpitch_err_col] < dpitch_lower or row[dpitch_err_col] > dpitch_upper):
                        out_of_bound = True
                    
                    if out_of_bound:
                        return ['background-color: #ffffcc'] * len(row)  # 黄色
                    
                    return styles
                
                # 应用样式
                styled_df = display_df.style.apply(highlight_row, axis=1)
                
                # 格式化数值
                format_dict = {col: '{:.4f}' for col in display_df.columns if display_df[col].dtype in ['float64', 'float32']}
                styled_df = styled_df.format(format_dict)
                
                # 显示表格
                st.dataframe(styled_df, use_container_width=True, height=600)
                
                # 字段说明
                st.markdown("---")
                st.subheader("📖 字段说明")
                
                with st.expander("**基本信息**", expanded=False):
                    st.markdown("""
                    - **No**: 当前行行号
                    - **image_path**: 对应图片的路径（相对于数据集根目录），用于关联数据与对应的图像文件
                    """)
                
                with st.expander("**距离测量**", expanded=False):
                    st.markdown("""
                    - **真值距离 (m)**: 无人机与目标之间实际距离的真实值，单位为米
                    - **算法距离 (m)**: 通过算法计算得到的无人机与目标之间的距离，单位为米
                    - **直接距离误差 (m)**: "算法距离" 与 "真值距离" 的差值，用于评估算法的距离计算精度
                    """)
                
                with st.expander("**侧向位置测量**", expanded=False):
                    st.markdown("""
                    - **真值侧向 (m)**: 无人机与目标在侧向（通常对应 NED 坐标系 Y 轴）相对位置的真实值，单位为米
                    - **算法侧向 (m)**: 通过算法计算得到的无人机与目标在侧向的相对位置，单位为米
                    - **侧向误差 (m)**: "算法侧向" 与 "真值侧向" 的差值，用于评估算法的侧向位置计算精度
                    """)
                
                with st.expander("**纵向位置测量**", expanded=False):
                    st.markdown("""
                    - **真值纵向 (m)**: 无人机与目标在纵向（通常对应 NED 坐标系 X 轴）相对位置的真实值，单位为米
                    - **算法纵向 (m)**: 通过算法计算得到的无人机与目标在纵向的相对位置，单位为米
                    - **纵向误差 (m)**: "算法纵向" 与 "真值纵向" 的差值，用于评估算法的纵向位置计算精度
                    """)
                
                with st.expander("**高度位置测量**", expanded=False):
                    st.markdown("""
                    - **真值高度 (m)**: 无人机与目标在高度方向（通常对应 NED 坐标系 Z 轴）相对位置的真实值，单位为米
                    - **算法高度 (m)**: 通过算法计算得到的无人机与目标在高度方向的相对位置，单位为米
                    - **高度误差 (m)**: "算法高度" 与 "真值高度" 的差值，用于评估算法的高度计算精度
                    """)
                
                with st.expander("**偏航光轴偏差角测量**", expanded=False):
                    st.markdown("""
                    - **真值偏航光轴偏差角(°)**: 目标偏航角的真实变化量
                    - **算法偏航光轴偏差角(°)**: 算法计算得到的目标偏航角变化量
                    - **偏航误差 (°)**: 算法计算的偏航角与真实偏航角的差值，单位为度，用于评估姿态计算精度
                    """)
                
                with st.expander("**俯仰光轴偏差角测量**", expanded=False):
                    st.markdown("""
                    - **真值俯仰光轴偏差角(°)**: 目标俯仰角的真实变化量
                    - **算法俯仰光轴偏差角(°)**: 算法计算得到的目标俯仰角变化量
                    - **俯仰误差 (°)**: 算法计算的俯仰角与真实俯仰角的差值，单位为度，用于评估姿态计算精度
                    """)
                
                with st.expander("**算法输出质量**", expanded=False):
                    st.markdown("""
                    - **置信度**: 算法输出结果的可靠程度（通常为 0-1），置信度越高代表结果越可靠
                    """)

        except Exception as e:
            st.error(f"处理文件时出错: {e}")

if __name__ == "__main__":
    main()
