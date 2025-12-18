# 数据格式适配修改总结

**日期**: 2025-12-18  
**修改者**: Antigravity AI  
**目的**: 适配真实照片评估数据的新格式

---

## 📋 问题分析

### 发现的不匹配问题

通过分析 `real_photo_eval_1766028624_analysis_bundle/analysis_data.json` 和现有代码，发现以下数据结构不匹配：

1. **相对位置字段命名**
   - ❌ 文档期望: `x_lateral`, `y_longitudinal`, `z_height`
   - ✅ 实际数据: `dx_ned`, `dy_ned`, `dz_ned`

2. **航向角字段**
   - ❌ 代码期望: `algorithm_output.heading`
   - ✅ 实际数据: `algorithm_output.dyaw`, `algorithm_output.dpitch` (光轴偏差角)

3. **误差字段**
   - ❌ 代码期望: `errors.heading_error_deg` 或 `heading_error_rad`
   - ✅ 实际数据: `errors.dyaw`, `errors.dpitch` (单位已经是度)

---

## ✅ 实施的修改

### 1. 修改 `src/processor.py`

**目标**: 支持新的 NED 坐标系字段和光轴偏差角

**关键更改**:
```python
# 旧代码（不匹配）
gt_lat = gt_rel.get('x_lateral')
gt_lon = gt_rel.get('y_longitudinal')
gt_h = gt_rel.get('z_height')
algo_heading = algo.get('heading')

# 新代码（匹配实际数据）
gt_lat = gt_rel.get('dx_ned')   # 横向 (NED坐标系)
gt_lon = gt_rel.get('dy_ned')   # 纵向 (NED坐标系)
gt_h = gt_rel.get('dz_ned')     # 高度 (NED坐标系)
algo_dyaw = algo.get('dyaw')    # 偏航光轴偏差角 (度)
algo_dpitch = algo.get('dpitch') # 俯仰光轴偏差角 (度)
```

**新增字段**:
- `gt_yaw`: 真实偏航角（从姿态数据中提取）
- `gt_pitch`: 真实俯仰角（从姿态数据中提取）
- `algo_dyaw`: 算法输出的偏航光轴偏差角
- `algo_dpitch`: 算法输出的俯仰光轴偏差角
- `dyaw_error`: 偏航偏差角误差
- `dpitch_error`: 俯仰偏差角误差

### 2. 修改 `app.py`

**目标**: 更新 UI 以显示光轴偏差角分析，而不是航向分析

**更改内容**:

#### A. 侧边栏配置 (第77-89行)
```python
# 旧代码
st.markdown("**航向误差 (deg)**")
heading_lower = st.number_input("下限", value=-0.5, ...)
heading_upper = st.number_input("上限", value=0.5, ...)

# 新代码
st.markdown("**偏航光轴偏差角 (deg)**")
dyaw_lower = st.number_input("下限", value=-2.0, ...)
dyaw_upper = st.number_input("上限", value=2.0, ...)

st.markdown("**俯仰光轴偏差角 (deg)**")
dpitch_lower = st.number_input("下限", value=-1.5, ...)
dpitch_upper = st.number_input("上限", value=1.5, ...)
```

#### B. 标签页 (第122行)
```python
# 旧代码 - 5个标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "距离分析", "侧向分析", "纵向分析", "高度分析", "航向分析"
])

# 新代码 - 6个标签页
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "距离分析", "侧向分析", "纵向分析", "高度分析", 
    "偏航光轴偏差角", "俯仰光轴偏差角"
])
```

#### C. 光轴偏差角显示 (第168-185行)
```python
# tab5: 偏航光轴偏差角
with tab5:
    st.subheader("偏航光轴偏差角分析 (Dyaw)")
    st.markdown("**光轴偏差角**：算法输出的光轴偏差角，单位为度")
    
    # 只显示算法输出的 dyaw，因为没有对应的 ground truth
    fig9 = plot_error(df, 'timestamp', 'dyaw_error',
                    '偏航光轴偏差角', '偏差角 (deg)', 
                    bounds=(dyaw_lower, dyaw_upper))
    st.plotly_chart(fig9, width='stretch', config={'scrollZoom': False})

# tab6: 俯仰光轴偏差角
with tab6:
    st.subheader("俯仰光轴偏差角分析 (Dpitch)")
    st.markdown("**光轴偏差角**：算法输出的光轴偏差角，单位为度")
    
    # 只显示算法输出的 dpitch，因为没有对应的 ground truth
    fig10 = plot_error(df, 'timestamp', 'dpitch_error',
                     '俯仰光轴偏差角', '偏差角 (deg)', 
                     bounds=(dpitch_lower, dpitch_upper))
    st.plotly_chart(fig10, width='stretch', config={'scrollZoom': False})
```

---

## 🧪 测试结果

### 测试环境
- **应用程序**: Streamlit (运行在 http://localhost:8502)
- **测试数据**: `real_photo_eval_1766028624_analysis_bundle/analysis_data.json`
- **测试日期**: 2025-12-18

### 测试验证
✅ **数据加载**: 成功加载 JSON 文件，无错误  
✅ **统计信息**: 正确显示总帧数 (30)、成功率 (100%)、RMSE 等指标  
✅ **距离分析**: 图表正确显示理论值与实际值对比  
✅ **侧向分析**: 正确提取 `dx_ned` 字段并显示  
✅ **纵向分析**: 正确提取 `dy_ned` 字段并显示  
✅ **高度分析**: 正确提取 `dz_ned` 字段并显示  
✅ **偏航光轴偏差角**: 新标签页正确显示 `dyaw` 数据  
✅ **俯仰光轴偏差角**: 新标签页正确显示 `dpitch` 数据  

### 浏览器测试截图
测试录像已保存至: `C:/Users/nanaue/.gemini/antigravity/brain/.../test_data_loading_xxx.webp`

---

## 📊 数据结构对比表

| 字段类别 | 旧格式（文档） | 新格式（实际数据） | 状态 |
|---------|---------------|-------------------|------|
| 横向位置 | `x_lateral` | `dx_ned` | ✅ 已适配 |
| 纵向位置 | `y_longitudinal` | `dy_ned` | ✅ 已适配 |
| 高度 | `z_height` | `dz_ned` | ✅ 已适配 |
| 航向输出 | `heading` | `dyaw`, `dpitch` | ✅ 已适配 |
| 航向误差 | `heading_error_deg` | `dyaw`, `dpitch` | ✅ 已适配 |

---

## 💡 设计决策

### 为什么分成两个标签页？
原始数据中 `dyaw` 和 `dpitch` 是两个独立的光轴偏差角测量值：
- `dyaw`: 偏航方向的光轴偏差（左右偏差）
- `dpitch`: 俯仰方向的光轴偏差（上下偏差）

它们不能像原来的 `heading` 那样合并为单一测量值，因此创建了两个独立的标签页来分别显示。

### 为什么只显示误差图表？
在新数据格式中：
- `ground_truth` 只包含飞行器的 `yaw` 和 `pitch` 姿态角
- `algorithm_output` 输出的是相对的**光轴偏差角** `dyaw` 和 `dpitch`
- 这两者不是同一个物理量，无法直接对比

因此光轴偏差角标签页只显示误差图表（单一时间序列），而不显示"理论值 vs 实际值"对比图。

---

## 📝 后续建议

1. **更新文档**: 建议修改 `docs/ANALYSIS_DATA_FORMAT.md`，将标准格式更新为使用 `dx_ned`, `dy_ned`, `dz_ned`

2. **向后兼容性**: 如果需要同时支持旧格式和新格式，可以在 `processor.py` 中添加回退逻辑：
   ```python
   # 尝试新格式，回退到旧格式
   gt_lat = gt_rel.get('dx_ned') or gt_rel.get('x_lateral')
   ```

3. **数据验证**: 建议添加数据格式验证，检测必需字段是否存在

---

## ✨ 总结

所有修改已完成并通过测试。应用程序现在可以正确处理使用 NED 坐标系字段（`dx_ned`, `dy_ned`, `dz_ned`）和光轴偏差角（`dyaw`, `dpitch`）的新数据格式。

**修改的文件**:
- `src/processor.py` - 数据提取逻辑
- `app.py` - UI 和可视化

**兼容性**: 仅支持新格式（按用户要求）
