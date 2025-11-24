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

## 示例数据
目录 `data/` 下有两个示例 CSV：
- `sample_algorithm.csv`
- `sample_simulation.csv`
列结构一致，含 `time,x,y,z`。

## 数据列要求
必须包含以下列：
- `time` : 时间戳或序列（数值）
- `x, y, z` : 三维位置数值

## 后续可扩展点（待讨论）
- 姿态(roll,pitch,yaw)误差
- 动态滤波与估计结果对比
- 误差随环境参数分组分析
- 误差统计导出 (CSV / Excel / PDF)
- 高级图形(3D轨迹对比)

## 许可证
当前未设置公共开源协议，内部使用。
