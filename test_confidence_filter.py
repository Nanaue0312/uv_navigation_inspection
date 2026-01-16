"""
测试低置信度过滤功能是否有效
"""
import json
import pandas as pd
from src.processor import process_frames

def test_confidence_filter():
    print("=" * 60)
    print("测试低置信度过滤功能")
    print("=" * 60)
    
    # 创建测试数据，包含不同置信度的数据点
    test_frames = [
        {
            'timestamp': 1.0,
            'ground_truth': {
                'relative_to_ship': {
                    'distance': 100.0,
                    'dx_ned': 10.0,
                    'dy_ned': 5.0,
                    'dz_ned': -50.0,
                    'dyaw': 2.0,
                    'dpitch': -3.0
                },
                'attitude': {'yaw': 0.0, 'pitch': 0.0}
            },
            'algorithm_output': {
                'distance': 98.0,
                'dx_ned': 9.5,
                'dy_ned': 5.2,
                'dz_ned': -48.0,
                'dyaw': 2.1,
                'dpitch': -2.9,
                'confidence': 0.9  # 高置信度
            },
            'errors': {
                'distance_error': -2.0,
                'lateral_error': -0.5,
                'longitudinal_error': 0.2,
                'height_error': 2.0,
                'dyaw_error': 0.1,
                'dpitch_error': 0.1,
                'position_error_3d': 2.1
            },
            'image_path': 'test_high_conf.jpg'
        },
        {
            'timestamp': 2.0,
            'ground_truth': {
                'relative_to_ship': {
                    'distance': 100.0,
                    'dx_ned': 10.0,
                    'dy_ned': 5.0,
                    'dz_ned': -50.0,
                    'dyaw': 2.0,
                    'dpitch': -3.0
                },
                'attitude': {'yaw': 0.0, 'pitch': 0.0}
            },
            'algorithm_output': {
                'distance': 50.0,  # 错误的距离
                'dx_ned': 15.0,
                'dy_ned': 8.0,
                'dz_ned': -30.0,
                'dyaw': 5.0,
                'dpitch': -1.0,
                'confidence': 0.3  # 低置信度 < 0.5
            },
            'errors': {
                'distance_error': -50.0,
                'lateral_error': 5.0,
                'longitudinal_error': 3.0,
                'height_error': 20.0,
                'dyaw_error': 3.0,
                'dpitch_error': 2.0,
                'position_error_3d': 20.6
            },
            'image_path': 'test_low_conf.jpg'
        },
        {
            'timestamp': 3.0,
            'ground_truth': {
                'relative_to_ship': {
                    'distance': 100.0,
                    'dx_ned': 10.0,
                    'dy_ned': 5.0,
                    'dz_ned': -50.0,
                    'dyaw': 2.0,
                    'dpitch': -3.0
                },
                'attitude': {'yaw': 0.0, 'pitch': 0.0}
            },
            'algorithm_output': {
                'distance': 0.0,  # 异常的零距离
                'dx_ned': 0.0,
                'dy_ned': 0.0,
                'dz_ned': 0.0,
                'dyaw': 0.0,
                'dpitch': 0.0,
                'confidence': 0.8  # 置信度虽高，但距离为0
            },
            'errors': {
                'distance_error': -100.0,
                'lateral_error': -10.0,
                'longitudinal_error': -5.0,
                'height_error': 50.0,
                'dyaw_error': -2.0,
                'dpitch_error': 3.0,
                'position_error_3d': 51.2
            },
            'image_path': 'test_zero_dist.jpg'
        },
        {
            'timestamp': 4.0,
            'ground_truth': {
                'relative_to_ship': {
                    'distance': 100.0,
                    'dx_ned': 10.0,
                    'dy_ned': 5.0,
                    'dz_ned': -50.0,
                    'dyaw': 2.0,
                    'dpitch': -3.0
                },
                'attitude': {'yaw': 0.0, 'pitch': 0.0}
            },
            'algorithm_output': {
                'distance': 102.0,
                'dx_ned': 10.5,
                'dy_ned': 4.8,
                'dz_ned': -51.0,
                'dyaw': 1.9,
                'dpitch': -3.1,
                'confidence': 0.85  # 高置信度
            },
            'errors': {
                'distance_error': 2.0,
                'lateral_error': 0.5,
                'longitudinal_error': -0.2,
                'height_error': -1.0,
                'dyaw_error': -0.1,
                'dpitch_error': -0.1,
                'position_error_3d': 1.1
            },
            'image_path': 'test_high_conf2.jpg'
        }
    ]
    
    # 处理数据
    df = process_frames(test_frames)
    
    print(f"\n原始数据框架（共 {len(df)} 条记录）：")
    print(df[['image_name', 'algo_confidence', 'algo_distance']].to_string(index=False))
    
    # 应用过滤条件（模拟app.py中的逻辑）
    print("\n" + "=" * 60)
    print("应用过滤条件: algo_confidence > 0.5 AND algo_distance > 0.1")
    print("=" * 60)
    
    if 'algo_confidence' in df.columns:
        initial_len = len(df)
        mask = (df['algo_confidence'] > 0.5) & (df['algo_distance'] > 0.1)
        filtered_df = df[mask]
        filtered_len = len(filtered_df)
        
        print(f"\n过滤前: {initial_len} 条")
        print(f"过滤后: {filtered_len} 条")
        print(f"已过滤: {initial_len - filtered_len} 条")
        
        print(f"\n过滤后的数据：")
        print(filtered_df[['image_name', 'algo_confidence', 'algo_distance']].to_string(index=False))
        
        # 检查被过滤掉的数据
        removed_mask = ~mask
        removed_df = df[removed_mask]
        if len(removed_df) > 0:
            print(f"\n被过滤掉的数据（共 {len(removed_df)} 条）：")
            for idx, row in removed_df.iterrows():
                reason = []
                if row['algo_confidence'] <= 0.5:
                    reason.append(f"置信度={row['algo_confidence']:.2f} <= 0.5")
                if row['algo_distance'] <= 0.1:
                    reason.append(f"距离={row['algo_distance']:.2f} <= 0.1")
                print(f"  - {row['image_name']}: {', '.join(reason)}")
        
        # 验证结果
        print("\n" + "=" * 60)
        print("验证结果:")
        print("=" * 60)
        
        # 预期应该过滤掉2条：
        # 1. test_low_conf.jpg (confidence=0.3 < 0.5)
        # 2. test_zero_dist.jpg (distance=0.0 < 0.1)
        expected_removed = 2
        actual_removed = initial_len - filtered_len
        
        if actual_removed == expected_removed:
            print(f"✅ 过滤功能正常！预期过滤 {expected_removed} 条，实际过滤 {actual_removed} 条")
            
            # 验证被保留的数据
            remaining_names = set(filtered_df['image_name'].tolist())
            expected_remaining = {'test_high_conf.jpg', 'test_high_conf2.jpg'}
            
            if remaining_names == expected_remaining:
                print(f"✅ 保留的数据正确！")
                return True
            else:
                print(f"❌ 保留的数据不正确！")
                print(f"   预期保留: {expected_remaining}")
                print(f"   实际保留: {remaining_names}")
                return False
        else:
            print(f"❌ 过滤功能异常！预期过滤 {expected_removed} 条，实际过滤 {actual_removed} 条")
            return False
    else:
        print("❌ 错误: DataFrame 中没有 'algo_confidence' 列！")
        return False

if __name__ == '__main__':
    success = test_confidence_filter()
    print("\n" + "=" * 60)
    if success:
        print("测试通过 ✅")
    else:
        print("测试失败 ❌")
    print("=" * 60)
