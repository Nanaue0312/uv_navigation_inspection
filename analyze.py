#!/usr/bin/env python3
"""
紫外导航算法性能分析工具 - 主程序
用于批量分析仿真数据并生成报告
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data_loader import DataLoader
from src.statistics_analyzer import StatisticsAnalyzer
from src.visualizer import Visualizer
from src.report_generator import ReportGenerator


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="紫外导航算法性能分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 分析单个数据文件
  python analyze.py data/closed_loop_20251122_154229/analysis_data.json
  
  # 分析整个数据目录
  python analyze.py data/closed_loop_20251122_154229
  
  # 指定输出目录
  python analyze.py data/closed_loop_20251122_154229 -o reports/my_report
  
  # 不生成图表（仅文本报告）
  python analyze.py data/closed_loop_20251122_154229 --no-plots
        """
    )
    
    parser.add_argument(
        'data_path',
        type=str,
        help='数据文件路径(analysis_data.json)或包含该文件的目录'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='reports',
        help='输出目录 (默认: reports)'
    )
    
    parser.add_argument(
        '--no-plots',
        action='store_true',
        help='不生成图表，仅生成文本报告'
    )
    
    parser.add_argument(
        '--format',
        choices=['text', 'html', 'json', 'all'],
        default='all',
        help='报告格式 (默认: all)'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("紫外导航算法性能分析工具".center(80))
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 加载数据
    print("步骤 1/5: 加载数据...")
    print("-" * 80)
    
    try:
        loader = DataLoader(args.data_path)
        if not loader.load():
            print("✗ 数据加载失败")
            return 1
    except Exception as e:
        print(f"✗ 错误: {e}")
        return 1
    
    print()
    
    # 2. 统计分析
    print("步骤 2/5: 统计分析...")
    print("-" * 80)
    
    df = loader.get_frames_dataframe()
    analyzer = StatisticsAnalyzer(df)
    
    try:
        report_data = analyzer.generate_comprehensive_report()
        print("✓ 统计分析完成")
        
        # 打印简要统计
        summary = report_data['summary']
        print(f"  - 分析帧数: {summary['total_frames']}")
        print(f"  - 时长: {summary['duration_seconds']:.2f}秒")
        print(f"  - 距离范围: {summary['distance_range']['min']:.2f}m ~ {summary['distance_range']['max']:.2f}m")
    except Exception as e:
        print(f"✗ 统计分析失败: {e}")
        return 1
    
    print()
    
    # 3. 生成图表
    image_paths = []
    if not args.no_plots:
        print("步骤 3/5: 生成图表...")
        print("-" * 80)
        
        try:
            visualizer = Visualizer(df, output_dir=args.output)
            image_paths = visualizer.generate_all_plots()
        except Exception as e:
            print(f"✗ 图表生成失败: {e}")
            print("  继续生成文本报告...")
    else:
        print("步骤 3/5: 跳过图表生成")
    
    print()
    
    # 4. 生成报告
    print("步骤 4/5: 生成报告...")
    print("-" * 80)
    
    try:
        generator = ReportGenerator(output_dir=args.output)
        metadata = loader.get_metadata()
        
        generated_files = []
        
        # 文本报告
        if args.format in ['text', 'all']:
            text_file = generator.generate_text_report(
                report_data, 
                metadata,
                filename="analysis_report.txt"
            )
            generated_files.append(text_file)
            print(f"✓ 文本报告: {text_file}")
        
        # HTML报告
        if args.format in ['html', 'all']:
            html_file = generator.generate_html_report(
                report_data,
                metadata,
                image_paths=image_paths,
                filename="analysis_report.html"
            )
            generated_files.append(html_file)
            print(f"✓ HTML报告: {html_file}")
        
        # JSON报告
        if args.format in ['json', 'all']:
            json_file = generator.save_json_report(
                report_data,
                filename="analysis_report.json"
            )
            generated_files.append(json_file)
            print(f"✓ JSON报告: {json_file}")
        
    except Exception as e:
        print(f"✗ 报告生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    
    # 5. 完成
    print("步骤 5/5: 完成")
    print("-" * 80)
    print(f"✓ 分析完成！共生成 {len(generated_files)} 个报告文件")
    print(f"✓ 输出目录: {args.output}")
    
    if image_paths:
        print(f"✓ 图表数量: {len(image_paths)}")
    
    print()
    print("=" * 80)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
