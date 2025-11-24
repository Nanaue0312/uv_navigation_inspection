"""
报告生成模块
负责生成文本和HTML格式的分析报告
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_text_report(self, 
                            report_data: Dict,
                            metadata: Dict,
                            filename: str = "analysis_report.txt") -> str:
        """
        生成文本格式报告
        
        Args:
            report_data: 统计分析数据
            metadata: 元数据
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        lines = []
        lines.append("=" * 100)
        lines.append("紫外导航算法性能分析报告".center(100))
        lines.append("=" * 100)
        lines.append("")
        lines.append(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append("")
        
        # 仿真信息
        lines.append("【仿真信息】")
        lines.append(f"仿真ID: {metadata.get('simulation_id', 'N/A')}")
        lines.append(f"软件版本: {metadata.get('software_version', 'N/A')}")
        lines.append(f"数据生成时间: {metadata.get('generation_time', 'N/A')}")
        
        sim_config = metadata.get('simulation_config', {})
        lines.append(f"配置帧率: {sim_config.get('frame_rate', 'N/A')} fps")
        lines.append(f"配置时长: {sim_config.get('duration_seconds', 'N/A')} 秒")
        
        scenario = metadata.get('scenario', {})
        lines.append(f"下滑道: {scenario.get('glide_path', 'N/A')}")
        lines.append(f"海况: {scenario.get('sea_state', 'N/A')}")
        lines.append("")
        
        # 基本统计
        summary = report_data.get('summary', {})
        lines.append("【基本统计】")
        lines.append(f"实际分析帧数: {summary.get('total_frames', 0)}")
        lines.append(f"实际时长: {summary.get('duration_seconds', 0):.2f} 秒")
        
        dist_range = summary.get('distance_range', {})
        lines.append(f"距离范围: {dist_range.get('min', 0):.2f}m ~ {dist_range.get('max', 0):.2f}m")
        lines.append(f"平均距离: {dist_range.get('mean', 0):.2f}m")
        lines.append("")
        
        # 指标精度符合率
        lines.append("=" * 100)
        lines.append("【指标精度符合率】")
        lines.append("=" * 100)
        lines.append("")
        
        # 1. 距离
        lines.append("1. 紫外距离")
        lines.append("-" * 100)
        distance_data = report_data.get('distance', {}).get('standard_ranges', {})
        for range_name, stats in distance_data.items():
            rate = stats['compliance_rate'] * 100
            total = stats['total_points']
            compliant = stats['compliant_points']
            lines.append(f"   {range_name}内，{rate:.1f}%的点({compliant}/{total})满足(0.5+0.2%×D)的指标精度要求")
            lines.append(f"      平均误差: {stats['mean_error']:.4f}m, 最大误差: {stats['max_error']:.4f}m")
        
        if 'tracking' in report_data.get('distance', {}):
            tracking_data = report_data['distance']['tracking']
            for range_name, stats in tracking_data.items():
                rate = stats['compliance_rate'] * 100
                total = stats['total_points']
                compliant = stats['compliant_points']
                lines.append(f"   跟踪过程中({range_name})，{rate:.1f}%的点({compliant}/{total})满足(0.5+0.2%×D)的指标精度要求")
        lines.append("")
        
        # 2. 纵向
        lines.append("2. 紫外纵向")
        lines.append("-" * 100)
        longitudinal_data = report_data.get('longitudinal', {}).get('standard_ranges', {})
        for range_name, stats in longitudinal_data.items():
            rate = stats['compliance_rate'] * 100
            total = stats['total_points']
            compliant = stats['compliant_points']
            lines.append(f"   {range_name}内，{rate:.1f}%的点({compliant}/{total})满足(0.5+0.2%×D)的指标精度要求")
            lines.append(f"      平均误差: {stats['mean_error']:.4f}m, 最大误差: {stats['max_error']:.4f}m")
        lines.append("")
        
        # 3. 侧向
        lines.append("3. 紫外侧向")
        lines.append("-" * 100)
        lateral_data = report_data.get('lateral', {}).get('standard_ranges', {})
        for range_name, stats in lateral_data.items():
            rate = stats['compliance_rate'] * 100
            total = stats['total_points']
            compliant = stats['compliant_points']
            lines.append(f"   {range_name}内，{rate:.1f}%的点({compliant}/{total})满足(0.5+0.2%×D)的指标精度要求")
            lines.append(f"      平均误差: {stats['mean_error']:.4f}m, 最大误差: {stats['max_error']:.4f}m")
        lines.append("")
        
        # 4. 高度
        lines.append("4. 紫外高度")
        lines.append("-" * 100)
        height_data = report_data.get('height', {}).get('standard_ranges', {})
        for range_name, stats in height_data.items():
            rate = stats['compliance_rate'] * 100
            total = stats['total_points']
            compliant = stats['compliant_points']
            lines.append(f"   {range_name}内，{rate:.1f}%的点({compliant}/{total})满足(0.5+0.2%×D)的指标精度要求")
            lines.append(f"      平均误差: {stats['mean_error']:.4f}m, 最大误差: {stats['max_error']:.4f}m")
        lines.append("")
        
        # 5. 航向角
        lines.append("5. 紫外航向角")
        lines.append("-" * 100)
        heading_data = report_data.get('heading', {}).get('standard_ranges', {})
        for range_name, stats in heading_data.items():
            rate = stats['compliance_rate'] * 100
            total = stats['total_points']
            compliant = stats['compliant_points']
            lines.append(f"   {range_name}内，{rate:.1f}%的点({compliant}/{total})满足1°的指标精度要求")
            lines.append(f"      平均误差: {stats['mean_error']:.4f}°, 最大误差: {stats['max_error']:.4f}°")
        
        if 'tracking' in report_data.get('heading', {}):
            tracking_data = report_data['heading']['tracking']
            for range_name, stats in tracking_data.items():
                rate = stats['compliance_rate'] * 100
                total = stats['total_points']
                compliant = stats['compliant_points']
                lines.append(f"   跟踪过程中({range_name})，{rate:.1f}%的点({compliant}/{total})满足1°的指标精度要求")
        lines.append("")
        
        # 总体误差统计
        lines.append("=" * 100)
        lines.append("【总体误差统计】")
        lines.append("=" * 100)
        lines.append("")
        
        overall = summary.get('overall_errors', {})
        
        for metric_name, metric_label in [
            ('distance', '距离误差'),
            ('lateral', '侧向误差'),
            ('longitudinal', '纵向误差'),
            ('height', '高度误差'),
            ('heading', '航向角误差')
        ]:
            metric = overall.get(metric_name, {})
            unit = '°' if metric_name == 'heading' else 'm'
            lines.append(f"{metric_label}:")
            lines.append(f"   平均值(Mean):     {metric.get('mean', 0):.4f}{unit}")
            lines.append(f"   标准差(Std):      {metric.get('std', 0):.4f}{unit}")
            lines.append(f"   最大值(Max):      {metric.get('max', 0):.4f}{unit}")
            lines.append(f"   均方根(RMSE):     {metric.get('rmse', 0):.4f}{unit}")
            lines.append("")
        
        lines.append("=" * 100)
        lines.append("报告结束".center(100))
        lines.append("=" * 100)
        
        # 保存文件
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return str(filepath)
    
    def generate_html_report(self,
                            report_data: Dict,
                            metadata: Dict,
                            image_paths: List[str] = None,
                            filename: str = "analysis_report.html") -> str:
        """
        生成HTML格式报告
        
        Args:
            report_data: 统计分析数据
            metadata: 元数据
            image_paths: 图表文件路径列表
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        html_lines = []
        
        # HTML头部
        html_lines.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>紫外导航算法性能分析报告</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2980b9;
            margin-top: 30px;
            border-left: 5px solid #3498db;
            padding-left: 10px;
        }
        h3 {
            color: #34495e;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .info-box {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .metric-good {
            color: #27ae60;
            font-weight: bold;
        }
        .metric-warning {
            color: #f39c12;
            font-weight: bold;
        }
        .metric-bad {
            color: #e74c3c;
            font-weight: bold;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 10px 0;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary-card h4 {
            margin-top: 0;
            color: #2980b9;
        }
        .timestamp {
            text-align: right;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>紫外导航算法性能分析报告</h1>
        <div class="timestamp">生成时间: """ + datetime.now().strftime('%Y年%m月%d日 %H:%M:%S') + """</div>
""")
        
        # 仿真信息
        html_lines.append("""
        <h2>1. 仿真信息</h2>
        <div class="info-box">
""")
        html_lines.append(f"            <p><strong>仿真ID:</strong> {metadata.get('simulation_id', 'N/A')}</p>")
        html_lines.append(f"            <p><strong>软件版本:</strong> {metadata.get('software_version', 'N/A')}</p>")
        html_lines.append(f"            <p><strong>数据生成时间:</strong> {metadata.get('generation_time', 'N/A')}</p>")
        
        sim_config = metadata.get('simulation_config', {})
        html_lines.append(f"            <p><strong>配置帧率:</strong> {sim_config.get('frame_rate', 'N/A')} fps</p>")
        html_lines.append(f"            <p><strong>配置时长:</strong> {sim_config.get('duration_seconds', 'N/A')} 秒</p>")
        
        scenario = metadata.get('scenario', {})
        html_lines.append(f"            <p><strong>下滑道:</strong> {scenario.get('glide_path', 'N/A')}</p>")
        html_lines.append(f"            <p><strong>海况:</strong> {scenario.get('sea_state', 'N/A')}</p>")
        html_lines.append("""        </div>""")
        
        # 基本统计
        summary = report_data.get('summary', {})
        html_lines.append("""
        <h2>2. 基本统计</h2>
        <div class="summary-grid">
""")
        
        html_lines.append(f"""
            <div class="summary-card">
                <h4>分析帧数</h4>
                <p style="font-size: 2em; margin: 10px 0; color: #3498db;">{summary.get('total_frames', 0)}</p>
            </div>
""")
        
        html_lines.append(f"""
            <div class="summary-card">
                <h4>实际时长</h4>
                <p style="font-size: 2em; margin: 10px 0; color: #3498db;">{summary.get('duration_seconds', 0):.2f}s</p>
            </div>
""")
        
        dist_range = summary.get('distance_range', {})
        html_lines.append(f"""
            <div class="summary-card">
                <h4>距离范围</h4>
                <p style="font-size: 1.5em; margin: 10px 0; color: #3498db;">{dist_range.get('min', 0):.1f}m ~ {dist_range.get('max', 0):.1f}m</p>
            </div>
""")
        
        html_lines.append(f"""
            <div class="summary-card">
                <h4>平均距离</h4>
                <p style="font-size: 2em; margin: 10px 0; color: #3498db;">{dist_range.get('mean', 0):.2f}m</p>
            </div>
""")
        
        html_lines.append("""        </div>""")
        
        # 指标精度符合率
        html_lines.append("""
        <h2>3. 指标精度符合率</h2>
""")
        
        def add_compliance_table(title, data_key, threshold_text):
            html_lines.append(f"""
        <h3>{title}</h3>
        <p>精度要求: <strong>{threshold_text}</strong></p>
        <table>
            <tr>
                <th>距离范围</th>
                <th>总点数</th>
                <th>符合点数</th>
                <th>符合率</th>
                <th>平均误差</th>
                <th>最大误差</th>
            </tr>
""")
            data = report_data.get(data_key, {}).get('standard_ranges', {})
            for range_name, stats in data.items():
                rate = stats['compliance_rate'] * 100
                rate_class = 'metric-good' if rate >= 90 else ('metric-warning' if rate >= 70 else 'metric-bad')
                unit = '°' if data_key == 'heading' else 'm'
                html_lines.append(f"""
            <tr>
                <td>{range_name}</td>
                <td>{stats['total_points']}</td>
                <td>{stats['compliant_points']}</td>
                <td class="{rate_class}">{rate:.1f}%</td>
                <td>{stats['mean_error']:.4f}{unit}</td>
                <td>{stats['max_error']:.4f}{unit}</td>
            </tr>
""")
            
            # 添加跟踪过程数据（如果有）
            if 'tracking' in report_data.get(data_key, {}):
                tracking_data = report_data[data_key]['tracking']
                for range_name, stats in tracking_data.items():
                    rate = stats['compliance_rate'] * 100
                    rate_class = 'metric-good' if rate >= 90 else ('metric-warning' if rate >= 70 else 'metric-bad')
                    unit = '°' if data_key == 'heading' else 'm'
                    html_lines.append(f"""
            <tr style="background-color: #e8f4f8;">
                <td>跟踪过程({range_name})</td>
                <td>{stats['total_points']}</td>
                <td>{stats['compliant_points']}</td>
                <td class="{rate_class}">{rate:.1f}%</td>
                <td>{stats['mean_error']:.4f}{unit}</td>
                <td>{stats['max_error']:.4f}{unit}</td>
            </tr>
""")
            
            html_lines.append("""        </table>""")
        
        add_compliance_table("3.1 紫外距离", "distance", "(0.5 + 0.2% × D) 米")
        add_compliance_table("3.2 紫外纵向", "longitudinal", "(0.5 + 0.2% × D) 米")
        add_compliance_table("3.3 紫外侧向", "lateral", "(0.5 + 0.2% × D) 米")
        add_compliance_table("3.4 紫外高度", "height", "(0.5 + 0.2% × D) 米")
        add_compliance_table("3.5 紫外航向角", "heading", "1°")
        
        # 总体误差统计
        html_lines.append("""
        <h2>4. 总体误差统计</h2>
        <table>
            <tr>
                <th>误差类型</th>
                <th>平均值(Mean)</th>
                <th>标准差(Std)</th>
                <th>最大值(Max)</th>
                <th>均方根(RMSE)</th>
            </tr>
""")
        
        overall = summary.get('overall_errors', {})
        for metric_name, metric_label in [
            ('distance', '距离误差'),
            ('lateral', '侧向误差'),
            ('longitudinal', '纵向误差'),
            ('height', '高度误差'),
            ('heading', '航向角误差')
        ]:
            metric = overall.get(metric_name, {})
            unit = '°' if metric_name == 'heading' else 'm'
            html_lines.append(f"""
            <tr>
                <td><strong>{metric_label}</strong></td>
                <td>{metric.get('mean', 0):.4f}{unit}</td>
                <td>{metric.get('std', 0):.4f}{unit}</td>
                <td>{metric.get('max', 0):.4f}{unit}</td>
                <td>{metric.get('rmse', 0):.4f}{unit}</td>
            </tr>
""")
        
        html_lines.append("""        </table>""")
        
        # 添加图表
        if image_paths:
            html_lines.append("""
        <h2>5. 误差分析图表</h2>
""")
            for img_path in image_paths:
                img_name = Path(img_path).name
                # 使用相对路径
                rel_path = Path(img_path).name
                html_lines.append(f"""
        <div class="chart-container">
            <img src="{rel_path}" alt="{img_name}">
        </div>
""")
        
        # HTML尾部
        html_lines.append("""
    </div>
</body>
</html>
""")
        
        # 保存文件
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_lines))
        
        return str(filepath)
    
    def save_json_report(self, report_data: Dict, filename: str = "analysis_report.json") -> str:
        """
        保存JSON格式的报告数据
        
        Args:
            report_data: 报告数据
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
