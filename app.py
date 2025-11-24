import streamlit as st
import numpy as np
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
                
                # Error bound configuration with input fields
                st.subheader("误差上限/下限配置")
                
                st.markdown("**距离误差 (m)**")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    dist_lower = st.number_input("下限", value=-2.0, step=0.1, key="dist_lower")
                with col_d2:
                    dist_upper = st.number_input("上限", value=2.0, step=0.1, key="dist_upper")
                
                st.markdown("**侧向误差 (m)**")
                col_l1, col_l2 = st.columns(2)
                with col_l1:
                    lat_lower = st.number_input("下限", value=-0.5, step=0.1, key="lat_lower")
                with col_l2:
                    lat_upper = st.number_input("上限", value=0.5, step=0.1, key="lat_upper")
                
                st.markdown("**纵向误差 (m)**")
                col_ln1, col_ln2 = st.columns(2)
                with col_ln1:
                    lon_lower = st.number_input("下限", value=-0.5, step=0.1, key="lon_lower")
                with col_ln2:
                    lon_upper = st.number_input("上限", value=0.5, step=0.1, key="lon_upper")
                
                st.markdown("**高度误差 (m)**")
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    height_lower = st.number_input("下限", value=-1.0, step=0.1, key="height_lower")
                with col_h2:
                    height_upper = st.number_input("上限", value=1.0, step=0.1, key="height_upper")
                
                st.markdown("**航向误差 (deg)**")
                col_hd1, col_hd2 = st.columns(2)
                with col_hd1:
                    heading_lower = st.number_input("下限", value=-0.5, step=0.1, key="heading_lower")
                with col_hd2:
                    heading_upper = st.number_input("上限", value=0.5, step=0.1, key="heading_upper")

            df = process_frames(frames)
            
            # Summary Metrics using statistics from JSON
            st.header("📈 概要统计")
            
            exec_stats = statistics.get('execution', {})
            algo_perf = statistics.get('algorithm_performance', {})
            err_stats = statistics.get('error_statistics', {})
            conv_metrics = statistics.get('convergence_metrics', {})
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总帧数", exec_stats.get('total_frames', len(df)))
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
                st.subheader("算法性能")
                st.text(f"平均置信度: {algo_perf.get('average_confidence', 0):.3f}")
                st.text(f"平均处理时间: {algo_perf.get('average_processing_time_ms', 0):.2f} ms")
                st.text(f"最大处理时间: {algo_perf.get('max_processing_time_ms', 0):.2f} ms")
                
                st.subheader("收敛指标")
                st.text(f"初始距离误差: {conv_metrics.get('initial_distance_error', 0):.2f} m")
                st.text(f"最终距离误差: {conv_metrics.get('final_distance_error', 0):.2f} m")
                st.text(f"收敛时间: {conv_metrics.get('convergence_time_s', 0):.2f} s")
                st.text(f"稳态误差: {conv_metrics.get('steady_state_error', 0):.2f} m")
            
            # Tabs for analysis
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["距离分析", "侧向分析", "纵向分析", "高度分析", "航向分析"])
            
            with tab1:
                st.subheader("距离分析")
                fig1 = plot_comparison(df, 'timestamp', 'gt_distance', 'algo_distance', 
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)', 
                                     '理论值与实际值距离对比', '距离 (m)')
                st.plotly_chart(fig1, use_container_width=True, config={'scrollZoom': False})
                
                fig2 = plot_error(df, 'timestamp', 'distance_error', 
                                '距离误差（实际值 - 理论值）', '误差 (m)', bounds=(dist_lower, dist_upper))
                st.plotly_chart(fig2, use_container_width=True, config={'scrollZoom': False})
                
            with tab2:
                st.subheader("侧向位置分析")
                fig3 = plot_comparison(df, 'timestamp', 'gt_lateral', 'algo_lateral',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值侧向对比', '侧向距离 (m)')
                st.plotly_chart(fig3, use_container_width=True, config={'scrollZoom': False})
                
                fig4 = plot_error(df, 'timestamp', 'lateral_error',
                                '侧向误差（实际值 - 理论值）', '误差 (m)', bounds=(lat_lower, lat_upper))
                st.plotly_chart(fig4, use_container_width=True, config={'scrollZoom': False})
                
            with tab3:
                st.subheader("纵向位置分析")
                fig5 = plot_comparison(df, 'timestamp', 'gt_longitudinal', 'algo_longitudinal',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值纵向对比', '纵向距离 (m)')
                st.plotly_chart(fig5, use_container_width=True, config={'scrollZoom': False})
                
                fig6 = plot_error(df, 'timestamp', 'longitudinal_error',
                                '纵向误差（实际值 - 理论值）', '误差 (m)', bounds=(lon_lower, lon_upper))
                st.plotly_chart(fig6, use_container_width=True, config={'scrollZoom': False})
                
            with tab4:
                st.subheader("高度分析")
                fig7 = plot_comparison(df, 'timestamp', 'gt_height', 'algo_height',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值高度对比', '高度 (m)')
                st.plotly_chart(fig7, use_container_width=True, config={'scrollZoom': False})
                
                fig8 = plot_error(df, 'timestamp', 'height_error',
                                '高度误差（实际值 - 理论值）', '误差 (m)', bounds=(height_lower, height_upper))
                st.plotly_chart(fig8, use_container_width=True, config={'scrollZoom': False})
                
            with tab5:
                st.subheader("航向分析")
                fig9 = plot_comparison(df, 'timestamp', 'gt_heading', 'algo_heading',
                                     '理论值 (Ground Truth)', '实际值 (Algorithm)',
                                     '理论值与实际值航向对比', '航向 (rad)')
                st.plotly_chart(fig9, use_container_width=True, config={'scrollZoom': False})
                
                fig10 = plot_error(df, 'timestamp', 'heading_error',
                                 '航向误差（实际值 - 理论值）', '误差 (deg)', bounds=(heading_lower, heading_upper))
                st.plotly_chart(fig10, use_container_width=True, config={'scrollZoom': False})

        except Exception as e:
            st.error(f"处理文件时出错: {e}")

if __name__ == "__main__":
    main()
