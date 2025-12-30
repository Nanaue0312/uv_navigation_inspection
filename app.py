import streamlit as st
import numpy as np
import pandas as pd
from src.data_loader import load_data
from src.processor import process_frames
from src.visualizer import plot_comparison, plot_error

st.set_page_config(page_title="算法性能评估工具", layout="wide")

def main():
    st.title("📊 仿真应用理论输出评估控制算法性能")
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
                st.header("📋 仿真信息")
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
                
                # Plot mode selection
                st.subheader("📊 图表显示模式")
                plot_mode = st.radio(
                    "选择显示方式",
                    options=['lines', 'markers', 'lines+markers'],
                    format_func=lambda x: {'lines': '📈 折线图', 
                                          'markers': '⚫ 散点图', 
                                          'lines+markers': '📊 折线+散点'}[x],
                    index=2,
                    key='plot_mode'
                )
                
                st.subheader("🛡️ 数据过滤")
                filter_low_conf = st.toggle("过滤低置信度/异常数据", value=True, help="开启后将隐藏置信度<0.5或算法输出为0的异常点")
                
                # Error bound configuration with input fields
                st.subheader("误差上限/下限配置")
                
                st.markdown("**距离误差 (m)**")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    dist_lower = st.number_input("下限", value=-1.6, step=0.1, key="dist_lower")
                with col_d2:
                    dist_upper = st.number_input("上限", value=1.6, step=0.1, key="dist_upper")
                
                st.markdown("**侧向误差 (m)**")
                col_l1, col_l2 = st.columns(2)
                with col_l1:
                    lat_lower = st.number_input("下限", value=-1.6, step=0.1, key="lat_lower")
                with col_l2:
                    lat_upper = st.number_input("上限", value=1.6, step=0.1, key="lat_upper")
                
                st.markdown("**纵向误差 (m)**")
                col_ln1, col_ln2 = st.columns(2)
                with col_ln1:
                    lon_lower = st.number_input("下限", value=-1.6, step=0.1, key="lon_lower")
                with col_ln2:
                    lon_upper = st.number_input("上限", value=1.6, step=0.1, key="lon_upper")
                
                st.markdown("**高度误差 (m)**")
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    height_lower = st.number_input("下限", value=-1.6, step=0.1, key="height_lower")
                with col_h2:
                    height_upper = st.number_input("上限", value=1.6, step=0.1, key="height_upper")
                
                st.markdown("**偏航光轴偏差角 (deg)**")
                col_yaw1, col_yaw2 = st.columns(2)
                with col_yaw1:
                    dyaw_lower = st.number_input("下限", value=-1.5, step=0.1, key="dyaw_lower")
                with col_yaw2:
                    dyaw_upper = st.number_input("上限", value=1.5, step=0.1, key="dyaw_upper")
                
                st.markdown("**俯仰光轴偏差角 (deg)**")
                col_pitch1, col_pitch2 = st.columns(2)
                with col_pitch1:
                    dpitch_lower = st.number_input("下限", value=-1.5, step=0.1, key="dpitch_lower")
                with col_pitch2:
                    dpitch_upper = st.number_input("上限", value=1.5, step=0.1, key="dpitch_upper")


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
                    mask = (filtered_df['algo_confidence'] > 0.5) & (filtered_df['algo_distance'] > 0.1)
                    filtered_df = filtered_df[mask]
                filtered_len = len(filtered_df)
                if initial_len > filtered_len:
                    st.sidebar.info(f"已过滤 {initial_len - filtered_len} 个异常点（仅用于图表与统计显示）")
                elif filtered_len == 0:
                    st.sidebar.warning("过滤后用于图表的数据为空！")
            
            # Summary Metrics using statistics from JSON
            st.header("📈 概要统计")
            
            exec_stats = statistics.get('execution', {})
            algo_perf = statistics.get('algorithm_performance', {})
            err_stats = statistics.get('error_statistics', {})
            conv_metrics = statistics.get('convergence_metrics', {})
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总帧数", exec_stats.get('total_frames', len(filtered_df)))
            col2.metric("成功率", f"{exec_stats.get('success_rate', 0)*100:.1f}%")
            
            # Use pre-calculated RMSE from statistics
            dist_rmse = err_stats.get('distance', {}).get('rmse', 0)
            col3.metric("距离RMSE", f"{dist_rmse:.3f} m")
            
            lat_rmse = err_stats.get('lateral', {}).get('rmse', 0)
            lon_rmse = err_stats.get('longitudinal', {}).get('rmse', 0)
            h_rmse = err_stats.get('height', {}).get('rmse', 0)
            pos_rmse_3d = np.sqrt(lat_rmse**2 + lon_rmse**2 + h_rmse**2)
            col4.metric("位置RMSE(3D)", f"{pos_rmse_3d:.3f} m")
            
            # Display additional statistics
            with st.expander("📊 详细统计信息"):
                st.markdown("##### 📌 计算方式说明")
                st.info("""
                **RMSE (均方根误差)**: 衡量误差大小的指标，公式为 √(Σ(误差²)/N)  
                **平均置信度**: 算法输出置信度的平均值 (0-1之间)  
                **收敛时间**: 误差收敛到稳态阈值所需的时间  
                """)
                
                st.subheader("算法性能")
                st.markdown("""
                - **平均置信度**: `{:.3f}` - 算法对其输出结果的平均信心程度，范围0-1，越接近1表示算法越确信其结果准确
                - **平均处理时间**: `{:.2f} ms` - 算法处理单帧数据所需的平均时间，反映算法的实时性能
                - **最大处理时间**: `{:.2f} ms` - 算法处理单帧数据的最长耗时，用于评估最坏情况下的性能
                """.format(
                    algo_perf.get('average_confidence', 0),
                    algo_perf.get('average_processing_time_ms', 0),
                    algo_perf.get('max_processing_time_ms', 0)
                ))
                
                st.subheader("收敛指标")
                st.markdown("""
                - **初始距离误差**: `{:.2f} m` - 仿真开始时算法输出与真实值之间的距离误差
                - **最终距离误差**: `{:.2f} m` - 仿真结束时算法输出与真实值之间的距离误差
                - **收敛时间**: `{:.2f} s` - 算法从初始状态收敛到稳定状态所需的时间
                - **稳态误差**: `{:.2f} m` - 算法收敛后在稳定状态下的平均误差水平
                """.format(
                    conv_metrics.get('initial_distance_error', 0),
                    conv_metrics.get('final_distance_error', 0),
                    conv_metrics.get('convergence_time_s', 0),
                    conv_metrics.get('steady_state_error', 0)
                ))
            
            # Tabs for analysis
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["距离分析", "侧向分析", "纵向分析", "高度分析", "偏航光轴偏差角", "俯仰光轴偏差角", "原始数据"])
            
            with tab1:
                st.subheader("距离分析")
                fig1 = plot_comparison(filtered_df, 'timestamp', 'gt_distance', 'algo_distance', 
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)', 
                                     '理论值与实际值距离对比', '距离 (m)', plot_mode=plot_mode)
                st.plotly_chart(fig1, width='stretch', config={'scrollZoom': False})
                
                fig2 = plot_error(filtered_df, 'timestamp', 'distance_error', 
                                '距离误差（实际值 - 理论值）', '误差 (m)', bounds=(dist_lower, dist_upper), plot_mode=plot_mode)
                st.plotly_chart(fig2, width='stretch', config={'scrollZoom': False})
                
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
                
            with tab2:
                st.subheader("侧向位置分析")
                fig3 = plot_comparison(filtered_df, 'timestamp', 'gt_lateral', 'algo_lateral',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值侧向对比', '侧向距离 (m)', plot_mode=plot_mode)
                st.plotly_chart(fig3, width='stretch', config={'scrollZoom': False})
                
                fig4 = plot_error(filtered_df, 'timestamp', 'lateral_error',
                                '侧向误差（实际值 - 理论值）', '误差 (m)', bounds=(lat_lower, lat_upper), plot_mode=plot_mode)
                st.plotly_chart(fig4, width='stretch', config={'scrollZoom': False})
                
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
                                     '理论值与实际值纵向对比', '纵向距离 (m)', plot_mode=plot_mode)
                st.plotly_chart(fig5, width='stretch', config={'scrollZoom': False})
                
                fig6 = plot_error(filtered_df, 'timestamp', 'longitudinal_error',
                                '纵向误差（实际值 - 理论值）', '误差 (m)', bounds=(lon_lower, lon_upper), plot_mode=plot_mode)
                st.plotly_chart(fig6, width='stretch', config={'scrollZoom': False})
                
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
                                     '理论值与实际值高度对比', '高度 (m)', plot_mode=plot_mode)
                st.plotly_chart(fig7, width='stretch', config={'scrollZoom': False})
                
                fig8 = plot_error(filtered_df, 'timestamp', 'height_error',
                                '高度误差（实际值 - 理论值）', '误差 (m)', bounds=(height_lower, height_upper), plot_mode=plot_mode)
                st.plotly_chart(fig8, width='stretch', config={'scrollZoom': False})
                
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
                                     '理论值与实际值偏航光轴偏差角对比', '偏差角 (deg)', plot_mode=plot_mode)
                st.plotly_chart(fig9, width='stretch', config={'scrollZoom': False})
                
                # 显示误差图
                fig9_err = plot_error(filtered_df, 'timestamp', 'dyaw_error',
                                '偏航光轴偏差角误差（实际值 - 理论值）', '误差 (deg)', bounds=(dyaw_lower, dyaw_upper), plot_mode=plot_mode)
                st.plotly_chart(fig9_err, width='stretch', config={'scrollZoom': False})
                
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
                                     '理论值与实际值俯仰光轴偏差角对比', '偏差角 (deg)', plot_mode=plot_mode)
                st.plotly_chart(fig10, width='stretch', config={'scrollZoom': False})
                
                # 显示误差图
                fig10_err = plot_error(filtered_df, 'timestamp', 'dpitch_error',
                                 '俯仰光轴偏差角误差（实际值 - 理论值）', '误差 (deg)', bounds=(dpitch_lower, dpitch_upper), plot_mode=plot_mode)
                st.plotly_chart(fig10_err, width='stretch', config={'scrollZoom': False})

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
                    'distance_error': '距离误差(m)',
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
                    dist_err_col = '距离误差(m)'
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

        except Exception as e:
            st.error(f"处理文件时出错: {e}")

if __name__ == "__main__":
    main()
