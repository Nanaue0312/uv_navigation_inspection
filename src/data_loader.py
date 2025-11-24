"""
数据加载模块
负责从JSON文件中加载仿真数据
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple


class DataLoader:
    """数据加载器"""
    
    def __init__(self, data_source):
        """
        初始化数据加载器
        
        Args:
            data_source: analysis_data.json文件路径(str/Path) 或 数据字典(dict)
        """
        self.data_source = data_source
        self.data_file = None
        
        if isinstance(data_source, (str, Path)):
            self.data_path = Path(data_source)
            # 判断是文件还是目录
            if self.data_path.is_dir():
                self.data_file = self.data_path / "analysis_data.json"
            else:
                self.data_file = self.data_path
        elif isinstance(data_source, dict):
            self.data = data_source
        else:
            raise ValueError("data_source 必须是文件路径或字典")
            
        self.metadata = None
        self.frames_df = None
        
    def load(self) -> bool:
        """
        加载数据文件
        
        Returns:
            是否加载成功
        """
        try:
            if self.data is None:
                if self.data_file is None or not self.data_file.exists():
                     raise FileNotFoundError(f"数据文件不存在: {self.data_file}")
                
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            
            self.metadata = self.data.get('metadata', {})
            
            # 将帧数据转换为DataFrame
            self._parse_frames()
            
            source_name = self.data_file.name if self.data_file else "In-Memory Dict"
            print(f"✓ 成功加载数据: {source_name}")
            print(f"  - 仿真ID: {self.metadata.get('simulation_id')}")
            print(f"  - 总帧数: {len(self.frames_df)}")
            if not self.frames_df.empty:
                print(f"  - 时长: {self.frames_df['timestamp'].max():.2f}秒")
            
            return True
            
        except Exception as e:
            print(f"✗ 加载数据失败: {e}")
            return False
    
    def _parse_frames(self):
        """解析帧数据并转换为DataFrame"""
        frames = self.data.get('frames', [])
        
        records = []
        for frame in frames:
            # 提取真实值
            gt = frame.get('ground_truth', {})
            gt_pos_ned = gt.get('position_ned', {})
            gt_attitude = gt.get('attitude', {})
            gt_velocity = gt.get('velocity_ned', {})
            gt_relative = gt.get('relative_to_ship', {})
            
            # 提取算法输出
            algo = frame.get('algorithm_output', {})
            
            # 提取误差
            errors = frame.get('errors', {})
            
            # 提取环境信息
            env = frame.get('environment', {})
            ship_motion = env.get('ship_motion', {})
            camera = env.get('camera_state', {})
            
            record = {
                # 基本信息
                'frame_id': frame.get('frame_id'),
                'timestamp': frame.get('timestamp'),
                
                # 真实值 - 位置
                'gt_north': gt_pos_ned.get('north', 0),
                'gt_east': gt_pos_ned.get('east', 0),
                'gt_down': gt_pos_ned.get('down', 0),
                'gt_height': -gt_pos_ned.get('down', 0),  # 转换为正高度
                
                # 真实值 - 姿态
                'gt_roll': gt_attitude.get('roll', 0),
                'gt_pitch': gt_attitude.get('pitch', 0),
                'gt_yaw': gt_attitude.get('yaw', 0),
                
                # 真实值 - 速度
                'gt_vn': gt_velocity.get('vn', 0),
                'gt_ve': gt_velocity.get('ve', 0),
                'gt_vd': gt_velocity.get('vd', 0),
                'gt_speed': gt_velocity.get('speed', 0),
                
                # 真实值 - 相对位置
                'gt_distance': gt_relative.get('distance', 0),
                'gt_x_lateral': gt_relative.get('x_lateral', 0),
                'gt_y_longitudinal': gt_relative.get('y_longitudinal', 0),
                'gt_z_height': gt_relative.get('z_height', 0),
                
                # 算法输出
                'algo_distance': algo.get('distance', 0),
                'algo_x_lateral': algo.get('x_lateral', 0),
                'algo_y_longitudinal': algo.get('y_longitudinal', 0),
                'algo_z_height': algo.get('z_height', 0),
                'algo_heading': algo.get('heading', 0),
                'algo_roll_cmd': algo.get('roll_cmd', 0),
                'algo_pitch_cmd': algo.get('pitch_cmd', 0),
                'algo_yaw_cmd': algo.get('yaw_cmd', 0),
                'algo_gain_cmd': algo.get('gain_cmd', 0),
                'algo_confidence': algo.get('confidence', 0),
                'algo_processing_time_ms': algo.get('processing_time_ms', 0),
                
                # 误差
                'error_distance': errors.get('distance_error', 0),
                'error_lateral': errors.get('lateral_error', 0),
                'error_longitudinal': errors.get('longitudinal_error', 0),
                'error_height': errors.get('height_error', 0),
                'error_heading_rad': errors.get('heading_error_rad', 0),
                'error_heading_deg': errors.get('heading_error_deg', 0),
                'error_position_3d': errors.get('position_error_3d', 0),
                
                # 环境
                'ship_roll': ship_motion.get('roll', 0),
                'ship_pitch': ship_motion.get('pitch', 0),
                'ship_yaw': ship_motion.get('yaw', 0),
                'ship_heave': ship_motion.get('heave', 0),
                'camera_gain_db': camera.get('gain_db', 0),
                'camera_mean_brightness': camera.get('mean_brightness', 0),
            }
            
            records.append(record)
        
        self.frames_df = pd.DataFrame(records)
        
        # 计算绝对误差
        self.frames_df['abs_error_distance'] = np.abs(self.frames_df['error_distance'])
        self.frames_df['abs_error_lateral'] = np.abs(self.frames_df['error_lateral'])
        self.frames_df['abs_error_longitudinal'] = np.abs(self.frames_df['error_longitudinal'])
        self.frames_df['abs_error_height'] = np.abs(self.frames_df['error_height'])
        self.frames_df['abs_error_heading_deg'] = np.abs(self.frames_df['error_heading_deg'])
    
    def get_frames_dataframe(self) -> pd.DataFrame:
        """获取帧数据DataFrame"""
        return self.frames_df
    
    def get_metadata(self) -> Dict:
        """获取元数据"""
        return self.metadata
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return self.data.get('statistics', {})
    
    def filter_by_distance_range(self, min_dist: float = None, max_dist: float = None) -> pd.DataFrame:
        """
        按距离范围筛选数据
        
        Args:
            min_dist: 最小距离（米）
            max_dist: 最大距离（米）
            
        Returns:
            筛选后的DataFrame
        """
        df = self.frames_df.copy()
        
        if min_dist is not None:
            df = df[df['gt_distance'] >= min_dist]
        if max_dist is not None:
            df = df[df['gt_distance'] <= max_dist]
            
        return df
    
    def filter_by_time_range(self, min_time: float = None, max_time: float = None) -> pd.DataFrame:
        """
        按时间范围筛选数据
        
        Args:
            min_time: 开始时间（秒）
            max_time: 结束时间（秒）
            
        Returns:
            筛选后的DataFrame
        """
        df = self.frames_df.copy()
        
        if min_time is not None:
            df = df[df['timestamp'] >= min_time]
        if max_time is not None:
            df = df[df['timestamp'] <= max_time]
            
        return df
