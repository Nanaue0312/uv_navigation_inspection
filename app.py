import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json5
import os
from pathlib import Path
from typing import Dict, List

st.set_page_config(page_title="紫外导航误差对比", layout="wide")

def load_csv(file) -> pd.DataFrame:
    try:
        df = pd.read_csv(file)
        # 标准化常见列名
        df = normalize_df_columns(df)
        return df
    except Exception as e:
        st.error(f"文件读取失败: {e}")
        return pd.DataFrame()

EXPECTED_COLUMNS = ["time", "x", "y", "z"]  # 基础位置列
OPTIONAL_METRIC_COLUMNS = [
    "dist",      # 距离 D (m)
    "lon",       # 纵向 (m)
    "lat",       # 侧向 (m)
    "alt",       # 高度 (m)
    "heading",   # 航向角 (deg)
    "speed"      # 速度 (m/s)
]

def validate_dataframe(df: pd.DataFrame, name: str) -> bool:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"{name} 缺少必要列: {missing}")
        return False
    return True

def compute_errors(alg_df: pd.DataFrame, sim_df: pd.DataFrame) -> pd.DataFrame:
    # 对齐时间列（内连接）
    base_cols = [c for c in EXPECTED_COLUMNS if c in alg_df.columns and c in sim_df.columns]
    merged = pd.merge(alg_df, sim_df, on="time", suffixes=("_alg", "_sim"))
    # 位置误差
    for axis in ["x", "y", "z"]:
        if f"{axis}_alg" in merged.columns and f"{axis}_sim" in merged.columns:
            merged[f"err_{axis}"] = merged[f"{axis}_alg"] - merged[f"{axis}_sim"]
    if all(f"err_{a}" in merged.columns for a in ["x", "y", "z"]):
        merged["err_norm"] = np.sqrt(merged[["err_x", "err_y", "err_z"]].pow(2).sum(axis=1))
    # 可选指标误差
    for opt in OPTIONAL_METRIC_COLUMNS:
        col_alg = f"{opt}_alg"
        col_sim = f"{opt}_sim"
        if col_alg in merged.columns and col_sim in merged.columns:
            merged[f"err_{opt}"] = merged[col_alg] - merged[col_sim]
    return merged


def normalize_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    """把常见替代列名映射到项目期望列名: timestamp->time, distance->dist, latitude->lat, longitude->lon 等"""
    if df is None or df.empty:
        return df
    rename_map = {}
    # 时间
    if 'timestamp' in df.columns and 'time' not in df.columns:
        rename_map['timestamp'] = 'time'
    # 距离
    if 'distance' in df.columns and 'dist' not in df.columns:
        rename_map['distance'] = 'dist'
    if 'dist' in df.columns and 'distance' not in df.columns:
        # 保留 dist
        pass
    # 纵向/侧向/高度
    if 'longitude' in df.columns and 'lon' not in df.columns:
        rename_map['longitude'] = 'lon'
    if 'latitude' in df.columns and 'lat' not in df.columns:
        rename_map['latitude'] = 'lat'
    if 'altitude' in df.columns and 'alt' not in df.columns:
        rename_map['altitude'] = 'alt'
    # heading / yaw
    if 'yaw' in df.columns and 'heading' not in df.columns:
        rename_map['yaw'] = 'heading'
    if 'speed_ms' in df.columns and 'speed' not in df.columns:
        rename_map['speed_ms'] = 'speed'
    if rename_map:
        try:
            df = df.rename(columns=rename_map)
        except Exception:
            pass
    return df

def summary_stats(err_df: pd.DataFrame) -> Dict[str, float]:
    stats = {}
    usable = [c for c in err_df.columns if c.startswith("err_")]
    for axis in usable:
        series = err_df[axis]
        stats[axis] = {
            "MAE": float(series.abs().mean()),
            "RMSE": float(np.sqrt((series ** 2).mean())),
            "MAX": float(series.abs().max())
        }
    return stats

def threshold_formula(distance_series: pd.Series) -> pd.Series:
    """(0.5 + 0.2% * D) 其中 D 为距离(m). 若缺失则使用常量 0.5."""
    if distance_series is None or distance_series.empty:
        return pd.Series([0.5])
    return 0.5 + 0.002 * distance_series

def percentage_within(errors: pd.Series, thresholds: pd.Series) -> float:
    if errors.empty or thresholds.empty:
        return 0.0
    comp = (errors.abs() <= thresholds).mean()
    return float(round(comp * 100, 2))

def compute_range_percentages(df: pd.DataFrame, err_col: str, dist_col: str = "dist_alg") -> Dict[str, float]:
    res = {"全程": 0.0, "≤1500m": 0.0, "≤800m": 0.0}
    if err_col not in df.columns:
        return res
    if dist_col not in df.columns:
        # 没有距离列则只做全程常量阈值 0.5
        thr = pd.Series([0.5] * len(df))
        res["全程"] = percentage_within(df[err_col], thr)
        return res
    dist_series = df[dist_col]
    thr_all = threshold_formula(dist_series)
    res["全程"] = percentage_within(df[err_col], thr_all)
    mask_1500 = dist_series <= 1500
    mask_800 = dist_series <= 800
    if mask_1500.any():
        res["≤1500m"] = percentage_within(df.loc[mask_1500, err_col], thr_all.loc[mask_1500])
    if mask_800.any():
        res["≤800m"] = percentage_within(df.loc[mask_800, err_col], thr_all.loc[mask_800])
    return res

def compute_fixed_threshold_percentage(df: pd.DataFrame, err_col: str, threshold: float, dist_col: str = "dist_alg") -> Dict[str, float]:
    res = {"全程": 0.0, "≤1500m": 0.0, "≤800m": 0.0}
    if err_col not in df.columns:
        return res
    dist_series = df[dist_col] if dist_col in df.columns else pd.Series([np.inf]*len(df))
    within = (df[err_col].abs() <= threshold)
    res["全程"] = float(round(within.mean()*100, 2))
    if dist_series is not None:
        mask_1500 = dist_series <= 1500
        mask_800 = dist_series <= 800
        if mask_1500.any():
            res["≤1500m"] = float(round(within[mask_1500].mean()*100, 2))
        if mask_800.any():
            res["≤800m"] = float(round(within[mask_800].mean()*100, 2))
    return res

def rolling_fit(series: pd.Series, window: int = 30) -> pd.Series:
    if series.empty:
        return series
    w = max(3, min(window, len(series)))
    return series.rolling(w, center=True, min_periods=1).mean()

def plot_with_threshold(df: pd.DataFrame, value_alg: str, value_sim: str, err_col: str, dist_col: str = "dist_alg", is_angle=False, is_speed=False):
    """生成两列对比 + 误差图 (含阈值 + 可选合格率注记)."""
    charts = []
    if value_alg in df.columns and value_sim in df.columns:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df['time'], y=df[value_sim], name='参考', mode='lines'))
        fig1.add_trace(go.Scatter(x=df['time'], y=df[value_alg], name='紫外', mode='lines'))
        fig1.update_layout(title=f"{value_alg.replace('_alg','')} 与参考对比", xaxis_title="时间 (s)")
        charts.append(fig1)
    return charts

def plot_error_with_threshold(df: pd.DataFrame, err_col: str, dist_col: str = "dist_alg", is_angle=False, is_speed=False, percents: Dict[str, float] = None, metric_label: str = ""):
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['time'], y=df[err_col], name='误差', mode='lines', line=dict(color='green', width=1)))
    fit = rolling_fit(df[err_col])
    fig2.add_trace(go.Scatter(x=df['time'], y=fit, name='拟合曲线', mode='lines', line=dict(color='black', width=2)))
    if dist_col in df.columns:
        dist_series = df[dist_col]
        if is_angle:
            upper = pd.Series([1.0]*len(df))
            lower = pd.Series([-1.0]*len(df))
        elif is_speed:
            upper = pd.Series([1.0]*len(df))
            lower = pd.Series([-1.0]*len(df))
        else:
            thr = threshold_formula(dist_series)
            upper = thr
            lower = -thr
        fig2.add_trace(go.Scatter(x=df['time'], y=upper, name='阈值上限', line=dict(color='red')))
        fig2.add_trace(go.Scatter(x=df['time'], y=lower, name='阈值下限', line=dict(color='red')))
    fig2.update_layout(title=f"{err_col} 误差与阈值", xaxis_title="时间 (s)", yaxis_title="误差")
    # 注记
    if percents:
        txt_lines = []
        mapping = {"≤1500m": "≤1500m", "≤800m": "≤800m", "全程": "全程"}
        for key in ["≤1500m", "≤800m", "全程"]:
            if key in percents:
                if is_angle:
                    rule = "±1°"
                elif is_speed:
                    rule = "±1m/s"
                else:
                    rule = "(0.5+0.2%×D)"
                txt_lines.append(f"{mapping[key]}: {percents[key]}% 满足 {rule}")
        if txt_lines:
            fig2.add_annotation(xref='paper', yref='paper', x=0.01, y=0.95,
                                text="<br>".join([metric_label] + txt_lines),
                                showarrow=False, align='left', bgcolor='rgba(255,255,255,0.7)', bordercolor='gray')
    return fig2

st.title("紫外导航算法与仿真数据误差分析")

st.sidebar.header("数据上传")
mode = st.sidebar.radio("选择数据来源", ["CSV", "JSON(analysis_data)", "项目数据包目录"])
alg_file = None
sim_file = None
json_file = None
package_dir = None
if mode == "CSV":
    alg_file = st.sidebar.file_uploader("算法输出 CSV", type=["csv"], key="alg")
    sim_file = st.sidebar.file_uploader("仿真输出 CSV", type=["csv"], key="sim")
elif mode == "JSON(analysis_data)":
    json_file = st.sidebar.file_uploader("analysis_data.json", type=["json"], key="json")
else:
    # 从项目 data 目录中选择一个数据包
    data_root = Path("data")
    candidates = [str(p) for p in data_root.glob("*/") if (Path(p)/"analysis_data.json").exists() or (Path(p)/"metadata").exists()]
    if not candidates:
        st.sidebar.info("未在 data/ 下发现数据包目录")
    package_dir = st.sidebar.selectbox("选择数据包目录", options=candidates if candidates else ["无可用目录"])

def parse_analysis_json(file, uv_from_gt: bool = True) -> Dict[str, pd.DataFrame]:
    """解析含注释的 analysis_data.json，产出 alg_df 与 sim_df。
    列：time,x,y,z,dist,lon,lat,alt,heading,speed
    其中 x=横向, y=纵向, z=高度。heading以度。
    """
    try:
        # 支持三种输入：已打开的文件对象 / 原始 JSON 字符串 / 文件路径字符串
        if hasattr(file, 'read'):
            raw = file.read()
        else:
            # 若是路径且存在则读取；否则直接视为 JSON 文本
            if isinstance(file, (str, Path)) and Path(str(file)).exists():
                raw = Path(str(file)).read_text(encoding="utf-8")
            else:
                raw = file
        if isinstance(raw, bytes):
            text = raw.decode("utf-8", errors="ignore")
        else:
            text = str(raw)
        # 初次尝试解析
        try:
            data = json5.loads(text)
        except Exception:
            # 兼容无数组包裹的多对象：在首尾加 [] 再试
            stripped = text.strip()
            if stripped.startswith("{") and not stripped.startswith("["):
                wrapped = f"[{stripped}]"
                data = json5.loads(wrapped)
            else:
                raise
        # 提取 frames 数组：若有 .frames 字段则用之，否则视为直接数组或单对象
        if isinstance(data, dict) and "frames" in data:
            frames = data["frames"]
        elif isinstance(data, list):
            frames = data
        else:
            frames = [data]
    except Exception as e:
        st.error(f"JSON 解析失败: {e}")
        return {}

    rows_alg, rows_sim = [], []
    debug_first_keys = None
    for f in frames:
        if debug_first_keys is None and isinstance(f, dict):
            debug_first_keys = list(f.keys())
        # 时间戳
        t = f.get("timestamp")
        if t is None:
            continue
        try:
            t = float(t) if isinstance(t, (str, int)) else t
        except Exception:
            continue
        
        # 按规范结构提取各层级数据
        gt = f.get("ground_truth", {})
        pos_ned = gt.get("position_ned", {})
        rel = gt.get("relative_to_ship", {})
        att = gt.get("attitude", {})
        vel = gt.get("velocity_ned", {})
        ao = f.get("algorithm_output", {})

        # sim (实际/DGPS)：来自仿真 ground_truth，表示“实际相对距离”
        # 提取速度, 若 speed 缺失尝试矢量分量 sqrt(vx^2+vy^2+vz^2)
        speed_val = vel.get("speed")
        if speed_val is None:
            vn, ve, vd = vel.get("vn"), vel.get("ve"), vel.get("vd")
            if all(v is not None for v in [vn, ve, vd]):
                try:
                    speed_val = float(np.sqrt(vn**2 + ve**2 + vd**2))
                except Exception:
                    speed_val = None
        heading_sim = None
        if att.get("yaw") is not None:
            try:
                heading_sim = float(np.degrees(att.get("yaw")))
            except Exception:
                pass
        sim_row = {
            "time": t,
            "x": float(rel.get("x_lateral")) if rel.get("x_lateral") is not None else None,
            "y": float(rel.get("y_longitudinal")) if rel.get("y_longitudinal") is not None else None,
            "z": float(rel.get("z_height")) if rel.get("z_height") is not None else None,
            "dist": float(rel.get("distance")) if rel.get("distance") is not None else None,
            "lon": float(rel.get("y_longitudinal")) if rel.get("y_longitudinal") is not None else None,
            "lat": float(rel.get("x_lateral")) if rel.get("x_lateral") is not None else None,
            "alt": float(rel.get("z_height")) if rel.get("z_height") is not None else None,
            "heading": heading_sim,
            "speed": float(speed_val) if speed_val is not None else None,
        }
        rows_sim.append(sim_row)

        # alg (紫外)：算法输出数据
        heading_alg = None
        heading_out = ao.get("heading")
        if heading_out is not None:
            try:
                heading_alg = float(heading_out)
            except Exception:
                pass
        
        x_alg = float(ao.get("x_lateral")) if ao.get("x_lateral") is not None else None
        y_alg = float(ao.get("y_longitudinal")) if ao.get("y_longitudinal") is not None else None
        z_alg = float(ao.get("z_height")) if ao.get("z_height") is not None else None
        dist_alg = float(ao.get("distance")) if ao.get("distance") is not None else None
        
        alg_row = {
            "time": t,
            "x": x_alg,
            "y": y_alg,
            "z": z_alg,
            "dist": float(rel.get("distance")) if (uv_from_gt and rel.get("distance") is not None) else dist_alg,
            "lon": y_alg,
            "lat": x_alg,
            "alt": z_alg,
            "heading": heading_alg,
            "speed": None,
        }
        rows_alg.append(alg_row)

    alg_df = pd.DataFrame(rows_alg)
    sim_df = pd.DataFrame(rows_sim)
    # 丢弃 time 缺失的行
    alg_df = alg_df.dropna(subset=["time"]).reset_index(drop=True)
    sim_df = sim_df.dropna(subset=["time"]).reset_index(drop=True)
    # 若全部 time 为 None 导致空，提示调试
    if alg_df.empty or sim_df.empty:
        st.info(f"解析后数据为空：时间字段可能缺失。首对象键: {debug_first_keys}")
    return {"alg_df": alg_df, "sim_df": sim_df}

def parse_package_dir(package_dir: str, uv_from_gt: bool = True) -> Dict[str, pd.DataFrame]:
    """从数据包目录读取数据：优先 analysis_data.json，否则聚合 metadata/frame_*.json。"""
    p = Path(package_dir)
    ana = p / "analysis_data.json"
    if ana.exists():
        with open(ana, "r", encoding="utf-8") as f:
            return parse_analysis_json(f, uv_from_gt=uv_from_gt)
    meta = p / "metadata"
    if meta.exists() and meta.is_dir():
        frames = []
        for fp in sorted(meta.glob("frame_*.json")):
            try:
                text = fp.read_text(encoding="utf-8")
                frames.append(json5.loads(text))
            except Exception:
                continue
        pseudo = "[" + ",".join([json5.dumps(fr) for fr in frames]) + "]"
        return parse_analysis_json(pseudo, uv_from_gt=uv_from_gt)
    return {}

if mode == "CSV" and alg_file and sim_file:
    alg_df = load_csv(alg_file)
    sim_df = load_csv(sim_file)

    if validate_dataframe(alg_df, "算法数据") and validate_dataframe(sim_df, "仿真数据"):
        err_df = compute_errors(alg_df, sim_df)
        with st.expander("诊断信息 (CSV): 列 & 样例"):
            st.write("列:", list(err_df.columns))
            st.write(err_df.head(3))
            st.write("非空计数:", err_df.count().to_dict())
        st.subheader("数据与误差预览")
        st.dataframe(err_df.head())

        stats = summary_stats(err_df)
        st.subheader("基础误差统计 (MAE / RMSE / MAX)")
        stat_rows = [{"误差维度": k, **v} for k, v in stats.items()]
        st.table(pd.DataFrame(stat_rows))

        # 合格率统计
        st.subheader("指标合格率统计")
        percent_records: List[Dict[str, float]] = []
        percent_map: Dict[str, Dict[str, float]] = {}
        # 距离类/位置类采用公式阈值
        for metric in ["err_dist", "err_lon", "err_lat", "err_alt"]:
            res = compute_range_percentages(err_df, metric)
            if any(v > 0 for v in res.values()):
                percent_records.append({"指标": metric, **res})
                percent_map[metric] = res
        # 航向角 & 速度固定阈值
        angle_res = compute_fixed_threshold_percentage(err_df, "err_heading", threshold=1.0)
        if any(v > 0 for v in angle_res.values()):
            percent_records.append({"指标": "err_heading(±1°)", **angle_res})
            percent_map["err_heading"] = angle_res
        speed_res = compute_fixed_threshold_percentage(err_df, "err_speed", threshold=1.0)
        if any(v > 0 for v in speed_res.values()):
            percent_records.append({"指标": "err_speed(±1m/s)", **speed_res})
            percent_map["err_speed"] = speed_res
        if percent_records:
            st.table(pd.DataFrame(percent_records))
        else:
            st.info("当前数据缺少距离/纵向/侧向/高度/航向角/速度列，无法计算合格率。")

        st.subheader("位置误差随时间")
        pos_err_cols = [c for c in ["err_x", "err_y", "err_z"] if c in err_df.columns]
        if pos_err_cols:
            fig_err = px.line(err_df, x="time", y=pos_err_cols, labels={"value": "位置误差", "time": "时间"})
            st.plotly_chart(fig_err, width='stretch')
        if "err_norm" in err_df.columns:
            fig_norm = px.line(err_df, x="time", y="err_norm", labels={"err_norm": "三维归一误差", "time": "时间"})
            st.plotly_chart(fig_norm, width='stretch')

        st.subheader("误差分布直方图")
        err_cols = [c for c in err_df.columns if c.startswith("err_")]
        if err_cols:
            grid_cols = st.columns(min(4, len(err_cols)))
            for i, axis in enumerate(err_cols):
                with grid_cols[i % len(grid_cols)]:
                    fig_hist = px.histogram(err_df, x=axis, nbins=40, title=axis)
                    st.plotly_chart(fig_hist, width='stretch')

        st.subheader("指标对比与误差阈值图")
        tab_names = ["距离", "纵向", "侧向", "高度", "航向角", "速度"]
        tabs = st.tabs(tab_names)
        charts_map = {
            "距离": ("dist_alg", "dist_sim", "err_dist", False, False, "紫外距离"),
            "纵向": ("lon_alg", "lon_sim", "err_lon", False, False, "紫外纵向"),
            "侧向": ("lat_alg", "lat_sim", "err_lat", False, False, "紫外侧向"),
            "高度": ("alt_alg", "alt_sim", "err_alt", False, False, "紫外高度"),
            "航向角": ("heading_alg", "heading_sim", "err_heading", True, False, "紫外航向角"),
            "速度": ("speed_alg", "speed_sim", "err_speed", False, True, "紫外速度")
        }
        for tab, name in zip(tabs, tab_names):
            val_alg, val_sim, err_c, is_angle, is_speed, label = charts_map[name]
            with tab:
                chs = plot_with_threshold(err_df, val_alg, val_sim, err_c, dist_col="dist_alg", is_angle=is_angle, is_speed=is_speed)
                for fig in chs:
                    st.plotly_chart(fig, width='stretch')
                if err_c in err_df.columns:
                    fig_err = plot_error_with_threshold(err_df, err_c, dist_col="dist_alg", is_angle=is_angle, is_speed=is_speed, percents=percent_map.get(err_c), metric_label=label)
                    st.plotly_chart(fig_err, width='stretch')
                else:
                    st.info(f"{err_c} 列缺失，无法绘制误差图。")
    else:
        st.info("请检查列名是否包含 time, x, y, z")
elif mode == "JSON(analysis_data)" and json_file:
    uv_src = st.sidebar.selectbox("紫外距离来源", ["仿真理论(GT)", "算法输出"], index=0)
    parsed = parse_analysis_json(json_file, uv_from_gt=(uv_src == "仿真理论(GT)"))
    if parsed:
        alg_df, sim_df = parsed["alg_df"], parsed["sim_df"]
        alg_df = normalize_df_columns(alg_df)
        sim_df = normalize_df_columns(sim_df)
        alg_df = normalize_df_columns(alg_df)
        sim_df = normalize_df_columns(sim_df)
        # 校验并计算
        needed = ["time", "x", "y", "z"]
        if all(c in alg_df.columns for c in needed) and all(c in sim_df.columns for c in needed):
            err_df = compute_errors(alg_df, sim_df)
            with st.expander("诊断信息 (JSON): 列 & 样例"):
                st.write("列:", list(err_df.columns))
                st.write(err_df.head(3))
                st.write("非空计数:", err_df.count().to_dict())
            st.subheader("数据与误差预览 (JSON)")
            st.dataframe(err_df.head())

            stats = summary_stats(err_df)
            st.subheader("基础误差统计 (MAE / RMSE / MAX)")
            st.table(pd.DataFrame([{"误差维度": k, **v} for k, v in stats.items()]))

            st.subheader("指标合格率统计")
            percent_records: List[Dict[str, float]] = []
            percent_map: Dict[str, Dict[str, float]] = {}
            # 距离类/位置类采用公式阈值
            for metric in ["err_dist", "err_lon", "err_lat", "err_alt"]:
                res = compute_range_percentages(err_df, metric)
                if any(v > 0 for v in res.values()):
                    percent_records.append({"指标": metric, **res})
                    percent_map[metric] = res
            # 航向角 & 速度固定阈值
            angle_res = compute_fixed_threshold_percentage(err_df, "err_heading", threshold=1.0)
            if any(v > 0 for v in angle_res.values()):
                percent_records.append({"指标": "err_heading(±1°)", **angle_res})
                percent_map["err_heading"] = angle_res
            speed_res = compute_fixed_threshold_percentage(err_df, "err_speed", threshold=1.0)
            if any(v > 0 for v in speed_res.values()):
                percent_records.append({"指标": "err_speed(±1m/s)", **speed_res})
                percent_map["err_speed"] = speed_res
            percent_map: Dict[str, Dict[str, float]] = {}
            for metric in ["err_dist", "err_lon", "err_lat", "err_alt"]:
                res = compute_range_percentages(err_df, metric)
                if any(v > 0 for v in res.values()):
                    percent_records.append({"指标": metric, **res})
                    percent_map[metric] = res
            angle_res = compute_fixed_threshold_percentage(err_df, "err_heading", threshold=1.0)
            if any(v > 0 for v in angle_res.values()):
                percent_records.append({"指标": "err_heading(±1°)", **angle_res})
                percent_map["err_heading"] = angle_res
            speed_res = compute_fixed_threshold_percentage(err_df, "err_speed", threshold=1.0)
            if any(v > 0 for v in speed_res.values()):
                percent_records.append({"指标": "err_speed(±1m/s)", **speed_res})
                percent_map["err_speed"] = speed_res
            if percent_records:
                st.table(pd.DataFrame(percent_records))

            st.subheader("指标对比与误差阈值图")
            tab_names = ["距离", "纵向", "侧向", "高度", "航向角"]
            tabs = st.tabs(tab_names)
            charts_map = {
                "距离": ("dist_alg", "dist_sim", "err_dist", False, False, "紫外距离"),
                "纵向": ("lon_alg", "lon_sim", "err_lon", False, False, "紫外纵向"),
                "侧向": ("lat_alg", "lat_sim", "err_lat", False, False, "紫外侧向"),
                "高度": ("alt_alg", "alt_sim", "err_alt", False, False, "紫外高度"),
                "航向角": ("heading_alg", "heading_sim", "err_heading", True, False, "紫外航向角"),
            }
            for tab, name in zip(tabs, tab_names):
                val_alg, val_sim, err_c, is_angle, is_speed, label = charts_map[name]
                with tab:
                    if val_alg not in err_df.columns or val_sim not in err_df.columns:
                        st.info(f"缺少列以绘制对比图: {val_alg} 或 {val_sim} (当前列: {', '.join(err_df.columns)})")
                        chs = []
                    else:
                        chs = plot_with_threshold(err_df, val_alg, val_sim, err_c, dist_col="dist_alg", is_angle=is_angle, is_speed=is_speed)
                    for fig in chs:
                        st.plotly_chart(fig, width='stretch')
                    if err_c in err_df.columns:
                        try:
                            fig_err = plot_error_with_threshold(err_df, err_c, dist_col="dist_alg", is_angle=is_angle, is_speed=is_speed, percents=percent_map.get(err_c), metric_label=label)
                            st.plotly_chart(fig_err, width='stretch')
                        except Exception as e:
                            st.info(f"绘制误差图时出错: {e}")
                    else:
                        st.info(f"{err_c} 列缺失，无法绘制误差图。")
                    if err_c in err_df.columns:
                        fig_err = plot_error_with_threshold(err_df, err_c, dist_col="dist_alg", is_angle=is_angle, is_speed=is_speed, percents=percent_map.get(err_c), metric_label=label)
                        st.plotly_chart(fig_err, width='stretch')
                    else:
                        st.info(f"{err_c} 列缺失，无法绘制误差图。")
                    # 已绘制误差图并注记，避免重复绘制 (仅保留一个)
        else:
            st.error("JSON 解析后缺少 time/x/y/z 列，无法计算误差。")
elif mode == "项目数据包目录" and package_dir and package_dir != "无可用目录":
    uv_src = st.sidebar.selectbox("紫外距离来源", ["仿真理论(GT)", "算法输出"], index=0, key="uvsrc_dir")
    parsed = parse_package_dir(package_dir, uv_from_gt=(uv_src == "仿真理论(GT)"))
    if parsed:
        alg_df, sim_df = parsed["alg_df"], parsed["sim_df"]
        needed = ["time", "x", "y", "z"]
        if all(c in alg_df.columns for c in needed) and all(c in sim_df.columns for c in needed):
            err_df = compute_errors(alg_df, sim_df)
            st.subheader(f"数据与误差预览 ({package_dir})")
            st.dataframe(err_df.head())

            stats = summary_stats(err_df)
            st.subheader("基础误差统计 (MAE / RMSE / MAX)")
            st.table(pd.DataFrame([{"误差维度": k, **v} for k, v in stats.items()]))

            st.subheader("指标合格率统计")
            percent_records: List[Dict[str, float]] = []
            for metric in ["err_dist", "err_lon", "err_lat", "err_alt"]:
                res = compute_range_percentages(err_df, metric)
                if any(v > 0 for v in res.values()):
                    percent_records.append({"指标": metric, **res})
            angle_res = compute_fixed_threshold_percentage(err_df, "err_heading", threshold=1.0)
            if any(v > 0 for v in angle_res.values()):
                percent_records.append({"指标": "err_heading(±1°)", **angle_res})
            speed_res = compute_fixed_threshold_percentage(err_df, "err_speed", threshold=1.0)
            if any(v > 0 for v in speed_res.values()):
                percent_records.append({"指标": "err_speed(±1m/s)", **speed_res})
            if percent_records:
                st.table(pd.DataFrame(percent_records))

            st.subheader("指标对比与误差阈值图")
            tab_names = ["距离", "纵向", "侧向", "高度", "航向角"]
            tabs = st.tabs(tab_names)
            charts_map = {
                "距离": ("dist_alg", "dist_sim", "err_dist", False, False, "紫外距离"),
                "纵向": ("lon_alg", "lon_sim", "err_lon", False, False, "紫外纵向"),
                "侧向": ("lat_alg", "lat_sim", "err_lat", False, False, "紫外侧向"),
                "高度": ("alt_alg", "alt_sim", "err_alt", False, False, "紫外高度"),
                "航向角": ("heading_alg", "heading_sim", "err_heading", True, False, "紫外航向角"),
            }
            for tab, name in zip(tabs, tab_names):
                val_alg, val_sim, err_c, is_angle, is_speed, label = charts_map[name]
                with tab:
                    if val_alg not in err_df.columns or val_sim not in err_df.columns:
                        st.info(f"缺少列以绘制对比图: {val_alg} 或 {val_sim} (当前列: {', '.join(err_df.columns)})")
                        chs = []
                    else:
                        chs = plot_with_threshold(err_df, val_alg, val_sim, err_c, dist_col="dist_alg", is_angle=is_angle, is_speed=is_speed)
                    for fig in chs:
                        st.plotly_chart(fig, width='stretch')
        else:
            st.error("目录解析后缺少 time/x/y/z 列，无法计算误差。")
else:
    st.info("请在侧边栏选择 CSV、analysis_data.json 或数据包目录。示例数据见 data 目录。")
st.caption("当前版本：已支持距离/纵向/侧向/高度/航向角/速度误差及合格率统计。缺失列时自动跳过。")
