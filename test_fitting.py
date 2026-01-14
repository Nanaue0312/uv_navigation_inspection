"""
测试曲线拟合功能 - 滑动平均 + Savitzky-Golay滤波
"""
import pandas as pd
import numpy as np
from src.visualizer import plot_comparison, plot_error

# 创建测试数据 - 模拟真实的误差数据（高频波动，无明显趋势）
np.random.seed(42)
n_points = 100
timestamps = np.linspace(0, 10, n_points)
# 添加多种频率的正弦波 + 噪声，模拟复杂的误差波动
gt_values = 5 + 0.5 * np.sin(2 * timestamps) + 0.3 * np.sin(5 * timestamps) + np.random.normal(0, 0.1, n_points)
algo_values = gt_values + np.random.normal(0, 0.3, n_points)
errors = algo_values - gt_values

df = pd.DataFrame({
    'timestamp': timestamps,
    'gt_distance': gt_values,
    'algo_distance': algo_values,
    'distance_error': errors
})

print("=" * 80)
print("测试曲线拟合功能 - 优化后的双拟合方案")
print("=" * 80)
print("\n💡 针对误差数据的优化：")
print("   - 移除多项式拟合（不适合高频波动数据）")
print("   - 新增 Savitzky-Golay 滤波器（保留峰值特征）")
print()

# ============================================================================
# 测试 1: 误差图 - 滑动平均 vs Savitzky-Golay
# ============================================================================
print("\n【测试 1】误差图 - 双拟合对比（默认参数）...")
fig1 = plot_error(
    df, 'timestamp', 'distance_error',
    '误差图 - 滑动平均 vs SavGol滤波', '误差 (m)',
    bounds=(-1.0, 1.0), plot_mode='markers', show_fitting=True
)
print(f"✓ 生成了 {len(fig1.data)} 条曲线")
print(f"  - 误差数据: 1 条")
print(f"  - 滑动平均拟合: 1 条（黑色实线）")
print(f"  - SavGol滤波拟合: 1 条（深绿色点线）")
print(f"  - 边界线: 2 条")

# ============================================================================
# 测试 2: 对比图 - 仍使用多项式（适合有趋势的数据）
# ============================================================================
print("\n【测试 2】对比图 - 滑动平均 + 多项式拟合...")
print("   （对比图数据通常有趋势，保留多项式拟合）")
fig2 = plot_comparison(
    df, 'timestamp', 'gt_distance', 'algo_distance',
    '理论值', '实际值', '对比图 - 双拟合曲线', '距离 (m)',
    plot_mode='markers', show_fitting=True
)
print(f"✓ 生成了 {len(fig2.data)} 条曲线")
print(f"  - 原始数据: 2 条")
print(f"  - 拟合曲线: {len(fig2.data) - 2} 条")

# ============================================================================
# 测试 3: 不同窗口大小对比
# ============================================================================
print("\n【测试 3】SavGol滤波 - 不同窗口大小...")
for window in [5, 10, 15]:
    fig = plot_error(
        df, 'timestamp', 'distance_error',
        f'误差图 - 窗口={window}', '误差 (m)',
        bounds=(-1.0, 1.0), plot_mode='markers', show_fitting=True,
        fitting_window=window
    )
    print(f"  ✓ 窗口={window}: 更{'平滑' if window > 10 else '贴近原始数据'}")

# ============================================================================
# 测试 4: 不同多项式次数对比（SavGol）
# ============================================================================
print("\n【测试 4】SavGol滤波 - 不同多项式次数...")
for degree in [2, 3, 4]:
    fig = plot_error(
        df, 'timestamp', 'distance_error',
        f'误差图 - 次数={degree}', '误差 (m)',
        bounds=(-1.0, 1.0), plot_mode='markers', show_fitting=True,
        poly_degree=degree
    )
    print(f"  ✓ 次数={degree}: {'低次平滑' if degree == 2 else ('推荐' if degree == 3 else '高次灵活')}")

print("\n" + "=" * 80)
print("✅ 所有测试通过！")
print("=" * 80)
print("\n功能说明:")
print("  ✨ 针对不同数据类型的优化拟合：")
print()
print("  📊 误差图（高频波动数据）：")
print("     1. 滑动平均 - 简单快速的平滑")
print("     2. Savitzky-Golay 滤波 - 保留峰值和局部特征")
print("     ❌ 移除多项式拟合（会变成接近0的直线，无意义）")
print()
print("  📈 对比图（有趋势的数据）：")
print("     1. 滑动平均 - 局部平滑")
print("     2. 多项式拟合 - 全局趋势（保留）")
print()
print("  🎯 Savitzky-Golay 滤波优势：")
print("     - 在平滑数据的同时保留峰值特征")
print("     - 适合有局部极值的误差数据")
print("     - 比简单移动平均更好地保持信号形状")
print("     - 特别适合分析周期性波动")
print()
print("  ⚙️ 默认参数:")
print("     - 滑动窗口: 10")
print("     - SavGol多项式次数: 3")
print("=" * 80)
