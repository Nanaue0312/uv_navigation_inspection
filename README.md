# UV Navigation Inspection

一个用于分析和可视化 UV 导航算法性能的交互式评估工具。基于 Streamlit 构建，支持实时数据分析、误差可视化和性能统计。

## ✨ 主要功能

- 📊 **交互式 Web 界面** - 基于 Streamlit，上传 JSON 数据即可生成可视化图表
- 📈 **多维度分析** - 支持距离、侧向、纵向、高度、航向等多个维度的对比分析
- 🎯 **误差评估** - 实时计算误差统计，支持自定义误差上下限
- 📉 **Plotly 交互图表** - 支持缩放、平移、框选等交互操作
- 🔧 **角度环绕处理** - 自动处理航向角度的环绕问题，确保图表连续性
- 💾 **数据导出** - 支持将处理后的数据导出为 DataFrame
- 📦 **跨平台打包** - 支持 Windows (PyInstaller) 和 Unix (uv build) 打包

## 🚀 快速开始

### 前置要求

- Python >= 3.12
- uv 包管理器（推荐）或 pip

### 安装步骤

#### 方式一：使用 uv（推荐）

```bash
# 克隆仓库
git clone <repository-url>
cd uv_navigation_inspection

# 使用 uv 同步依赖
uv sync

# 运行应用
uv run streamlit run app.py
```

#### 方式二：使用传统 venv

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### 使用应用

1. 在浏览器中打开显示的地址（通常是 `http://localhost:8501`）
2. 上传 `analysis_data.json` 文件
3. 在侧边栏配置误差上下限
4. 查看各个分析标签页的图表和统计信息

## 📁 项目结构

```
uv_navigation_inspection/
├── app.py                      # Streamlit 主应用
├── run_app.py                  # 打包入口点
├── pyproject.toml              # 项目配置和依赖
├── requirements.txt            # Python 依赖列表
├── build_windows.ps1           # Windows 打包脚本
├── build_unix.sh               # Unix/Linux 打包脚本
├── src/
│   ├── data_loader.py          # JSON 数据加载器
│   ├── processor.py            # 数据处理和转换（含角度unwrap）
│   └── visualizer.py           # Plotly 图表生成
├── docs/
│   ├── ANALYSIS_DATA_FORMAT.md # 数据格式规范
│   ├── README_ANALYSIS.md      # 分析工具说明
│   └── README_PACKAGING.md     # 打包部署文档
├── data/                       # 示例数据目录
└── tests/                      # 测试文件
```

## 📊 数据格式

应用遵循 `docs/ANALYSIS_DATA_FORMAT.md` 中定义的 JSON 数据规范。

### 关键字段

```json
{
  "format_version": "1.0",
  "metadata": { ... },
  "frames": [
    {
      "timestamp": 0.0,
      "ground_truth": {
        "relative_to_ship": { "distance": ..., "x_lateral": ..., ... },
        "attitude": { "yaw": ..., "pitch": ..., "roll": ... }
      },
      "algorithm_output": {
        "distance": ..., "x_lateral": ..., "heading": ...
      },
      "errors": { ... }
    }
  ],
  "statistics": { ... }
}
```

详细规范请参阅 `docs/ANALYSIS_DATA_FORMAT.md`。

## 🎨 功能特性

### 1. 多维度对比分析

- **距离分析** - 理论值 vs 实际值距离对比
- **侧向分析** - 横向位置偏差分析
- **纵向分析** - 纵向位置偏差分析
- **高度分析** - 垂直位置偏差分析
- **航向分析** - 航向角对比（自动处理角度环绕）

### 2. 误差可视化

每个维度包含：
- 原始误差曲线
- 拟合曲线（30点移动平均）
- 可配置的上下限边界
- 实时误差统计

### 3. 交互式图表

- **框选缩放** - 拖拽选择区域进行缩放
- **拖拽平移** - 移动查看不同时间段
- **双击重置** - 恢复原始视图
- **悬停显示** - 查看精确数值
- **禁用滚轮** - 避免与页面滚动冲突

### 4. 角度环绕处理

航向数据自动应用 `numpy.unwrap`，解决 ±π 跳变问题，确保图表显示连续曲线。

## 📦 打包部署

### Windows 平台（PyInstaller）

```powershell
# 一键打包
.\build_windows.ps1

# 运行打包后的程序
.\dist\uv_navigation_inspection.exe
```

生成单文件可执行程序，无需 Python 环境即可运行。

### Unix/Linux/macOS 平台（uv build）

```bash
# 添加执行权限
chmod +x build_unix.sh

# 一键打包
./build_unix.sh

# 安装 wheel 包
pip install dist/uv_navigation_inspection-*.whl

# 运行
uv_navigation_inspection
```

详细打包说明请参阅 `docs/README_PACKAGING.md`。

## 🔧 开发

### 程序化使用

```python
from src.data_loader import load_data
from src.processor import process_frames
from src.visualizer import plot_comparison, plot_error

# 加载数据
with open('data/example/analysis_data.json') as f:
    data = load_data(f.read())

# 处理数据
df = process_frames(data['frames'])

# 生成图表
fig = plot_comparison(
    df, 'timestamp', 'gt_distance', 'algo_distance',
    '理论值', '实际值', '距离对比', '距离 (m)'
)
fig.show()
```

### 运行测试

```bash
# 使用 pytest
pytest tests/

# 或使用 uv
uv run pytest tests/
```

## 📚 文档

- **[数据格式规范](docs/ANALYSIS_DATA_FORMAT.md)** - JSON 数据结构详细说明
- **[分析工具说明](docs/README_ANALYSIS.md)** - 工具使用和分析方法
- **[打包部署文档](docs/README_PACKAGING.md)** - 详细的打包和分发指南
 - **[用户指南](docs/USER_GUIDE.md)** - 使用说明与界面功能介绍

## 🛠️ 技术栈

- **Streamlit** - Web 应用框架
- **Plotly** - 交互式图表库
- **Pandas** - 数据处理
- **NumPy** - 数值计算（角度unwrap）
- **PyInstaller** - Windows 打包
- **uv** - 现代 Python 包管理

## 📝 更新日志

### v1.0.0 (2025-11-24)

- ✨ 初始版本发布
- 📊 支持多维度性能分析
- 🎯 可配置误差边界
- 📈 Plotly 交互式图表
- 🔧 自动处理航向角度环绕
- 📦 跨平台打包支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

建议贡献前：
1. 查看现有 Issues
2. 遵循代码风格
3. 添加必要的测试
4. 更新相关文档

## 📄 许可证

本项目当前未指定开源许可证。如需商业使用或二次开发，请联系项目维护者。

## 🔗 相关链接

- [Streamlit 文档](https://docs.streamlit.io/)
- [Plotly Python 文档](https://plotly.com/python/)
- [uv 包管理器](https://github.com/astral-sh/uv)

## 💬 支持

如有问题或建议：
1. 查看 `docs/` 目录下的文档
2. 提交 GitHub Issue
3. 联系项目维护者

---

**最后更新**: 2025-11-24
