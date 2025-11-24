import pandas as pd
import numpy as np
from typing import List, Dict, Any

def process_frames(frames: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process a list of frame dictionaries into a Pandas DataFrame.
    Extracts relevant metrics for analysis.
    """
    data_list = []
    for frame in frames:
        timestamp = frame.get('timestamp')
        
        # Ground Truth
        gt = frame.get('ground_truth', {})
        gt_rel = gt.get('relative_to_ship', {})
        gt_att = gt.get('attitude', {})
        
        gt_dist = gt_rel.get('distance')
        gt_lat = gt_rel.get('x_lateral')
        gt_lon = gt_rel.get('y_longitudinal')
        gt_h = gt_rel.get('z_height')
        gt_heading = gt_att.get('yaw')
        
        # Algorithm Output
        algo = frame.get('algorithm_output', {})
        algo_dist = algo.get('distance')
        algo_lat = algo.get('x_lateral')
        algo_lon = algo.get('y_longitudinal')
        algo_h = algo.get('z_height')
        algo_heading = algo.get('heading')
        
        # Errors
        err = frame.get('errors', {})
        dist_err = err.get('distance_error')
        lat_err = err.get('lateral_error')
        lon_err = err.get('longitudinal_error')
        h_err = err.get('height_error')
        
        # Handle heading error: prefer degrees, fallback to rad->deg
        heading_err = err.get('heading_error_deg')
        if heading_err is None:
            heading_err_rad = err.get('heading_error_rad')
            if heading_err_rad is not None:
                heading_err = np.degrees(heading_err_rad)
            else:
                heading_err = 0.0

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
            'gt_heading': gt_heading,
            'algo_heading': algo_heading,
            'heading_error': heading_err
        })
    
    return pd.DataFrame(data_list)
