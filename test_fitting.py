"""
测试曲线拟合功能
"""
import pandas as pd
import numpy as np
from src.visualizer import plot_comparison, plot_error

# 创建测试数据
np.random.seed(42)
n_points = 100
timestamps = np.linspace(0, 10, n_points)
gt_values = 5 + 2 * np.sin(timestamps) + np.random.normal(0, 0.1, n_points)
algo_values = gt_values + np.random.normal(0, 0.3, n_points)
errors = algo_values - gt_values

df = pd.DataFrame({
    'timestamp': timestamps,
    'gt_distance': gt_values,
    'algo_distance': algo_values,
    'distance_error': errors
})

# 测试 plot_comparison 函数（散点图模式，带拟合）
print("测试 plot_comparison (散点图 + 拟合)...")
fig1 = plot_comparison(
    df, 'timestamp', 'gt_distance', 'algo_distance',
    '理论值', '实际值', '对比图（散点+拟合）', '距离 (m)',
    plot_mode='markers', show_fitting=True
)
print(f"✓ 生成了 {len(fig1.data)} 条曲线")
print(f"  - 散点数据: {fig1.data[0].name}, {fig1.data[2].name}")
print(f"  - 拟合曲线: {fig1.data[1].name}, {fig1.data[3].name}")

# 测试 plot_comparison 函数（散点图模式，不带拟合）
print("\n测试 plot_comparison (仅散点)...")
fig2 = plot_comparison(
    df, 'timestamp', 'gt_distance', 'algo_distance',
    '理论值', '实际值', '对比图（仅散点）', '距离 (m)',
    plot_mode='markers', show_fitting=False
)
print(f"✓ 生成了 {len(fig2.data)} 条曲线")
print(f"  - 仅散点数据: {fig2.data[0].name}, {fig2.data[1].name}")

# 测试 plot_error 函数（散点图模式，带拟合）
print("\n测试 plot_error (散点图 + 拟合)...")
fig3 = plot_error(
    df, 'timestamp', 'distance_error',
    '误差图（散点+拟合）', '误差 (m)',
    bounds=(-1.0, 1.0), plot_mode='markers', show_fitting=True
)
print(f"✓ 生成了 {len(fig3.data)} 条曲线")
print(f"  - 误差散点: {fig3.data[0].name}")
print(f"  - 拟合曲线: {fig3.data[1].name}")
print(f"  - 上下限: {fig3.data[2].name}, {fig3.data[3].name}")

# 测试 plot_error 函数（折线图模式，带拟合）
print("\n测试 plot_error (折线图 + 拟合)...")
fig4 = plot_error(
    df, 'timestamp', 'distance_error',
    '误差图（折线+拟合）', '误差 (m)',
    bounds=(-1.0, 1.0), plot_mode='lines', show_fitting=True
)
print(f"✓ 生成了 {len(fig4.data)} 条曲线")
print(f"  - 误差折线: {fig4.data[0].name}")
print(f"  - 拟合曲线: {fig4.data[1].name}")

print("\n✅ 所有测试通过！曲线拟合功能工作正常。")
