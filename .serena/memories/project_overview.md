# uv_navigation_inspection 项目概览

## 项目目的
基于 Streamlit 的交互式算法性能评估工具：上传 `analysis_data.json`（闭环仿真/实测评估数据），对比 Ground Truth 与 Algorithm Output，并可视化距离/位置/光轴偏差角等误差，展示统计指标。

## 技术栈
- Python >= 3.12
- Streamlit：Web UI
- Pandas / NumPy：数据处理
- Plotly：交互式图表
- Matplotlib/Seaborn：依赖中存在（当前 UI 主要用 Plotly）
- PyInstaller：Windows 单文件打包
- uv：依赖/构建工具（可选）

## 代码结构（关键文件）
- `app.py`：Streamlit 主界面（上传文件、过滤、误差阈值、tab 展示、原始表格）
- `run_app.py`：打包/可执行入口（调用 `streamlit run app.py` 并固定端口）
- `src/data_loader.py`：读取 JSON（支持拼接/非标准 JSON 的容错）
- `src/processor.py`：把 frames 转为 DataFrame（提取 gt/algo/误差/置信度/图片路径）
- `src/visualizer.py`：Plotly 绘图
- `docs/ANALYSIS_DATA_FORMAT.md`：数据格式规范
- `docs/README_PACKAGING.md`：打包说明

## 数据格式要点
顶层：`metadata`, `frames`, `statistics`。
每帧包含：`timestamp`, `ground_truth`, `algorithm_output`, `errors`，并可能有 `image_path`。
