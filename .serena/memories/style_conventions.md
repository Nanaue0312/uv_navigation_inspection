# 代码风格与约定

- 语言：Python
- 命名：snake_case（函数/变量），模块同名
- 类型标注：在 `src/` 里有轻量 type hints（如 `List[Dict[str, Any]]`）
- 文档：函数 docstring 简要说明输入/输出以及数据字段含义
- 依赖：通过 `pyproject.toml`/`requirements.txt` 管理
- UI：Streamlit 组件 + Plotly 图表

建议：保持现有风格（不做大范围重排/格式化），小步修改并确保数据字段兼容。