# 算法性能分析数据格式规范

**版本**: v1.0  
**发布日期**: 2025-11-22  
**适用软件**: 紫外线降落引导仿真系统 v1.0.5+

---

## 📋 概述

本文档定义了闭环仿真输出的标准JSON数据格式，供算法性能分析软件使用。
所有闭环仿真都会输出此格式的数据文件。

## 📁 文件结构

```
output/closed_loop_YYYYMMDD_HHMMSS/
├── closed_loop_simulation.mp4       # 仿真视频
├── analysis_data.json                # 完整分析数据（本文档定义）
└── summary.json                      # 简要统计信息
```

---

## 📊 数据格式定义

### 1. 顶层结构

```json
{
  "format_version": "1.0",
  "metadata": { ... },
  "frames": [ ... ],
  "statistics": { ... }
}
```

### 2. metadata（元数据）

仿真基本信息：

```json
{
  "metadata": {
    "simulation_id": "closed_loop_20251122_143000",
    "format_version": "1.0",
    "software_version": "1.0.5",
    "generation_time": "2025-11-22T14:35:20",
    
    "simulation_config": {
      "duration_seconds": 120.0,
      "frame_rate": 30,
      "total_frames": 3600,
      "time_step": 0.0333
    },
    
    "algorithm_info": {
      "library_path": "algorithms/pose_estimation.dll",
      "library_name": "pose_estimation",
      "platform": "Windows"
    },
    
    "scenario": {
      "glide_path": "standard_3.4deg",
      "initial_position_ned": [0.0, 0.0, -1500.0],
      "initial_attitude_deg": [0.0, -30.0, 300.0],
      "sea_state": 3,
      "beacon_layout": "C_shape_4x4",
      "beacon_spacing_m": 2.0
    },
    
    "camera_config": {
      "resolution": [1280, 720],
      "focal_length_mm": 8.0,
      "fov_deg": [12.68, 6.38],
      "initial_gain_db": 0.0,
      "agc_enabled": true,
      "em_gain_enabled": false
    }
  }
}
```

**字段说明**：
- `simulation_id`: 仿真唯一标识符
- `generation_time`: 数据生成时间（ISO 8601格式）
- `duration_seconds`: 仿真时长（秒）
- `total_frames`: 总帧数
- `glide_path`: 下滑道类型
- `initial_position_ned`: 初始位置 [北, 东, 地]（米，NED坐标系）
- `initial_attitude_deg`: 初始姿态 [Roll, Pitch, Yaw]（度）

### 3. frames（帧数据）

每帧的完整数据，包含真实值、算法输出、误差等：

```json
{
  "frames": [
    {
      "frame_id": 0,
      "timestamp": 0.0,
      
      "ground_truth": {
        "position_ned": {
          "north": 0.0,
          "east": 0.0,
          "down": -1500.0,
          "description": "NED坐标系，单位米，down为正值向下，负值表示高度"
        },
        
        "attitude": {
          "roll": 0.0,
          "pitch": -0.5236,
          "yaw": 5.2360,
          "description": "姿态角，单位弧度，roll=横滚，pitch=俯仰，yaw=偏航/航向"
        },
        
        "velocity_ned": {
          "vn": 0.0,
          "ve": 0.0,
          "vd": -5.0,
          "speed": 5.0,
          "description": "NED坐标系速度，单位m/s，speed为合速度"
        },
        
        "relative_to_ship": {
          "distance": 1500.0,
          "x_lateral": 0.0,
          "y_longitudinal": 0.0,
          "z_height": 1500.0,
          "description": "相对于着舰点，x=横向(左负右正)，y=纵向(前正后负)，z=高度"
        }
      },
      
      "algorithm_output": {
        "distance": 1502.3,
        "x_lateral": -0.15,
        "y_longitudinal": 0.23,
        "z_height": 1498.5,
        "heading": 5.2400,
        "roll_cmd": 0.0035,
        "pitch_cmd": -0.0087,
        "yaw_cmd": 0.0012,
        "gain_cmd": 0.65,
        "confidence": 0.856,
        "processing_time_ms": 8.5,
        "description": "算法输出，单位与ground_truth一致，控制指令为增量"
      },
      
      "errors": {
        "distance_error": 2.3,
        "lateral_error": -0.15,
        "longitudinal_error": 0.23,
        "height_error": -1.5,
        "heading_error_rad": 0.0040,
        "heading_error_deg": 0.229,
        "position_error_3d": 2.35,
        "description": "误差 = 算法输出 - 真实值"
      },
      
      "environment": {
        "ship_motion": {
          "roll": 0.0349,
          "pitch": 0.0175,
          "yaw": 0.0,
          "heave": 0.5,
          "description": "船舶6-DOF运动，单位：角度(rad)，位移(m)"
        },
        
        "camera_state": {
          "gain_db": 12.5,
          "exposure_ms": 10.0,
          "em_gain": 1.0,
          "agc_enabled": true,
          "mean_brightness": 1250,
          "description": "相机参数，mean_brightness为12-bit灰度值"
        },
        
        "image_quality": {
          "num_detected_lights": 16,
          "mean_intensity": 2500.0,
          "snr_db": 18.5,
          "description": "图像质量指标（可选）"
        }
      }
    }
  ]
}
```

**关键字段说明**：

#### ground_truth（真实值）
- `position_ned`: NED坐标系位置（北-东-地，单位米）
- `attitude`: 姿态角（弧度）
- `velocity_ned`: NED坐标系速度（m/s）
- `relative_to_ship`: 相对着舰点的位置（米）

#### algorithm_output（算法输出）
- `distance`: 算法估计的斜距（米）
- `x_lateral`, `y_longitudinal`, `z_height`: 算法估计的相对位置（米）
- `heading`: 算法估计的航向角（弧度）
- `roll_cmd`, `pitch_cmd`, `yaw_cmd`: 控制指令增量（弧度）
- `gain_cmd`: 增益控制（0-1，表示0-100%）
- `confidence`: 算法置信度（0-1）
- `processing_time_ms`: 算法处理时间（毫秒）

#### errors（误差）
- 所有误差 = 算法输出 - 真实值
- 单位与对应的真实值一致

### 4. statistics（统计信息）

仿真整体统计：

```json
{
  "statistics": {
    "execution": {
      "total_frames": 3600,
      "algorithm_calls": 3598,
      "successful_detections": 3580,
      "success_rate": 0.994,
      "control_adjustments": 2456,
      "gain_adjustments": 892
    },
    
    "algorithm_performance": {
      "average_confidence": 0.823,
      "confidence_std": 0.125,
      "average_processing_time_ms": 8.2,
      "max_processing_time_ms": 15.3,
      "frames_with_high_confidence": 3200
    },
    
    "error_statistics": {
      "distance": {
        "mean": 0.5,
        "std": 1.2,
        "rmse": 1.3,
        "max": 5.8,
        "percentile_50": 0.4,
        "percentile_95": 2.8
      },
      "lateral": {
        "mean": -0.02,
        "std": 0.15,
        "rmse": 0.15,
        "max": 0.45,
        "percentile_50": -0.01,
        "percentile_95": 0.28
      },
      "longitudinal": {
        "mean": 0.05,
        "std": 0.18,
        "rmse": 0.19,
        "max": 0.52,
        "percentile_50": 0.03,
        "percentile_95": 0.35
      },
      "height": {
        "mean": -0.1,
        "std": 0.8,
        "rmse": 0.81,
        "max": 3.2,
        "percentile_50": -0.05,
        "percentile_95": 1.5
      },
      "heading": {
        "mean_deg": 0.05,
        "std_deg": 0.25,
        "rmse_deg": 0.26,
        "max_deg": 1.2,
        "percentile_50_deg": 0.03,
        "percentile_95_deg": 0.55
      }
    },
    
    "convergence_metrics": {
      "initial_distance_error": 45.2,
      "final_distance_error": 0.8,
      "convergence_time_s": 25.5,
      "steady_state_error": 0.5
    }
  }
}
```

**字段说明**：
- `rmse`: 均方根误差
- `percentile_50`: 中位数
- `percentile_95`: 95%分位数
- `frames_with_high_confidence`: 置信度>0.8的帧数

---

## 🔧 数据单位规范

| 物理量 | 单位 | 说明 |
|--------|------|------|
| **位置** | 米 (m) | NED坐标系或相对坐标 |
| **角度** | 弧度 (rad) | 数据中统一使用弧度 |
| **角度（可选）** | 度 (deg) | 仅在error字段中提供度数版本 |
| **速度** | 米/秒 (m/s) | 线速度 |
| **时间** | 秒 (s) | 时间戳和时长 |
| **时间（短）** | 毫秒 (ms) | 算法处理时间 |
| **置信度** | 0-1 | 无量纲，1表示完全置信 |
| **增益** | 0-1 | 无量纲，1表示100% |

---

## 📐 坐标系定义

### NED坐标系（北-东-地）
- **N (North)**: 北向为正
- **E (East)**: 东向为正
- **D (Down)**: 向下为正（高度为负值）

**示例**：
- 位置 `[0, 0, -1500]` 表示：北0米，东0米，高度1500米
- 速度 `[0, 0, -5]` 表示：向上5m/s

### 相对坐标系（相对于着舰点）
- **X (Lateral)**: 横向，左负右正
- **Y (Longitudinal)**: 纵向，前正后负
- **Z (Height)**: 高度，向上为正

---

## 💾 文件命名规范

### analysis_data.json
完整的帧数据，包含所有信息。

**文件大小估算**：
- 每帧约 1.5KB
- 30fps × 60s = 1800帧 ≈ 2.7MB
- 30fps × 120s = 3600帧 ≈ 5.4MB

### summary.json
仅包含 `metadata` 和 `statistics`，不包含 `frames`。

**用途**：快速查看仿真结果，不需要加载全部帧数据。

---

## 🔍 数据完整性验证

### 必需字段检查清单

**metadata必需字段**：
- ✅ `format_version`
- ✅ `simulation_id`
- ✅ `software_version`
- ✅ `generation_time`
- ✅ `simulation_config`
- ✅ `scenario`

**每帧必需字段**：
- ✅ `frame_id`
- ✅ `timestamp`
- ✅ `ground_truth` (包含 position_ned, attitude, relative_to_ship)
- ✅ `algorithm_output` (包含 distance, confidence)
- ✅ `errors`

**statistics必需字段**：
- ✅ `execution`
- ✅ `algorithm_performance`
- ✅ `error_statistics`

---

## 📚 使用示例

### Python读取示例

```python
import json
import numpy as np
import pandas as pd

# 读取数据
with open('analysis_data.json', 'r') as f:
    data = json.load(f)

# 获取元数据
metadata = data['metadata']
print(f"仿真ID: {metadata['simulation_id']}")
print(f"总帧数: {metadata['simulation_config']['total_frames']}")

# 转换为DataFrame
frames = data['frames']
df = pd.DataFrame([
    {
        'timestamp': f['timestamp'],
        'gt_distance': f['ground_truth']['relative_to_ship']['distance'],
        'algo_distance': f['algorithm_output']['distance'],
        'distance_error': f['errors']['distance_error'],
        'confidence': f['algorithm_output']['confidence'],
    }
    for f in frames
])

# 计算统计量
print(f"平均距离误差: {df['distance_error'].mean():.2f}m")
print(f"RMSE: {np.sqrt((df['distance_error']**2).mean()):.2f}m")
```

### JavaScript读取示例

```javascript
// 读取数据
fetch('analysis_data.json')
  .then(response => response.json())
  .then(data => {
    // 获取元数据
    const metadata = data.metadata;
    console.log(`仿真ID: ${metadata.simulation_id}`);
    
    // 处理帧数据
    const frames = data.frames;
    const distanceErrors = frames.map(f => f.errors.distance_error);
    
    // 计算平均误差
    const meanError = distanceErrors.reduce((a, b) => a + b) / distanceErrors.length;
    console.log(`平均距离误差: ${meanError.toFixed(2)}m`);
  });
```

### MATLAB读取示例

```matlab
% 读取数据
data = jsondecode(fileread('analysis_data.json'));

% 获取元数据
metadata = data.metadata;
fprintf('仿真ID: %s\n', metadata.simulation_id);

% 提取帧数据
frames = data.frames;
timestamps = arrayfun(@(x) x.timestamp, frames);
gt_distances = arrayfun(@(x) x.ground_truth.relative_to_ship.distance, frames);
algo_distances = arrayfun(@(x) x.algorithm_output.distance, frames);

% 绘图
figure;
plot(timestamps, gt_distances, 'b-', timestamps, algo_distances, 'r-');
legend('真实距离', '算法距离');
xlabel('时间 (s)');
ylabel('距离 (m)');
```

---

## 📝 版本历史

### v1.0 (2025-11-22)
- 初始版本
- 定义基本数据结构
- 支持位置、姿态、速度、误差数据
- 支持环境状态和图像质量数据

---

## 🔗 相关文档

- `ALGORITHM_INTERFACE_GUIDE.md` - 算法接口规范
- `软件使用说明书.md` - 用户使用指南
- `README.md` - 系统概述

---

**维护者**: 紫外线降落引导仿真系统开发团队  
**联系方式**: 见项目主页
