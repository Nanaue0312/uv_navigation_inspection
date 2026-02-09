# Windows 打包脚本 - 使用 PyInstaller
# 使用方法: .\build_windows.ps1

Write-Host "开始 Windows 平台打包..." -ForegroundColor Green

# 检查是否安装了 PyInstaller
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "未找到 PyInstaller，正在安装..." -ForegroundColor Yellow
    uv run pip install pyinstaller
}

# 清理之前的构建
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
if (Test-Path "*.spec") {
    Remove-Item -Force "*.spec"
}

Write-Host "正在使用 PyInstaller 打包..." -ForegroundColor Cyan

# PyInstaller 打包命令
# 注意：Streamlit 需要特殊处理
uv run pyinstaller --onefile `
    --name uv_navigation_inspection `
    --add-data "app.py;." `
    --add-data "src;src" `
    --hidden-import streamlit.web.cli `
    --hidden-import streamlit.runtime.scriptrunner.magic_funcs `
    --hidden-import streamlit `
    --hidden-import plotly `
    --hidden-import plotly.graph_objs `
    --hidden-import pandas `
    --hidden-import numpy `
    --hidden-import scipy `
    --hidden-import scipy.signal `
    --hidden-import matplotlib `
    --hidden-import matplotlib.pyplot `
    --hidden-import seaborn `
    --hidden-import PIL `
    --hidden-import altair `
    --collect-all streamlit `
    --copy-metadata streamlit `
    --copy-metadata plotly `
    --collect-all scipy `
    run_app.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ 打包成功！" -ForegroundColor Green
    Write-Host "可执行文件位置: dist\uv_navigation_inspection.exe" -ForegroundColor Green
    Write-Host "`n使用方法:" -ForegroundColor Yellow
    Write-Host "  .\dist\uv_navigation_inspection.exe" -ForegroundColor White
    Write-Host "  - 按 Ctrl+C 停止应用" -ForegroundColor White
} else {
    Write-Host "`n✗ 打包失败！请检查错误信息。" -ForegroundColor Red
    Write-Host "`n常见问题:" -ForegroundColor Yellow
    Write-Host "  1. 确保所有依赖已安装: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "  2. 尝试清理缓存: pip cache purge" -ForegroundColor White
    Write-Host "  3. 查看详细日志以获取更多信息" -ForegroundColor White
    exit 1
}
