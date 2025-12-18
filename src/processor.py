import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any

def process_frames(frames: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process a list of frame dictionaries into a Pandas DataFrame.
    Extracts relevant metrics for analysis.
    
    新数据格式使用:
    - dx_ned, dy_ned, dz_ned (NED坐标系相对位置)
    - dyaw, dpitch (光轴偏差角，单位：度)
    """
    data_list = []
    for frame in frames:
        timestamp = frame.get('timestamp')
        
        # Ground Truth
        gt = frame.get('ground_truth', {})
        gt_rel = gt.get('relative_to_ship', {})
        gt_att = gt.get('attitude', {})
        
        # 使用新的字段名: dx_ned, dy_ned, dz_ned
        gt_dist = gt_rel.get('distance')
        gt_lat = gt_rel.get('dx_ned')  # 横向 (NED坐标系)
        gt_lon = gt_rel.get('dy_ned')  # 纵向 (NED坐标系)
        gt_h = gt_rel.get('dz_ned')    # 高度 (NED坐标系)
        gt_yaw = gt_att.get('yaw')
        gt_pitch = gt_att.get('pitch')
        
        # Ground Truth 光轴偏差角 (从 relative_to_ship 中提取)
        gt_dyaw = gt_rel.get('dyaw')    # 真值的偏航光轴偏差角 (度)
        gt_dpitch = gt_rel.get('dpitch') # 真值的俯仰光轴偏差角 (度)
        
        # Algorithm Output
        algo = frame.get('algorithm_output', {})
        algo_dist = algo.get('distance')
        algo_lat = algo.get('dx_ned')   # 横向 (NED坐标系)
        algo_lon = algo.get('dy_ned')   # 纵向 (NED坐标系)
        algo_h = algo.get('dz_ned')     # 高度 (NED坐标系)
        algo_dyaw = algo.get('dyaw')    # 算法输出的偏航光轴偏差角 (度)
        algo_dpitch = algo.get('dpitch') # 算法输出的俯仰光轴偏差角 (度)
        
        # Errors
        err = frame.get('errors', {})
        dist_err = err.get('distance_error')
        lat_err = err.get('lateral_error')
        lon_err = err.get('longitudinal_error')
        h_err = err.get('height_error')
        dyaw_err = err.get('dyaw_error', 0.0)      # 偏航光轴偏差角误差 (度)
        dpitch_err = err.get('dpitch_error', 0.0)  # 俯仰光轴偏差角误差 (度)

        data_list.append({
            'timestamp': timestamp,
            'gt_distance': gt_dist,
            'algo_distance': algo_dist,
            'distance_error': dist_err,
            'gt_lateral': gt_lat,
            'algo_lateral': algo_lat,
            'lateral_error': lat_err,
            'gt_longitudinal': gt_lon,
            'algo_longitudinal': algo_lon,
            'longitudinal_error': lon_err,
            'gt_height': gt_h,
            'algo_height': algo_h,
            'height_error': h_err,
            'gt_yaw': gt_yaw,
            'gt_pitch': gt_pitch,
            'gt_dyaw': gt_dyaw,          # 真值的偏航光轴偏差角
            'gt_dpitch': gt_dpitch,      # 真值的俯仰光轴偏差角
            'algo_dyaw': algo_dyaw,      # 算法输出的偏航光轴偏差角
            'algo_dpitch': algo_dpitch,  # 算法输出的俯仰光轴偏差角
            'dyaw_error': dyaw_err,      # 偏航光轴偏差角误差
            'dpitch_error': dpitch_err,   # 俯仰光轴偏差角误差
            'algo_confidence': algo.get('confidence', 1.0), # 算法置信度
            'image_path': frame.get('image_path', ''),      # 图片完整路径
            'image_name': os.path.basename(frame.get('image_path', '')) # 图片文件名
        })
    
    return pd.DataFrame(data_list)
