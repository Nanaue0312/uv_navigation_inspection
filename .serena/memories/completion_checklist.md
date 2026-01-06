# 任务完成前检查清单

- 能运行：`streamlit run app.py`（或 `uv run streamlit run app.py`）
- UI 关键路径：上传 JSON -> 生成图表/表格无异常
- 数据字段：`src/processor.py` 中提取字段与实际 JSON 一致（必要时兼容旧字段名）
- 统计/过滤：过滤开关不影响原始数据表展示
- 测试：`pytest tests/`（若存在测试）
- 打包（如涉及）：`build_windows.ps1` 或按 `docs/README_PACKAGING.md` 手动打包验证启动
