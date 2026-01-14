# 曲线拟合功能说明

## 概述

系统现在支持两种曲线拟合方法，用于在散点图模式下平滑显示数据趋势：
1. **滑动平均（Moving Average）** - 局部平滑方法
2. **最小二乘多项式拟合（Polynomial Fitting）** - 全局拟合方法

## 更新内容

### 1. 默认参数变更
- **旧默认值**：滑动平均窗口 = 30
- **新默认值**：滑动平均窗口 = 3

### 2. 新增功能
- 添加拟合方法选择器
- 添加滑动窗口大小可调节（3-50）
- 添加多项式次数可调节（1-10）
- 在应用侧边栏提供交互式配置

## 拟合方法详解

### 滑动平均（Moving Average）

**原理**：
- 计算每个点周围窗口内数据的平均值
- 使用居中窗口（center=True），平衡前后数据

**优点**：
- 简单快速
- 保留局部特征
- 对噪声有一定抑制作用

**缺点**：
- 窗口边界处理可能不够平滑
- 窗口大小需要根据数据特点调整

**参数配置**：
- `fitting_window`: 窗口大小（默认：3）
  - 窗口 = 3：快速响应，贴近原始数据，适合细节分析
  - 窗口 = 10：中等平滑，适合一般场景
  - 窗口 = 30：强平滑，适合长趋势观察

**适用场景**：
- 数据量大、计算性能要求高
- 需要保留局部特征
- 数据噪声较小

### 最小二乘多项式拟合（Polynomial Fitting）

**原理**：
- 使用最小二乘法（Least Squares）拟合多项式
- 通过 numpy.polyfit 实现全局最优拟合
- 自动处理 NaN 值

**优点**：
- 全局平滑，曲线连续光滑
- 数学性质好，可微分
- 适合展示整体趋势

**缺点**：
- 计算量较大
- 高次多项式可能过拟合
- 不适合突变数据

**参数配置**：
- `poly_degree`: 多项式次数（默认：3）
  - 次数 = 1：线性拟合，最简单的趋势线
  - 次数 = 2：二次曲线，适合抛物线趋势
  - 次数 = 3：三次曲线，推荐值，适合大多数场景
  - 次数 = 5+：高次曲线，灵活但可能过拟合

**适用场景**：
- 需要光滑的趋势曲线
- 数据具有明显的全局趋势
- 用于报告展示和趋势预测

## 使用方法

### 在 Streamlit 应用中

1. 上传数据文件后，在左侧边栏找到 **"图表显示模式"** 区域
2. 勾选 **"显示曲线拟合"**
3. 选择拟合方法：
   - **滑动平均**：调节滑动窗口大小（3-50）
   - **最小二乘多项式**：调节多项式次数（1-10）
4. 在图表中点击图例可以显示/隐藏拟合曲线

### 在代码中调用

```python
from src.visualizer import plot_comparison, plot_error

# 使用滑动平均（窗口=3）
fig = plot_comparison(
    df, 'timestamp', 'gt_distance', 'algo_distance',
    '理论值', '实际值', '对比图', '距离 (m)',
    plot_mode='markers',
    show_fitting=True,
    fitting_method='moving_average',
    fitting_window=3
)

# 使用多项式拟合（3次）
fig = plot_error(
    df, 'timestamp', 'distance_error',
    '误差图', '误差 (m)',
    plot_mode='markers',
    show_fitting=True,
    fitting_method='polynomial',
    poly_degree=3
)
```

### 多曲线对比图

```python
from src.visualizer_ext import plot_multiple_errors

error_configs = [
    {'col': 'distance_error', 'name': '距离误差', 'color': '#E63946'},
    {'col': 'lateral_error', 'name': '侧向误差', 'color': '#1D3557'},
]

fig = plot_multiple_errors(
    df, 'timestamp', error_configs,
    '综合误差分析', '误差 (m)',
    plot_mode='markers',
    show_fitting=True,
    fitting_method='polynomial',
    poly_degree=3
)
```

## 推荐配置

### 快速分析场景
- **方法**：滑动平均
- **窗口**：3
- **优势**：快速响应，细节保留

### 报告展示场景
- **方法**：多项式拟合
- **次数**：3
- **优势**：曲线光滑，美观专业

### 长期趋势场景
- **方法**：滑动平均 或 多项式拟合
- **窗口**：10-30（滑动平均）
- **次数**：2-3（多项式）
- **优势**：突出主要趋势

## 注意事项

1. **数据量不足**：当数据点少于多项式次数+1时，会自动降级到滑动平均
2. **NaN 处理**：多项式拟合会自动跳过 NaN 值
3. **性能考虑**：数据量超过10000点时，建议使用滑动平均
4. **过拟合风险**：多项式次数不建议超过5，除非有特殊需求

## 测试验证

运行测试脚本验证功能：

```bash
python test_fitting.py
```

测试包含：
- 滑动平均拟合（窗口 3, 10, 30）
- 多项式拟合（次数 1, 2, 3, 5）
- 对比图和误差图测试
- 综合性能验证

## 技术细节

### 滑动平均实现
```python
df[y_col].rolling(window=window, min_periods=1, center=True).mean()
```

### 多项式拟合实现
```python
x = np.arange(len(df))
y = df[y_col].values
valid_mask = ~np.isnan(y)
coeffs = np.polyfit(x[valid_mask], y[valid_mask], degree)
poly = np.poly1d(coeffs)
fitted = poly(x)
```

## 更新历史

- **2026-01-14**：
  - 新增最小二乘多项式拟合方法
  - 滑动平均窗口从 30 改为 3
  - 添加参数可配置功能
  - 在 Streamlit 应用中添加交互式配置界面
