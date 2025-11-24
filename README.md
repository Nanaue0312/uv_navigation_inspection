uv_navigation_inspection
=======================

这是一个用于分析和可视化紫外（UV）导航算法在仿真闭环数据上的性能评估工具：包含一个 Streamlit 的交互式界面与可复用的 Python 模块。主要用于对比算法输出与仿真真实值，生成误差统计与可视化。

主要功能
--------
- 基于 Streamlit 的可交互 Web 界面：上传 `analysis_data.json`，实时生成可视化图表与关键统计指标
- 将仿真每帧数据转换为 Pandas DataFrame，便于后续分析与导出
- 支持距离/侧向/纵向/高度/航向等维度的对比与误差展示，支持误差上/下限显示
- 简易的数据加载工具，支持常见 JSON 格式（官方规范见 docs/ANALYSIS_DATA_FORMAT.md）

快速开始
---------

先决条件：
- Python >= 3.12（项目在 pyproject.toml 中声明了依赖）

步骤（Windows PowerShell 示例）：

1) 创建并激活虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) 安装依赖

```powershell
pip install -U pip
pip install -e .
```

3) 运行 Streamlit 应用

```powershell
streamlit run app.py
```

在浏览器中打开显示的地址，上传 `analysis_data.json` 即可开始交互式分析。

项目结构
------------

```
uv_navigation_inspection/
├── app.py                      # Streamlit Web 界面入口
├── pyproject.toml              # 项目与依赖声明
├── data/                       # 示例/仿真数据
│   └── closed_loop_YYYYMMDD_HHMMSS/
│       └── analysis_data.json  # 仿真导出数据示例
├── docs/                       # 规范和分析说明（ANALYSIS_DATA_FORMAT.md）
├── src/
│   ├── data_loader.py          # JSON -> dict 的容错加载器
│   ├── processor.py            # 将帧转换为 DataFrame（提取常用列）
│   └── visualizer.py           # 基于 Plotly 的对比与误差图工具
└── README.md                   # 本文件
```

数据规范
---------

工程遵循 `docs/ANALYSIS_DATA_FORMAT.md` 中定义的 `analysis_data.json` 规范。关键字段包括：
- 顶层：`format_version`, `metadata`, `frames`, `statistics`
- 单帧：`timestamp`, `ground_truth`, `algorithm_output`, `errors`

程序化使用示例
-----------------
可以在脚本/REPL 中直接调用模块：

```python
from src.data_loader import load_data
from src.processor import process_frames
from src.visualizer import plot_comparison

content = open('data/closed_loop_20251122_154229/analysis_data.json').read()
data = load_data(content)
df = process_frames(data['frames'])

fig = plot_comparison(df, 'timestamp', 'gt_distance', 'algo_distance',
                      'Ground Truth', 'Algorithm', '距离对比', '距离 (m)')
fig.show()
```

更多使用方式可参见 `src/visualizer.py`、`src/processor.py` 注释与 `app.py` 的使用逻辑。

开发与贡献
-------------

欢迎贡献：提交 Issue、Pull Request 或在 PR 中指出改进方向。建议在贡献前：
- 更新与运行测试（如果加入测试套件）
- 说明变更和兼容性影响

可扩展点：
- 批量/命令行分析入口（例如 `analyze.py`）
- 增强报告导出（HTML / PDF / CSV）
- 自动化测试与 CI 集成

常见问题
-----------

- Q: 上传文件后没有显示数据？
  - A: 检查你的 JSON 中是否有 `frames` 字段且为非空数组
- Q: 数据格式和字段名字不完全匹配？
  - A: 优先遵循 `ANALYSIS_DATA_FORMAT.md`，如果还有兼容问题，可以在 `src/data_loader.py` 中添加解析逻辑

许可证
---------

本仓库当前未赋予具体的开源许可证：在发布为开源项目之前请补充 `LICENSE` 文件（例如 MIT / Apache-2.0）。

更多文档
----------

- `docs/ANALYSIS_DATA_FORMAT.md`: 数据格式规范（强烈推荐先阅读）
- `docs/README_ANALYSIS.md`: 工具说明与示例（文档级别的示例与设计）

维护者：项目团队
# 紫外导航算法误差对比应用 (初始版本)

## 目标
使用 Streamlit 快速搭建一个界面：上传“紫外导航算法输出数据”与“仿真数据”，对比生成误差统计与可视化（时间序列、分布）。当前为基础框架，后续再细化需求与扩展功能。

## 运行环境
- Python >= 3.10
- 使用 [uv](https://docs.astral.sh/uv/) 进行依赖与虚拟环境管理

## 快速开始
```bash
# 安装 uv (若未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同目录下执行依赖安装
eval "$(uv --activate)"  # 可选：若需要直接激活环境
uv sync

# 运行应用
uv run streamlit run app.py
```

## 后续可扩展点（待讨论）
- 姿态(roll,pitch,yaw)误差
- 动态滤波与估计结果对比
- 误差随环境参数分组分析
- 误差统计导出 (CSV / Excel / PDF)
- 高级图形(3D轨迹对比)

## 许可证
当前未设置公共开源协议，内部使用。
