# 打包与部署说明

本文档详细说明如何在不同平台上打包和部署 UV Navigation Inspection 应用。

## 目录

- [Windows 平台打包（PyInstaller）](#windows-平台打包pyinstaller)
- [Unix/Linux/macOS 平台打包（uv build）](#unixlinuxmacos-平台打包uv-build)
- [通用打包方式（Python wheel）](#通用打包方式python-wheel)
- [常见问题](#常见问题)

---

## Windows 平台打包（PyInstaller）

### 方式一：使用自动化脚本（推荐）

1. **运行打包脚本**

```powershell
.\build_windows.ps1
```

2. **查找生成的可执行文件**

打包成功后，可执行文件位于 `dist\uv_navigation_inspection.exe`

3. **运行应用**

```powershell
.\dist\uv_navigation_inspection.exe
```

### 方式二：手动打包

1. **安装 PyInstaller**

```powershell
pip install pyinstaller
```

2. **执行打包命令**

```powershell
pyinstaller --onefile `
    --name uv_navigation_inspection `
    --add-data "src;src" `
    --hidden-import streamlit `
    --hidden-import plotly `
    --hidden-import pandas `
    --hidden-import numpy `
    --hidden-import matplotlib `
    --hidden-import seaborn `
    run_app.py
```

3. **查找生成的文件**

可执行文件位于 `dist\uv_navigation_inspection.exe`

### PyInstaller 参数说明

- `--onefile`: 打包成单个可执行文件
- `--name`: 指定输出文件名
- `--add-data`: 添加数据文件（格式：`源路径;目标路径`）
- `--hidden-import`: 添加隐式导入的模块
- `--noconsole`: （可选）不显示控制台窗口

### 注意事项

1. **文件大小**: 单文件打包后体积较大（约 100-200MB），这是正常的
2. **首次启动**: 第一次运行可能需要较长时间解压
3. **杀毒软件**: 某些杀毒软件可能误报，需要添加信任
4. **依赖数据**: 如果应用需要额外的数据文件，使用 `--add-data` 添加

---

## Unix/Linux/macOS 平台打包（uv build）

### 方式一：使用自动化脚本（推荐）

1. **添加执行权限**

```bash
chmod +x build_unix.sh
```

2. **运行打包脚本**

```bash
./build_unix.sh
```

3. **安装生成的 wheel 包**

```bash
pip install dist/uv_navigation_inspection-*.whl
```

或使用 uv：

```bash
uv pip install dist/uv_navigation_inspection-*.whl
```

4. **运行应用**

```bash
uv_navigation_inspection
```

### 方式二：手动打包

1. **确保已安装 uv**

```bash
# 如果未安装，执行：
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **同步依赖**

```bash
uv sync
```

3. **构建 wheel 包**

```bash
uv build
```

4. **安装**

```bash
uv pip install dist/uv_navigation_inspection-*.whl
```

### uv 工具优势

- 更快的依赖解析和安装速度
- 更好的依赖管理
- 与现代 Python 打包标准兼容
- 适合 CI/CD 集成

---

## 通用打包方式（Python wheel）

适用于所有平台，但需要目标机器有 Python 环境。

### 使用 build 工具

1. **安装 build**

```bash
pip install build
```

2. **构建 wheel 包**

```bash
python -m build
```

3. **安装**

```bash
pip install dist/uv_navigation_inspection-0.1.0-py3-none-any.whl
```

4. **运行**

```bash
uv_navigation_inspection
```

或者：

```bash
streamlit run app.py
```

### 开发模式安装

如果需要在开发时安装（修改代码立即生效）：

```bash
pip install -e .
```

---

## 分发建议

### Windows 用户

**推荐方式**: PyInstaller 单文件可执行程序

**优点**:
- 无需安装 Python
- 双击即可运行
- 适合非技术用户

**分发步骤**:
1. 使用 `build_windows.ps1` 打包
2. 将 `dist\uv_navigation_inspection.exe` 分发给用户
3. 用户双击运行即可

### Linux/macOS 用户

**推荐方式**: uv build 生成的 wheel 包

**优点**:
- 标准 Python 包格式
- 易于版本管理
- 可发布到 PyPI

**分发步骤**:
1. 使用 `build_unix.sh` 打包
2. 将 `dist/*.whl` 文件分发给用户
3. 用户使用 `pip install` 或 `uv pip install` 安装

### 企业内部部署

**推荐方式**: 私有 PyPI 服务器或共享文件服务器

1. 构建 wheel 包
2. 上传到内部 PyPI 服务器或共享目录
3. 用户通过 `pip install` 从内部源安装

---

## 常见问题

### Q1: PyInstaller 打包后运行报错 "Failed to execute script"

**解决方案**:
1. 检查是否缺少隐式导入，添加 `--hidden-import` 参数
2. 使用 `--debug all` 参数查看详细错误信息
3. 确保所有数据文件都通过 `--add-data` 添加

### Q2: uv build 失败，提示缺少 setuptools

**解决方案**:
```bash
pip install setuptools wheel build
```

### Q3: 打包后的文件太大

**解决方案**:
- PyInstaller: 这是正常的，包含了完整的 Python 运行时
- wheel 包: 只包含代码，体积很小，但需要 Python 环境

### Q4: 如何减小 PyInstaller 打包体积？

**方法**:
1. 使用 `--exclude-module` 排除不需要的模块
2. 不使用 `--onefile`，改用 `--onedir`（生成文件夹）
3. 使用 UPX 压缩（需要单独安装）

### Q5: 如何在没有网络的环境中安装？

**方法**:
1. 在有网络的机器上下载所有依赖：
   ```bash
   pip download -d packages uv_navigation_inspection
   ```
2. 将 `packages/` 目录复制到目标机器
3. 离线安装：
   ```bash
   pip install --no-index --find-links=packages uv_navigation_inspection
   ```

### Q6: 如何更新已安装的应用？

**wheel 包方式**:
```bash
pip install --upgrade dist/uv_navigation_inspection-*.whl
```

**PyInstaller 方式**:
直接替换可执行文件即可

---

## 版本发布流程

1. **更新版本号**: 修改 `pyproject.toml` 中的 `version`
2. **构建包**: 运行对应平台的打包脚本
3. **测试**: 在干净环境中测试安装和运行
4. **分发**: 将生成的文件分发给用户或上传到发布平台

---

## 技术支持

如有打包相关问题，请：
1. 查看本文档的常见问题部分
2. 检查 GitHub Issues
3. 联系项目维护者

---

**最后更新**: 2025-11-24
