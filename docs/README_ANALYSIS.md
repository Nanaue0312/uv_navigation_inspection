# 紫外导航算法性能分析工具

## 📋 项目简介

这是一个用于分析紫外导航算法性能的自动化工具，通过比对算法输出与仿真真实值，生成详细的误差分析报告。

**主要功能：**
- ✅ 自动加载 `analysis_data.json` 格式的仿真数据
- ✅ 计算距离、纵向、侧向、高度、航向角等多维度误差
- ✅ 统计指标精度符合率（基于 `0.5+0.2%×D` 和固定阈值标准）
- ✅ 生成时间/距离维度的误差曲线图（带阈值线和平滑拟合）
- ✅ 输出文本、HTML、JSON 三种格式的分析报告

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用 pip 安装
pip install pandas numpy matplotlib scipy

# 或者使用项目的 pyproject.toml
pip install -e .
```

### 2. 运行分析

**基本用法：**
```bash
# 分析单个数据目录
python3 analyze.py data/closed_loop_20251122_154229

# 分析指定的 JSON 文件
python3 analyze.py data/closed_loop_20251122_154229/analysis_data.json
```

**高级选项：**
```bash
# 指定输出目录
python3 analyze.py data/closed_loop_20251122_154229 -o reports/my_report

# 仅生成文本报告（不生成图表，速度更快）
python3 analyze.py data/closed_loop_20251122_154229 --no-plots

# 指定报告格式
python3 analyze.py data/closed_loop_20251122_154229 --format html
python3 analyze.py data/closed_loop_20251122_154229 --format json
python3 analyze.py data/closed_loop_20251122_154229 --format text
```

**查看帮助：**
```bash
python3 analyze.py --help
```

### 3. 查看结果

分析完成后，在 `reports/` 目录（或指定的输出目录）中查看：

- **analysis_report.txt** - 文本格式报告（适合命令行查看）
- **analysis_report.html** - HTML网页报告（包含图表，浏览器打开）
- **analysis_report.json** - JSON数据报告（便于程序读取）
- **\*.png** - 12张误差分析图表

---

## 📊 分析维度

### 1. 距离误差分析
- **指标：** 紫外导航算法估计的斜距 vs 真实斜距
- **精度标准：** `(0.5 + 0.2% × D)` 米
- **输出：**
  - 不同距离范围（0-800m, 0-1500m, 全程）的符合率
  - 时间维度和距离维度的误差曲线
  - 平均误差、标准差、最大误差、RMSE

### 2. 纵向误差分析
- **指标：** y轴方向误差（前正后负）
- **精度标准：** `(0.5 + 0.2% × D)` 米
- **输出：** 同上

### 3. 侧向误差分析
- **指标：** x轴方向误差（左负右正）
- **精度标准：** `(0.5 + 0.2% × D)` 米
- **输出：** 同上

### 4. 高度误差分析
- **指标：** z轴方向误差（高度，向上为正）
- **精度标准：** `(0.5 + 0.2% × D)` 米
- **输出：** 同上

### 5. 航向角误差分析
- **指标：** 航向角（heading/yaw）误差
- **精度标准：** `±1°`
- **输出：**
  - 不同距离范围的符合率
  - 误差曲线图

---

## 📁 项目结构

```
uv_navigaion_inspetion/
├── analyze.py              # 主程序入口（命令行工具）
├── app.py                  # Streamlit Web界面（原有）
├── src/                    # 核心模块
│   ├── __init__.py
│   ├── data_loader.py      # 数据加载模块
│   ├── statistics_analyzer.py  # 统计分析模块
│   ├── visualizer.py       # 可视化模块
│   └── report_generator.py # 报告生成模块
├── data/                   # 数据目录
│   └── closed_loop_20251122_154229/
│       ├── analysis_data.json
│       ├── summary.json
│       └── metadata/
├── reports/                # 输出报告目录
│   ├── analysis_report.txt
│   ├── analysis_report.html
│   ├── analysis_report.json
│   └── *.png              # 图表
├── ANALYSIS_DATA_FORMAT.md  # 数据格式规范
└── README_ANALYSIS.md      # 本文档
```

---

## 📖 使用示例

### 示例 1：完整分析流程

```bash
# 1. 运行分析
python3 analyze.py data/closed_loop_20251122_154229

# 2. 查看文本报告
cat reports/analysis_report.txt

# 3. 在浏览器中打开 HTML 报告
open reports/analysis_report.html  # macOS
# 或 xdg-open reports/analysis_report.html  # Linux
# 或直接双击 analysis_report.html 文件
```

### 示例 2：批量分析多个数据包

```bash
# 创建批量分析脚本
for dir in data/*/; do
  echo "分析: $dir"
  python3 analyze.py "$dir" -o "reports/$(basename $dir)"
done
```

### 示例 3：仅生成统计数据（JSON）

```bash
# 快速生成JSON报告，不生成图表
python3 analyze.py data/closed_loop_20251122_154229 \
  --no-plots --format json -o reports/quick
```

---

## 📈 报告示例

### 文本报告片段

```
【指标精度符合率】

1. 紫外距离
   0-800m内，88.0%的点(132/150)满足(0.5+0.2%×D)的指标精度要求
      平均误差: 0.3521m, 最大误差: 1.2340m
   0-1500m内，69.0%的点(1035/1500)满足(0.5+0.2%×D)的指标精度要求
      平均误差: 0.8234m, 最大误差: 5.8000m

2. 紫外纵向
   0-800m内，86.9%的点满足(0.5+0.2%×D)的指标精度要求
   ...
```

### HTML报告特性
- 📊 完整的图表嵌入
- 🎨 美观的表格样式
- 🔢 自动颜色标记（绿色=优秀，黄色=一般，红色=待改进）
- 📱 响应式设计

---

## 🔧 高级配置

### 自定义距离范围

编辑 `src/statistics_analyzer.py` 中的 `generate_comprehensive_report()` 方法：

```python
# 修改标准距离范围
standard_ranges = [(0, 500), (0, 800), (0, 1500)]

# 添加跟踪过程范围
tracking_ranges = [(0, 50), (0, 100)]
```

### 自定义阈值函数

修改 `calculate_distance_accuracy()` 等方法中的 `threshold_func`：

```python
# 示例：更严格的阈值
def threshold_func(d):
    return 0.3 + 0.001 * d  # 0.3 + 0.1% × D
```

### 自定义图表样式

编辑 `src/visualizer.py` 中的绘图参数：

```python
# 修改图表尺寸
fig, ax = plt.subplots(figsize=(14, 8))  # 默认 (12, 6)

# 修改平滑窗口大小
def rolling_fit(series: pd.Series, window: int = 50):  # 默认 30
```

---

## 📝 数据格式要求

工具支持标准的 `analysis_data.json` 格式（详见 `ANALYSIS_DATA_FORMAT.md`）。

**必需字段：**
- `metadata`: 仿真元数据
- `frames`: 帧数据数组
  - 每帧包含：`timestamp`, `ground_truth`, `algorithm_output`, `errors`

**示例数据结构：**
```json
{
  "format_version": "1.0",
  "metadata": { ... },
  "frames": [
    {
      "frame_id": 0,
      "timestamp": 0.0,
      "ground_truth": {
        "relative_to_ship": {
          "distance": 1500.0,
          "x_lateral": 0.0,
          "y_longitudinal": 0.0,
          "z_height": 1500.0
        }
      },
      "algorithm_output": {
        "distance": 1502.3,
        "heading": 5.24
      },
      "errors": { ... }
    }
  ]
}
```

---

## ❓ 常见问题

### Q1: 报告中显示符合率为 0%？
**A:** 检查算法输出字段是否正确。如果 `algorithm_output.distance` 全为 0，说明算法未正常输出数据。

### Q2: 图表显示异常或曲线不平滑？
**A:** 
- 数据点太少（<10帧）时平滑效果差
- 可以调整 `visualizer.py` 中的 `smooth=False` 参数关闭平滑
- 或增加采样窗口大小

### Q3: 如何只分析特定距离范围？
**A:** 使用 `DataLoader.filter_by_distance_range()` 方法：
```python
loader = DataLoader("data/...")
loader.load()
df_filtered = loader.filter_by_distance_range(min_dist=0, max_dist=800)
```

### Q4: 能否导出原始误差数据到 Excel？
**A:** 可以在分析后手动导出：
```python
from src.data_loader import DataLoader
loader = DataLoader("data/...")
loader.load()
df = loader.get_frames_dataframe()
df.to_excel("errors.xlsx", index=False)
```

---

## 🔄 与原 Streamlit App 的关系

- **analyze.py（本工具）**: 命令行批量分析，适合自动化、CI/CD、批量处理
- **app.py（原有）**: Web界面交互式分析，适合单次手动分析、可视化探索

两者可以并行使用，数据格式兼容。

---

## 📞 技术支持

- **数据格式规范**: 见 `ANALYSIS_DATA_FORMAT.md`
- **问题反馈**: 提交 Issue 或联系开发团队
- **功能建议**: 欢迎提交 PR

---

## 📄 许可证

本项目遵循项目主仓库的许可证。

---

**最后更新**: 2025-11-22  
**版本**: v1.0.0
