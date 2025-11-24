"""
可视化模块
负责生成各种误差分析图表
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional
from scipy.interpolate import make_interp_spline


# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """可视化器"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = "reports"):
        """
        初始化可视化器
        
        Args:
            df: 包含数据的DataFrame
            output_dir: 输出目录
        """
        self.df = df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_error_vs_time(self, 
                          error_columns: List[str],
                          labels: List[str],
                          title: str,
                          ylabel: str,
                          filename: Optional[str] = None,
                          show_threshold: bool = False,
                          threshold_func = None,
                          smooth: bool = True,
                          ylim: Optional[Tuple[float, float]] = None) -> any:
        """
        绘制误差随时间变化曲线
        
        Args:
            error_columns: 误差列名列表
            labels: 图例标签列表
            title: 图表标题
            ylabel: Y轴标签
            filename: 保存文件名 (若为None则不保存，返回Figure对象)
            show_threshold: 是否显示阈值线
            threshold_func: 阈值函数
            smooth: 是否平滑曲线
            ylim: Y轴范围 (min, max)
            
        Returns:
            保存的文件路径(str) 或 Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        time = self.df['timestamp'].values
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, (col, label) in enumerate(zip(error_columns, labels)):
            if col not in self.df.columns:
                continue
                
            error = self.df[col].values
            
            if smooth and len(time) > 10:
                # 平滑曲线
                try:
                    # 减少数据点用于平滑
                    indices = np.linspace(0, len(time)-1, min(len(time), 100), dtype=int)
                    time_smooth = time[indices]
                    error_smooth = error[indices]
                    
                    spl = make_interp_spline(time_smooth, error_smooth, k=3)
                    time_fine = np.linspace(time_smooth.min(), time_smooth.max(), 300)
                    error_fine = spl(time_fine)
                    
                    ax.plot(time_fine, error_fine, label=label, linewidth=2, color=colors[i % len(colors)])
                    ax.scatter(time, error, alpha=0.3, s=10, color=colors[i % len(colors)])
                except:
                    # 如果平滑失败，直接绘制原始数据
                    ax.plot(time, error, label=label, linewidth=1.5, alpha=0.7, color=colors[i % len(colors)])
            else:
                ax.plot(time, error, label=label, linewidth=1.5, alpha=0.7, color=colors[i % len(colors)])
        
        # 添加阈值线
        if show_threshold and threshold_func is not None:
            distances = self.df['gt_distance'].values
            thresholds_pos = [threshold_func(d) for d in distances]
            thresholds_neg = [-threshold_func(d) for d in distances]
            
            ax.plot(time, thresholds_pos, '--', color='red', alpha=0.5, linewidth=1, label='阈值上限')
            ax.plot(time, thresholds_neg, '--', color='red', alpha=0.5, linewidth=1, label='阈值下限')
        
        if ylim:
            ax.set_ylim(ylim)
            
        ax.set_xlabel('时间 (s)', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        if filename:
            filepath = self.output_dir / filename
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            return str(filepath)
        else:
            plt.tight_layout()
            return fig
    
    def plot_error_vs_distance(self,
                              error_columns: List[str],
                              labels: List[str],
                              title: str,
                              ylabel: str,
                              filename: Optional[str] = None,
                              show_threshold: bool = False,
                              threshold_func = None,
                              smooth: bool = True,
                              ylim: Optional[Tuple[float, float]] = None) -> any:
        """
        绘制误差随距离变化曲线
        
        Args:
            error_columns: 误差列名列表
            labels: 图例标签列表
            title: 图表标题
            ylabel: Y轴标签
            filename: 保存文件名 (若为None则不保存，返回Figure对象)
            show_threshold: 是否显示阈值线
            threshold_func: 阈值函数
            smooth: 是否平滑曲线
            ylim: Y轴范围 (min, max)
            
        Returns:
            保存的文件路径(str) 或 Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        distance = self.df['gt_distance'].values
        
        # 按距离排序
        sorted_indices = np.argsort(distance)
        distance_sorted = distance[sorted_indices]
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, (col, label) in enumerate(zip(error_columns, labels)):
            if col not in self.df.columns:
                continue
                
            error = self.df[col].values
            error_sorted = error[sorted_indices]
            
            if smooth and len(distance_sorted) > 10:
                try:
                    # 分箱平均
                    bins = np.linspace(distance_sorted.min(), distance_sorted.max(), 50)
                    bin_indices = np.digitize(distance_sorted, bins)
                    
                    bin_centers = []
                    bin_means = []
                    
                    for bin_idx in range(1, len(bins)):
                        mask = bin_indices == bin_idx
                        if mask.sum() > 0:
                            bin_centers.append(bins[bin_idx-1] + (bins[bin_idx] - bins[bin_idx-1])/2)
                            bin_means.append(error_sorted[mask].mean())
                    
                    if len(bin_centers) > 3:
                        spl = make_interp_spline(bin_centers, bin_means, k=min(3, len(bin_centers)-1))
                        dist_fine = np.linspace(min(bin_centers), max(bin_centers), 300)
                        error_fine = spl(dist_fine)
                        
                        ax.plot(dist_fine, error_fine, label=label, linewidth=2, color=colors[i % len(colors)])
                    else:
                        ax.plot(bin_centers, bin_means, label=label, linewidth=2, marker='o', color=colors[i % len(colors)])
                    
                    ax.scatter(distance_sorted, error_sorted, alpha=0.2, s=10, color=colors[i % len(colors)])
                except:
                    ax.scatter(distance_sorted, error_sorted, label=label, alpha=0.5, s=20, color=colors[i % len(colors)])
            else:
                ax.scatter(distance_sorted, error_sorted, label=label, alpha=0.5, s=20, color=colors[i % len(colors)])
        
        # 添加阈值线
        if show_threshold and threshold_func is not None:
            dist_range = np.linspace(distance.min(), distance.max(), 100)
            thresholds_pos = [threshold_func(d) for d in dist_range]
            thresholds_neg = [-threshold_func(d) for d in dist_range]
            
            ax.plot(dist_range, thresholds_pos, '--', color='red', alpha=0.6, linewidth=2, label='阈值上限')
            ax.plot(dist_range, thresholds_neg, '--', color='red', alpha=0.6, linewidth=2, label='阈值下限')
        
        if ylim:
            ax.set_ylim(ylim)
            
        ax.set_xlabel('距离 (m)', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        if filename:
            filepath = self.output_dir / filename
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            return str(filepath)
        else:
            plt.tight_layout()
            return fig
    
    def plot_comparison(self,
                       gt_column: str,
                       algo_column: str,
                       title: str,
                       ylabel: str,
                       filename: Optional[str] = None,
                       vs_time: bool = True,
                       ylim: Optional[Tuple[float, float]] = None) -> any:
        """
        绘制真实值与算法输出对比图
        
        Args:
            gt_column: 真实值列名
            algo_column: 算法输出列名
            title: 图表标题
            ylabel: Y轴标签
            filename: 保存文件名 (若为None则不保存，返回Figure对象)
            vs_time: True为时间维度，False为距离维度
            ylim: Y轴范围 (min, max)
            
        Returns:
            保存的文件路径(str) 或 Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if vs_time:
            x = self.df['timestamp'].values
            xlabel = '时间 (s)'
        else:
            x = self.df['gt_distance'].values
            xlabel = '距离 (m)'
            # 按距离排序
            sorted_indices = np.argsort(x)
            x = x[sorted_indices]
        
        gt_values = self.df[gt_column].values
        algo_values = self.df[algo_column].values
        
        if not vs_time:
            gt_values = gt_values[sorted_indices]
            algo_values = algo_values[sorted_indices]
        
        ax.plot(x, gt_values, label='真实值 (Ground Truth)', linewidth=2, color='#2ca02c')
        ax.plot(x, algo_values, label='算法输出 (Algorithm)', linewidth=2, color='#ff7f0e', alpha=0.8)
        
        if ylim:
            ax.set_ylim(ylim)
            
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        if filename:
            filepath = self.output_dir / filename
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            return str(filepath)
        else:
            plt.tight_layout()
            return fig
    
    def generate_all_plots(self) -> List[str]:
        """
        生成所有标准图表
        
        Returns:
            生成的文件路径列表
        """
        filepaths = []
        
        print("正在生成图表...")
        
        # 1. 距离误差 vs 时间
        print("  - 距离误差 vs 时间")
        filepaths.append(self.plot_error_vs_time(
            error_columns=['error_distance'],
            labels=['距离误差'],
            title='距离误差随时间变化',
            ylabel='误差 (m)',
            filename='error_distance_vs_time.png',
            show_threshold=True,
            threshold_func=lambda d: 0.5 + 0.002 * d
        ))
        
        # 2. 距离误差 vs 距离
        print("  - 距离误差 vs 距离")
        filepaths.append(self.plot_error_vs_distance(
            error_columns=['error_distance'],
            labels=['距离误差'],
            title='距离误差随距离变化',
            ylabel='误差 (m)',
            filename='error_distance_vs_distance.png',
            show_threshold=True,
            threshold_func=lambda d: 0.5 + 0.002 * d
        ))
        
        # 3. 纵向误差 vs 时间
        print("  - 纵向误差 vs 时间")
        filepaths.append(self.plot_error_vs_time(
            error_columns=['error_longitudinal'],
            labels=['纵向误差'],
            title='纵向误差随时间变化',
            ylabel='误差 (m)',
            filename='error_longitudinal_vs_time.png',
            show_threshold=True,
            threshold_func=lambda d: 0.5 + 0.002 * d
        ))
        
        # 4. 纵向误差 vs 距离
        print("  - 纵向误差 vs 距离")
        filepaths.append(self.plot_error_vs_distance(
            error_columns=['error_longitudinal'],
            labels=['纵向误差'],
            title='纵向误差随距离变化',
            ylabel='误差 (m)',
            filename='error_longitudinal_vs_distance.png',
            show_threshold=True,
            threshold_func=lambda d: 0.5 + 0.002 * d
        ))
        
        # 5. 侧向误差 vs 时间
        print("  - 侧向误差 vs 时间")
        filepaths.append(self.plot_error_vs_time(
            error_columns=['error_lateral'],
            labels=['侧向误差'],
            title='侧向误差随时间变化',
            ylabel='误差 (m)',
            filename='error_lateral_vs_time.png',
            show_threshold=True,
            threshold_func=lambda d: 0.5 + 0.002 * d
        ))
        
        # 6. 侧向误差 vs 距离
        print("  - 侧向误差 vs 距离")
        filepaths.append(self.plot_error_vs_distance(
            error_columns=['error_lateral'],
            labels=['侧向误差'],
            title='侧向误差随距离变化',
            ylabel='误差 (m)',
            filename='error_lateral_vs_distance.png',
            show_threshold=True,
            threshold_func=lambda d: 0.5 + 0.002 * d
        ))
        
        # 7. 高度误差 vs 时间
        print("  - 高度误差 vs 时间")
        filepaths.append(self.plot_error_vs_time(
            error_columns=['error_height'],
            labels=['高度误差'],
            title='高度误差随时间变化',
            ylabel='误差 (m)',
            filename='error_height_vs_time.png',
            show_threshold=True,
            threshold_func=lambda d: 0.5 + 0.002 * d
        ))
        
        # 8. 高度误差 vs 距离
        print("  - 高度误差 vs 距离")
        filepaths.append(self.plot_error_vs_distance(
            error_columns=['error_height'],
            labels=['高度误差'],
            title='高度误差随距离变化',
            ylabel='误差 (m)',
            filename='error_height_vs_distance.png',
            show_threshold=True,
            threshold_func=lambda d: 0.5 + 0.002 * d
        ))
        
        # 9. 航向角误差 vs 时间
        print("  - 航向角误差 vs 时间")
        filepaths.append(self.plot_error_vs_time(
            error_columns=['error_heading_deg'],
            labels=['航向角误差'],
            title='航向角误差随时间变化',
            ylabel='误差 (°)',
            filename='error_heading_vs_time.png',
            show_threshold=True,
            threshold_func=lambda d: 1.0
        ))
        
        # 10. 航向角误差 vs 距离
        print("  - 航向角误差 vs 距离")
        filepaths.append(self.plot_error_vs_distance(
            error_columns=['error_heading_deg'],
            labels=['航向角误差'],
            title='航向角误差随距离变化',
            ylabel='误差 (°)',
            filename='error_heading_vs_distance.png',
            show_threshold=True,
            threshold_func=lambda d: 1.0
        ))
        
        # 11. 综合误差对比 vs 时间
        print("  - 综合误差对比 vs 时间")
        filepaths.append(self.plot_error_vs_time(
            error_columns=['error_distance', 'error_lateral', 'error_longitudinal', 'error_height'],
            labels=['距离误差', '侧向误差', '纵向误差', '高度误差'],
            title='各维度误差随时间变化对比',
            ylabel='误差 (m)',
            filename='error_comprehensive_vs_time.png',
            smooth=True
        ))
        
        # 12. 距离对比图
        print("  - 距离真实值vs算法输出")
        filepaths.append(self.plot_comparison(
            gt_column='gt_distance',
            algo_column='algo_distance',
            title='距离: 真实值 vs 算法输出',
            ylabel='距离 (m)',
            filename='comparison_distance_vs_time.png',
            vs_time=True
        ))
        
        print(f"✓ 成功生成 {len(filepaths)} 张图表")
        
        return filepaths
