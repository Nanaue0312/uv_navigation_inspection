# 常用命令（Windows / PowerShell）

## 安装依赖
### 使用 uv（推荐）
- `uv sync`

### 使用 venv + pip
- `python -m venv .venv`
- `\.\.venv\Scripts\Activate.ps1`
- `pip install -r requirements.txt`

## 运行（开发/本地）
- `streamlit run app.py`
- 或（uv）：`uv run streamlit run app.py`

## 运行（打包入口）
- `python run_app.py`

## 测试
- `pytest tests/`
- 或（uv）：`uv run pytest tests/`

## 打包
- Windows 一键打包：`./build_windows.ps1`
- 手动 PyInstaller：见 `docs/README_PACKAGING.md`

## 常用排查
- 查看依赖：`pip list`
- 查看当前目录：`Get-ChildItem`
