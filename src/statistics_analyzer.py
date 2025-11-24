"""
统计分析模块
负责计算误差统计、指标精度符合率等
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Callable


class StatisticsAnalyzer:
    """统计分析器"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化统计分析器
        
        Args:
            df: 包含真实值、算法输出和误差的DataFrame
        """
        self.df = df
        
    def calculate_accuracy_metrics(self, 
                                   error_column: str,
                                   threshold_func: Callable[[float], float],
                                   distance_column: str = 'gt_distance',
                                   distance_ranges: List[Tuple[float, float]] = None) -> Dict:
        """
        计算指标精度符合率
        
        Args:
            error_column: 误差列名
            threshold_func: 阈值函数，输入距离(m)，返回允许误差阈值
            distance_column: 距离列名
            distance_ranges: 距离范围列表，例如[(0, 800), (0, 1500)]
            
        Returns:
            包含各距离范围符合率的字典
        """
        if distance_ranges is None:
            distance_ranges = [(0, 800), (0, 1500)]
        
        results = {}
        
        for min_dist, max_dist in distance_ranges:
            # 筛选距离范围内的数据
            mask = (self.df[distance_column] >= min_dist) & (self.df[distance_column] <= max_dist)
            df_range = self.df[mask]
            
            if len(df_range) == 0:
                results[f'{min_dist}-{max_dist}m'] = {
                    'total_points': 0,
                    'compliant_points': 0,
                    'compliance_rate': 0.0
                }
                continue
            
            # 计算每个点的阈值
            thresholds = df_range[distance_column].apply(threshold_func)
            
            # 计算符合率（绝对误差小于阈值）
            abs_errors = np.abs(df_range[error_column])
            compliant = abs_errors <= thresholds
            
            total = len(df_range)
            compliant_count = compliant.sum()
            rate = compliant_count / total if total > 0 else 0
            
            results[f'{min_dist}-{max_dist}m'] = {
                'total_points': int(total),
                'compliant_points': int(compliant_count),
                'compliance_rate': float(rate),
                'mean_error': float(abs_errors.mean()),
                'max_error': float(abs_errors.max()),
                'std_error': float(abs_errors.std())
            }
        
        return results
    
    def calculate_distance_accuracy(self, distance_ranges: List[Tuple[float, float]] = None) -> Dict:
        """
        计算距离误差精度
        使用标准：(0.5 + 0.2% × D)
        
        Args:
            distance_ranges: 距离范围列表
            
        Returns:
            符合率统计结果
        """
        def threshold_func(d):
            return 0.5 + 0.002 * d
        
        return self.calculate_accuracy_metrics('error_distance', threshold_func, distance_ranges=distance_ranges)
    
    def calculate_longitudinal_accuracy(self, distance_ranges: List[Tuple[float, float]] = None) -> Dict:
        """
        计算纵向误差精度
        使用标准：(0.5 + 0.2% × D)
        """
        def threshold_func(d):
            return 0.5 + 0.002 * d
        
        return self.calculate_accuracy_metrics('error_longitudinal', threshold_func, distance_ranges=distance_ranges)
    
    def calculate_lateral_accuracy(self, distance_ranges: List[Tuple[float, float]] = None) -> Dict:
        """
        计算侧向误差精度
        使用标准：(0.5 + 0.2% × D)
        """
        def threshold_func(d):
            return 0.5 + 0.002 * d
        
        return self.calculate_accuracy_metrics('error_lateral', threshold_func, distance_ranges=distance_ranges)
    
    def calculate_height_accuracy(self, distance_ranges: List[Tuple[float, float]] = None) -> Dict:
        """
        计算高度误差精度
        使用标准：(0.5 + 0.2% × D)
        """
        def threshold_func(d):
            return 0.5 + 0.002 * d
        
        return self.calculate_accuracy_metrics('error_height', threshold_func, distance_ranges=distance_ranges)
    
    def calculate_heading_accuracy(self, distance_ranges: List[Tuple[float, float]] = None) -> Dict:
        """
        计算航向角误差精度
        使用标准：1°
        """
        def threshold_func(d):
            return 1.0  # 固定阈值1度
        
        return self.calculate_accuracy_metrics('error_heading_deg', threshold_func, distance_ranges=distance_ranges)
    
    def calculate_velocity_accuracy(self, distance_ranges: List[Tuple[float, float]] = None) -> Dict:
        """
        计算速度误差精度
        使用标准：1 m/s
        
        注意：需要先计算速度误差
        """
        # 计算速度误差（如果不存在）
        if 'error_velocity' not in self.df.columns:
            # 计算算法输出速度（假设从位置变化推导）
            # 这里暂时使用真实速度作为参考
            self.df['error_velocity'] = 0  # 占位符，实际需要根据算法输出计算
        
        def threshold_func(d):
            return 1.0  # 固定阈值1 m/s
        
        return self.calculate_accuracy_metrics('error_velocity', threshold_func, distance_ranges=distance_ranges)
    
    def generate_comprehensive_report(self) -> Dict:
        """
        生成综合分析报告
        
        Returns:
            包含所有指标的完整统计结果
        """
        # 定义标准距离范围
        standard_ranges = [(0, 800), (0, 1500)]
        
        # 检查是否有跟踪过程（可以定义为特定距离范围或时间段）
        # 这里假设跟踪过程是距离小于某个阈值的阶段
        max_distance = self.df['gt_distance'].max()
        if max_distance > 100:  # 如果有接近过程
            tracking_ranges = [(0, 100)]  # 跟踪阶段定义为100米以内
        else:
            tracking_ranges = None
        
        report = {
            'distance': {
                'standard_ranges': self.calculate_distance_accuracy(standard_ranges),
            },
            'longitudinal': {
                'standard_ranges': self.calculate_longitudinal_accuracy(standard_ranges),
            },
            'lateral': {
                'standard_ranges': self.calculate_lateral_accuracy(standard_ranges),
            },
            'height': {
                'standard_ranges': self.calculate_height_accuracy(standard_ranges),
            },
            'heading': {
                'standard_ranges': self.calculate_heading_accuracy(standard_ranges),
            }
        }
        
        # 添加跟踪过程统计（如果存在）
        if tracking_ranges:
            report['distance']['tracking'] = self.calculate_distance_accuracy(tracking_ranges)
            report['heading']['tracking'] = self.calculate_heading_accuracy(tracking_ranges)
        
        # 添加基本统计信息
        report['summary'] = {
            'total_frames': len(self.df),
            'duration_seconds': float(self.df['timestamp'].max() - self.df['timestamp'].min()),
            'distance_range': {
                'min': float(self.df['gt_distance'].min()),
                'max': float(self.df['gt_distance'].max()),
                'mean': float(self.df['gt_distance'].mean())
            },
            'overall_errors': {
                'distance': {
                    'mean': float(self.df['abs_error_distance'].mean()),
                    'std': float(self.df['abs_error_distance'].std()),
                    'max': float(self.df['abs_error_distance'].max()),
                    'rmse': float(np.sqrt((self.df['error_distance']**2).mean()))
                },
                'lateral': {
                    'mean': float(self.df['abs_error_lateral'].mean()),
                    'std': float(self.df['abs_error_lateral'].std()),
                    'max': float(self.df['abs_error_lateral'].max()),
                    'rmse': float(np.sqrt((self.df['error_lateral']**2).mean()))
                },
                'longitudinal': {
                    'mean': float(self.df['abs_error_longitudinal'].mean()),
                    'std': float(self.df['abs_error_longitudinal'].std()),
                    'max': float(self.df['abs_error_longitudinal'].max()),
                    'rmse': float(np.sqrt((self.df['error_longitudinal']**2).mean()))
                },
                'height': {
                    'mean': float(self.df['abs_error_height'].mean()),
                    'std': float(self.df['abs_error_height'].std()),
                    'max': float(self.df['abs_error_height'].max()),
                    'rmse': float(np.sqrt((self.df['error_height']**2).mean()))
                },
                'heading': {
                    'mean': float(self.df['abs_error_heading_deg'].mean()),
                    'std': float(self.df['abs_error_heading_deg'].std()),
                    'max': float(self.df['abs_error_heading_deg'].max()),
                    'rmse': float(np.sqrt((self.df['error_heading_deg']**2).mean()))
                }
            }
        }
        
        return report
    
    def format_compliance_report(self, report: Dict) -> str:
        """
        格式化符合率报告为文本
        
        Args:
            report: generate_comprehensive_report()的输出
            
        Returns:
            格式化的文本报告
        """
        lines = []
        lines.append("=" * 80)
        lines.append("紫外导航算法性能分析报告")
        lines.append("=" * 80)
        lines.append("")
        
        # 基本信息
        summary = report['summary']
        lines.append("【基本信息】")
        lines.append(f"总帧数: {summary['total_frames']}")
        lines.append(f"时长: {summary['duration_seconds']:.2f}秒")
        lines.append(f"距离范围: {summary['distance_range']['min']:.2f}m ~ {summary['distance_range']['max']:.2f}m")
        lines.append(f"平均距离: {summary['distance_range']['mean']:.2f}m")
        lines.append("")
        
        # 指标精度符合率
        lines.append("【指标精度符合率】")
        lines.append("")
        
        # 距离
        lines.append("1. 紫外距离")
        for range_name, stats in report['distance']['standard_ranges'].items():
            rate = stats['compliance_rate'] * 100
            lines.append(f"   {range_name}内，{rate:.1f}%的点满足(0.5+0.2%×D)的指标精度要求")
        if 'tracking' in report['distance']:
            for range_name, stats in report['distance']['tracking'].items():
                rate = stats['compliance_rate'] * 100
                lines.append(f"   跟踪过程中({range_name})，{rate:.1f}%的点满足(0.5+0.2%×D)的指标精度要求")
        lines.append("")
        
        # 纵向
        lines.append("2. 紫外纵向")
        for range_name, stats in report['longitudinal']['standard_ranges'].items():
            rate = stats['compliance_rate'] * 100
            lines.append(f"   {range_name}内，{rate:.1f}%的点满足(0.5+0.2%×D)的指标精度要求")
        lines.append("")
        
        # 侧向
        lines.append("3. 紫外侧向")
        for range_name, stats in report['lateral']['standard_ranges'].items():
            rate = stats['compliance_rate'] * 100
            lines.append(f"   {range_name}内，{rate:.1f}%的点满足(0.5+0.2%×D)的指标精度要求")
        lines.append("")
        
        # 高度
        lines.append("4. 紫外高度")
        for range_name, stats in report['height']['standard_ranges'].items():
            rate = stats['compliance_rate'] * 100
            lines.append(f"   {range_name}内，{rate:.1f}%的点满足(0.5+0.2%×D)的指标精度要求")
        lines.append("")
        
        # 航向角
        lines.append("5. 紫外航向角")
        for range_name, stats in report['heading']['standard_ranges'].items():
            rate = stats['compliance_rate'] * 100
            lines.append(f"   {range_name}内，{rate:.1f}%的点满足1°的指标精度要求")
        if 'tracking' in report['heading']:
            for range_name, stats in report['heading']['tracking'].items():
                rate = stats['compliance_rate'] * 100
                lines.append(f"   跟踪过程中({range_name})，{rate:.1f}%的点满足1°的指标精度要求")
        lines.append("")
        
        # 总体误差统计
        lines.append("【总体误差统计】")
        lines.append("")
        overall = summary['overall_errors']
        
        for metric_name, metric_label in [
            ('distance', '距离'),
            ('lateral', '侧向'),
            ('longitudinal', '纵向'),
            ('height', '高度'),
            ('heading', '航向角')
        ]:
            metric = overall[metric_name]
            unit = '°' if metric_name == 'heading' else 'm'
            lines.append(f"{metric_label}误差:")
            lines.append(f"   平均: {metric['mean']:.4f}{unit}")
            lines.append(f"   标准差: {metric['std']:.4f}{unit}")
            lines.append(f"   最大: {metric['max']:.4f}{unit}")
            lines.append(f"   RMSE: {metric['rmse']:.4f}{unit}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
