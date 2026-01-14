# 拟合算法优化说明

## 问题分析

### 原问题
在使用多项式拟合分析误差数据时，发现拟合结果几乎是一条水平线（接近0），无法反映误差的实际波动规律。

### 根本原因
**多项式拟合不适合高频波动、无明显全局趋势的误差数据**：
- 多项式拟合追求全局最优，对所有数据点进行加权平均
- 误差数据通常围绕0上下波动，无明显趋势
- 结果被平均成接近0的直线，丧失了拟合的意义

## 解决方案

### 针对性优化策略

根据数据特征，采用**不同的拟合算法组合**：

#### 1. 误差图（Error Plots）
**数据特征**：高频波动、无全局趋势、关注局部特征

**拟合方案**：
- ✅ **滑动平均（Moving Average）** - 简单快速
- ✅ **Savitzky-Golay 滤波** - 保留峰值和局部特征
- ❌ ~~多项式拟合~~ - 移除（会变成无意义的直线）

#### 2. 对比图（Comparison Plots）
**数据特征**：通常有上升/下降趋势

**拟合方案**：
- ✅ **滑动平均** - 局部平滑
- ✅ **多项式拟合** - 全局趋势（保留）

## 新增拟合方法详解

### Savitzky-Golay 滤波器

**原理**：
- 在移动窗口内拟合多项式
- 用拟合值替代中心点
- 滑动窗口遍历整个数据集

**优势**：
```
✓ 在平滑数据的同时保留峰值特征
✓ 适合有局部极值的误差数据
✓ 比简单移动平均更好地保持信号形状
✓ 特别适合分析周期性波动
✓ 数学性质好，可以计算导数
```

**参数说明**：
- **window_length**（窗口大小）：必须是奇数
  - 窗口越小：更贴近原始数据，保留更多细节
  - 窗口越大：更平滑，去除更多噪声
  - 推荐：10-15

- **polyorder**（多项式次数）：必须小于窗口大小
  - 次数越低：更平滑，但可能过度简化
  - 次数越高：更灵活，但可能过拟合
  - 推荐：2-3

**对比效果**：

| 方法 | 平滑度 | 保留峰值 | 保留形状 | 计算速度 |
|------|--------|----------|----------|----------|
| 滑动平均 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| SavGol滤波 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 多项式拟合 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ |

## 实现细节

### 代码结构

```python
def _apply_fitting(df, x_col, y_col, method, window, degree):
    """统一的拟合接口"""
    if method == 'moving_average':
        # 滑动平均
        return df[y_col].rolling(window, center=True).mean()
    
    elif method == 'savgol':
        # Savitzky-Golay 滤波
        from scipy.signal import savgol_filter
        window_size = window if window % 2 == 1 else window + 1
        return savgol_filter(df[y_col], window_size, degree)
    
    elif method == 'polynomial':
        # 多项式拟合（仅用于对比图）
        coeffs = np.polyfit(x, y, degree)
        return np.poly1d(coeffs)(x)
```

### 自动降级机制

为确保鲁棒性，实现了智能降级：

```python
# 数据点不足时，自动降级到滑动平均
if valid_data_points < window_size:
    return moving_average_fallback()

# SavGol 失败时，自动降级到滑动平均
try:
    return savgol_filter(...)
except:
    return moving_average_fallback()
```

## 使用方法

### 在应用中使用

1. **启用拟合**：在侧边栏勾选"显示曲线拟合"
2. **调节参数**：
   - 滑动平均窗口：3-50（默认10）
   - SavGol多项式次数：1-10（默认3）
3. **查看效果**：在图例中点击拟合曲线名称可显示/隐藏

### 在代码中调用

```python
from src.visualizer import plot_error

# 误差图自动使用 滑动平均 + SavGol
fig = plot_error(
    df, 'timestamp', 'distance_error',
    '误差分析', '误差 (m)',
    plot_mode='markers',
    show_fitting=True,
    fitting_window=10,  # 滑动窗口
    poly_degree=3       # SavGol多项式次数
)
```

## 效果对比

### 之前（多项式拟合）
```
问题：
- 拟合曲线几乎是水平线
- 无法反映误差波动规律
- 拟合失去意义
```

### 之后（SavGol滤波）
```
改进：
✓ 拟合曲线跟随数据波动
✓ 保留峰值和谷值特征
✓ 平滑噪声的同时保持信号形状
✓ 更好地揭示误差变化规律
```

## 适用场景建议

### 滑动平均
- ✅ 快速预览数据趋势
- ✅ 计算资源有限
- ✅ 不需要保留精确峰值

### Savitzky-Golay 滤波
- ✅ 需要保留峰值特征
- ✅ 分析周期性波动
- ✅ 准备后续计算（如求导）
- ✅ 科学报告和论文展示

### 多项式拟合
- ✅ 数据有明显全局趋势
- ✅ 需要外推预测
- ✅ 数学建模
- ❌ 不适合高频波动数据
- ❌ 不适合无趋势的误差数据

## 技术参考

### Savitzky-Golay 算法
- **论文**：Savitzky, A., & Golay, M. J. (1964). "Smoothing and Differentiation of Data by Simplified Least Squares Procedures"
- **实现**：scipy.signal.savgol_filter
- **复杂度**：O(n × w)，其中 n 是数据点数，w 是窗口大小

### 参数选择指南
```python
# 保守平滑（适合噪声数据）
window = 15, polyorder = 2

# 推荐配置（通用）
window = 10, polyorder = 3

# 激进保留（适合信噪比高的数据）
window = 7, polyorder = 3
```

## 总结

通过引入 Savitzky-Golay 滤波并针对不同数据类型优化拟合策略，显著提升了误差数据的分析能力：

✅ **解决了多项式拟合失效的问题**
✅ **更好地揭示误差波动规律**  
✅ **保留了数据的重要特征**
✅ **提供了更专业的分析工具**

这个优化方案特别适合分析控制系统的误差数据，能够更准确地反映系统的动态特性和性能表现。
