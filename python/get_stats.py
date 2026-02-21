import pandas as pd
import numpy as np 
import os 

# ==== CONFIG ====
csv_path = "C:\\Users\\teres\\Projects\\current_measurements\\data\\GATEWAY_ONLY_A_2026-02-19_16-41-31_current.csv"
thresholds = [150, 180, 200, 250] # mA thresholds for TX detection 
moving_avg_window = 10 # number of samples for moving average
discard_threshold = 1 # mA thresholds that mean not connected to PWR yet

# ==== SCRIPT ====

def basic_current_stats(df: pd.DataFrame, total_time: float) -> dict:
    stats = {}

    stats["total_time_s"] = total_time
    stats["mean_current_simple_mA"] = df["current_mA"].mean()

    # True integrated average current
    stats["mean_current_integrated_mA"] = (
        (df["current_filtered"] * df["dt"]).sum() / total_time
    )

    # Integrated average power
    stats["mean_power_mW"] = (
        (df["power_mW"] * df["dt"]).sum() / total_time
    )

    stats["min_current_mA"] = df["current_mA"].min()
    stats["max_current_mA"] = df["current_mA"].max()
    stats["std_current_mA"] = df["current_mA"].std()

    return stats

def duty_cycle_estimation(df: pd.DataFrame, total_time: float, current_column: str) -> dict: 
    duty_results = {}

    for th in thresholds:
        active = df[current_column] > th
        active_time = df.loc[active, "dt"].sum()
        duty = active_time / total_time

        duty_results[f"threshold_{th}_mA"] = {
            "active_time_s": active_time,
            "duty_cycle_percent": duty * 100,
        }
    
    return duty_results
    

def tx_burst_detection(df: pd.DataFrame, tx_threshold: float = 180) -> dict:
    df["is_tx"] = df["current_filtered"] > tx_threshold

    bursts = []
    in_burst = False
    burst_start = None

    for i, row in df.iterrows():
        if row["is_tx"] and not in_burst:
            in_burst = True
            burst_start = row["time_s"]

        elif not row["is_tx"] and in_burst:
            in_burst = False
            burst_end = row["time_s"]
            bursts.append(burst_end - burst_start)

    if not bursts:
        return {"num_bursts": 0}

    return {
        "num_bursts": len(bursts),
        "avg_burst_duration_s": np.mean(bursts),
        "max_burst_duration_s": np.max(bursts),
        "min_burst_duration_s": np.min(bursts),
    }


def run_stats(): 
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    # convert time to seconds
    df['time_s'] = (df['timestamp'] - df['timestamp']
                    .iloc[0]).dt.total_seconds()
    
    # remove start up transient 
    df=df[df['current_mA'] > discard_threshold]

    # compute time delta
    df['dt'] = df['time_s'].diff()
    df.loc[df.index[0], 'dt'] = 0

    total_time = df['dt'].sum()

    # apply smoothing 
    df['current_filtered'] = df['current_mA'].rolling(
        window=moving_avg_window, 
        min_periods=1
    ).mean()

    # run analyses
    basic = basic_current_stats(df, total_time)
    duty_raw = duty_cycle_estimation(df, total_time, "current_mA")
    duty_filtered = duty_cycle_estimation(df, total_time, "current_filtered")
    tx = tx_burst_detection(df)

    # write out to txt file
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    with open(f"{base_name}_stats.txt", "w") as f:
        f.write("=== Basic Current Stats ===\n")
        for k, v in basic.items():
            f.write(f"{k}: {v}\n")

        f.write("\n=== Duty Cycle Estimation ===\n")
        f.write("\n--- Raw Current ---\n")
        for th, res in duty_raw.items():
            f.write(f"Threshold: {th}\n")
            for k, v in res.items():
                f.write(f"  {k}: {v}\n")

        f.write("\n--- Filtered Current ---\n")
        for th, res in duty_filtered.items():
            f.write(f"Threshold: {th}\n")
            for k, v in res.items():
                f.write(f"  {k}: {v}\n")

        f.write("\n=== TX Burst Detection ===\n")
        for k, v in tx.items():
            f.write(f"{k}: {v}\n")
    


if __name__ == "__main__":
    run_stats()