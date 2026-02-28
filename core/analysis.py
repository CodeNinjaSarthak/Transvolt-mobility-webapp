# analysis.py
import os
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Matplotlib backend for headless servers
import matplotlib

matplotlib.use("Agg")


def load_df(csv_path=None, uploaded_bytes=None):
    """
    Load DataFrame either from a file path or uploaded BytesIO.
    """
    if uploaded_bytes is not None:
        df = pd.read_csv(io.BytesIO(uploaded_bytes))
    elif csv_path is not None and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        raise FileNotFoundError("CSV not found. Provide a valid path or upload a file.")
    # Ensure expected columns
    if "Timestamp" not in df.columns or "Values" not in df.columns:
        raise ValueError("CSV must contain 'Timestamp' and 'Values' columns.")
    # Parse & sort
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"], format="%d/%m/%y %H:%M", errors="coerce"
    )
    df = df.dropna(subset=["Timestamp"]).sort_values("Timestamp").reset_index(drop=True)
    # 5 point moving average (your code uses 5 rows; not daily aggregation)
    df["5_day_MA"] = df["Values"].rolling(window=5, min_periods=1).mean()
    return df


def find_extrema(df):
    # peaks & troughs
    peaks, _ = find_peaks(df["Values"])
    troughs, _ = find_peaks(-df["Values"])
    peaks_df = df.iloc[peaks].copy()
    troughs_df = df.iloc[troughs].copy()
    peaks_df = peaks_df[["Timestamp", "Values"]].rename(columns={"Values": "Value"})
    troughs_df = troughs_df[["Timestamp", "Values"]].rename(columns={"Values": "Value"})
    return peaks_df, troughs_df, peaks, troughs


def below_20(df):
    return df[df["Values"] < 20][["Timestamp", "Values"]].rename(
        columns={"Values": "Value"}
    )


def find_downward_acceleration(df):
    """
    Your rule: find the point in each downward cycle where slope is the most negative.
    """
    df = df.copy()
    df["slope"] = df["Values"].diff()

    downward_cycles = []
    current_cycle = []

    for i in range(1, len(df)):
        if df["slope"].iloc[i] < 0:
            current_cycle.append(i)
        else:
            if current_cycle:
                downward_cycles.append(current_cycle)
                current_cycle = []
    if current_cycle:
        downward_cycles.append(current_cycle)

    acceleration_points = []
    for cycle in downward_cycles:
        min_slope_idx = df["slope"].iloc[cycle].idxmin()
        acceleration_points.append(
            (
                int(min_slope_idx),
                df["Timestamp"].iloc[min_slope_idx],
                float(df["Values"].iloc[min_slope_idx]),
            )
        )

    accel_df = pd.DataFrame(
        acceleration_points, columns=["Index", "Timestamp", "Value"]
    )
    return accel_df


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def plot_and_save_all(df, peaks_idx, troughs_idx, accel_df, out_dir="static"):
    ensure_dir(out_dir)

    # Plot 1: Original
    fig = plt.figure(figsize=(10, 4))
    plt.plot(df["Timestamp"], df["Values"], label="Voltage")
    plt.xlabel("Timestamp")
    plt.ylabel("Voltage")
    plt.title("Original Voltage Data")
    plt.grid(True)
    plt.legend()
    fig.savefig(os.path.join(out_dir, "plot_1_original.png"), bbox_inches="tight")
    plt.close(fig)

    # Plot 2: 5-day MA
    fig = plt.figure(figsize=(10, 4))
    plt.plot(df["Timestamp"], df["Values"], label="Voltage")
    plt.plot(df["Timestamp"], df["5_day_MA"], label="5-day MA")
    plt.xlabel("Timestamp")
    plt.ylabel("Voltage")
    plt.title("Voltage with 5-day Moving Average")
    plt.grid(True)
    plt.legend()
    fig.savefig(os.path.join(out_dir, "plot_2_ma.png"), bbox_inches="tight")
    plt.close(fig)

    # Plot 3: Peaks & Troughs
    fig = plt.figure(figsize=(10, 4))
    plt.plot(df["Timestamp"], df["Values"], label="Voltage")
    if len(peaks_idx):
        plt.scatter(
            df.iloc[peaks_idx]["Timestamp"],
            df.iloc[peaks_idx]["Values"],
            s=10,
            label="Peaks",
            zorder=5,
        )
    if len(troughs_idx):
        plt.scatter(
            df.iloc[troughs_idx]["Timestamp"],
            df.iloc[troughs_idx]["Values"],
            s=10,
            label="Troughs",
            zorder=5,
        )
    plt.xlabel("Timestamp")
    plt.ylabel("Voltage")
    plt.title("Local Peaks & Troughs")
    plt.grid(True)
    plt.legend()
    fig.savefig(os.path.join(out_dir, "plot_3_peaks_troughs.png"), bbox_inches="tight")
    plt.close(fig)

    # Plot 4: Voltage < 20
    below = df[df["Values"] < 20]
    fig = plt.figure(figsize=(10, 4))
    plt.plot(df["Timestamp"], df["Values"], label="Voltage")
    if not below.empty:
        plt.scatter(
            below["Timestamp"], below["Values"], s=10, label="Voltage < 20", zorder=5
        )
    plt.xlabel("Timestamp")
    plt.ylabel("Voltage")
    plt.title("Voltage Below 20")
    plt.grid(True)
    plt.legend()
    fig.savefig(os.path.join(out_dir, "plot_4_below20.png"), bbox_inches="tight")
    plt.close(fig)

    # Plot 5: Downward acceleration points
    fig = plt.figure(figsize=(10, 4))
    plt.plot(df["Timestamp"], df["Values"], label="Voltage")
    if not accel_df.empty:
        plt.scatter(
            accel_df["Timestamp"],
            accel_df["Value"],
            s=15,
            label="Downward Acceleration",
            zorder=5,
        )
    plt.xlabel("Timestamp")
    plt.ylabel("Voltage")
    plt.title("Downward Acceleration Points")
    plt.grid(True)
    plt.legend()
    fig.savefig(os.path.join(out_dir, "plot_5_acceleration.png"), bbox_inches="tight")
    plt.close(fig)


def run_analysis(csv_path=None, uploaded_bytes=None, out_dir="static"):
    df = load_df(csv_path=csv_path, uploaded_bytes=uploaded_bytes)
    peaks_df, troughs_df, peaks_idx, troughs_idx = find_extrema(df)
    below_df = below_20(df)
    accel_df = find_downward_acceleration(df)

    # Save acceleration CSV for download
    ensure_dir(out_dir)
    accel_csv_path = os.path.join(out_dir, "downward_acceleration_points.csv")
    accel_df.to_csv(accel_csv_path, index=False)

    # Make all plots
    plot_and_save_all(df, peaks_idx, troughs_idx, accel_df, out_dir=out_dir)

    # Return tables (as DataFrames) to render
    return {
        "df": df,
        "peaks_df": peaks_df,
        "troughs_df": troughs_df,
        "below_df": below_df,
        "accel_df": accel_df,
        "accel_csv_path": accel_csv_path,
    }
