#!/bin/bash
# Unix/Linux/macOS 打包脚本 - 使用 uv build
# 使用方法: ./build_unix.sh

set -e  # 遇到错误立即退出

echo "开始 Unix 平台打包..."

# 检查是否安装了 uv
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv 工具"
    echo "请先安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 清理之前的构建
echo "清理之前的构建文件..."
rm -rf dist/ build/ *.egg-info/

# 使用 uv 同步依赖
echo "同步依赖..."
uv sync

# 使用 uv 构建 wheel 包
echo "构建 wheel 包..."
uv build

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ 打包成功！"
    echo "生成的文件位于 dist/ 目录："
    ls -lh dist/
    echo ""
    echo "安装方法:"
    echo "  pip install dist/uv_navigation_inspection-*.whl"
    echo ""
    echo "或使用 uv 安装:"
    echo "  uv pip install dist/uv_navigation_inspection-*.whl"
    echo ""
    echo "安装后运行:"
    echo "  uv_navigation_inspection"
else
    echo ""
    echo "✗ 打包失败！请检查错误信息。"
    exit 1
fi
