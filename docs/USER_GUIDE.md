# 用户指南：UV Navigation Inspection 应用使用说明

本用户指南面向最终用户（算法开发者、仿真分析人员与工程师），用于介绍 `UV Navigation Inspection` 工具的功能、界面、输入数据格式与使用示例，以及常见问题与排查建议。

---

## 1. 概述

`UV Navigation Inspection` 是一个基于 Streamlit 的交互式仿真分析工具，用于评估和可视化无人机（UV）/导航算法在闭环仿真环境中的性能。通过上传 `analysis_data.json`（仿真输出），本工具可以展示时序对比图、误差统计、收敛与稳态分析，帮助研发人员快速定位与调优算法问题。

适用场景：算法验证、参数调优、回归测试、仿真报告生成。

---

## 2. 主要功能（简要）

- 交互式：通过浏览器界面上传数据并查看即时可视化结果。
- 多维分析：距离、横向、纵向、高度与航向等维度对比与误差曲线。
- 统计汇总：均值、标准差、RMSE、最大值、分位数、成功率与收敛指标。
- 实时诊断：置信度、处理时间、图像质量与环境参数（船舶运动、相机设置）分析。
- 导出：可导出处理后的 DataFrame 用于后续分析。

---

## 3. 快速开始（运行与使用）

### 运行前准备

- Python >= 3.12
- 推荐使用虚拟环境或 `uv` 包管理器
- 安装依赖：`pip install -r requirements.txt`

### 启动应用

Windows PowerShell：
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Linux/macOS：
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

在浏览器中访问由 Streamlit 提示的地址（默认 `http://localhost:8501`）。

### 使用步骤

1. 在应用中点击“上传数据”并选择 `analysis_data.json`。
2. 等待数据解析并自动生成图表与统计概览。
3. 在侧边栏设置误差上下限（可选），用于突出显示异常区间。
4. 依次浏览：距离 / 侧向 / 纵向 / 高度 / 航向 分析页签。
5. 查看顶部摘要（总帧数、成功率、距离 RMSE、位置 RMSE(3D)）与折叠面板中的详细统计信息。

---

## 4. 界面元素说明

### 顶部摘要

- 总帧数（Total frames）：仿真或视频的总帧数量。字段：`metadata.simulation_config.total_frames`。
- 成功率（Success rate）：算法成功检测的帧占比。字段：`statistics.execution.success_rate`。
- 距离 RMSE（Distance RMSE）：均方根误差，衡量径向/斜距估计精度。字段：`statistics.error_statistics.distance.rmse`。
- 位置 RMSE(3D)：三维误差联合度量，采用各轴 RMSE 合并计算：`sqrt(rmse_x^2 + rmse_y^2 + rmse_z^2)`。

### 详细统计（折叠面板）

- 平均置信度（average_confidence）与置信度标准差（confidence_std）。字段：`statistics.algorithm_performance.*`。
- 处理时间（平均与最大）用于评估实时性能要求。字段：`statistics.algorithm_performance.average_processing_time_ms`、`max_processing_time_ms`。
- 收敛指标（初始/最终误差、收敛时间、稳态误差）。字段：`statistics.convergence_metrics.*`。
- 错误统计：每个维度（distance、lateral、longitudinal、height、heading）包含 mean、std、rmse、max、percentile_50、percentile_95 等。

### 图表（各标签页）

- 距离分析：理论值 vs 算法估计值对比图，误差时间序列，误差上下限标注。
- 侧向 / 纵向 / 高度 / 航向：与距离分析类似，分别针对对应维度展示对比曲线、误差曲线与统计信息。
- 交互操作：框选缩放、平移、双击重置、悬停显示详细数值。航向图自动进行角度环绕处理（unwrap），确保角度连续显示。

---

## 5. 数据格式（简要）

应用遵循 `docs/ANALYSIS_DATA_FORMAT.md` 的规范，关键字段包括：

- `metadata`：仿真配置与场景信息（帧率、总帧、传感器配置等）。
- `frames`：逐帧数据，含 `ground_truth`、`algorithm_output`、`errors` 与 `environment`。
- `statistics`：统计汇总（execution、algorithm_performance、error_statistics、convergence_metrics）。

如果你需要详细的字段说明或示例 JSON，请参阅 `docs/ANALYSIS_DATA_FORMAT.md`。

---

## 6. 常见问题与排查建议

### Q：为什么距离RMSE与位置RMSE差别较大？
- 距离 RMSE 是一个标量，表示斜距估计误差；位置 RMSE（3D）由各轴误差合并得来。若横向/纵向/高度误差较大但互相方向抵消（或相反方向），会导致距离误差小但位置误差大。建议同时查看 3 个分量的均值与 RMSE。

### Q：为什么置信度低但 RMSE 也小？
- 置信度（算法自评）并不总能反映真实误差。有时算法对异常情况不自信，但估计仍然接近真值。建议结合置信度分布、图像质量（mean_brightness、SNR）等因素评估。

### Q：收敛时间为 0 或稳态误差很大，是否出现了问题？
- 可能是收敛阈值设置不合理或收敛窗口选择错误。检查 `statistics.convergence_metrics` 的计算实现与阈值设定，或通过手动绘图检查误差随时间的变化以确认实际收敛行为。

### Q：高度误差过大是什么原因？
- 检查坐标系与符号（NED 的 Down vs relative_to_ship 的 z_height）。Down 为正意味着高度通常是 -down 的数值，两个字段如果混用会导致偏差大的错误。

---

## 7. 进阶分析建议

- 使用 `df = process_frames(frames)` 导出 DataFrame 后，进行 “长尾”分析（箱形图/直方图），并用 95% 或 99% 分位数评估异常值对 RMSE 的影响。
- 对航向角 적용 wrap-around 处理后再统计均值/STD，避免 360° 问题。
- 使用 `frames` 中的 `environment`（相机参数、图像质量）字段结合在 errors 与 confidence 上做回归分析，找出影响算法性能的环境因子。

---

## 8. 导出与报告

- 数据：可将 DataFrame 导出为 CSV/Parquet 以便在 Jupyter/Excel 中进一步分析。
- 报表：使用 Streamlit 的截图功能或将图表导出为图片后生成仿真性能报告。

---

## 9. 贡献与联系

欢迎为该仓库提出 Issue 或 Pull Request（添加新的图表、修复 bug、优化统计实现等）。

维护者联系信息见项目主页。

---

## 10. 附加资源

- [数据格式规范](./ANALYSIS_DATA_FORMAT.md)
- [分析工具说明](./README_ANALYSIS.md)
- [打包说明](./README_PACKAGING.md)

---

文档自动生成器: Assist by GitHub Copilot style doc helper.
