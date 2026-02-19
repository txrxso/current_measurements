import re, os, time, csv, sys, signal
from datetime import datetime
import serial
import matplotlib.pyplot as plt
import pandas as pd

from enum import Enum


class Topology(Enum):
    GATEWAY_ONLY = (1, "Gateway node only")
    GATEWAY_NOISE = (2, "Gateway and noise node")
    GATEWAY_AIR = (3, "Gateway and air quality node")
    GATEWAY_FULL = (4, "Gateway, noise, and air quality node")

    def __init__(self, id, description):
        self.id = id
        self.description = description

class Scenario(Enum):
    HEARTBEATS_ONLY = ("A", "Heartbeats only (5m)")
    MOCK_ALERTS_12M = ("B", "Heartbeats (5m) + Mock Alerts (12m)")
    MOCK_ALERTS_5M = ("C", "Heartbeats (5m) + Mock Alerts (5m)")

    def __init__(self, code, description):
        self.code = code
        self.description = description



# MANUALLY SET THESE VALUES
topology = Topology.GATEWAY_ONLY
scenario = Scenario.HEARTBEATS_ONLY
baud = 115200
port = "COM7"          

def pre_log_checks() -> str: 
    # ensure directories exist (../data/ and ../data/plots/)
    test_data_dir = os.path.join(os.path.dirname(__file__), "../data/")
    plots_dir = os.path.join(test_data_dir, "plots/")
    os.makedirs(test_data_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    curr_dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_file = os.path.join(test_data_dir, f"{topology.name}_{scenario.code}_{curr_dt}_current.csv")

    # check the scenario and topology values are valid instances of the types 
    if not isinstance(topology, Topology):
        raise ValueError(f"Invalid topology value: {topology}. Must be an instance of Topology enum.")
    if not isinstance(scenario, Scenario):
        raise ValueError(f"Invalid scenario value: {scenario}. Must be an instance of Scenario enum.") 

    return out_file


def auto_gen_plots(csv_file: str) -> None:
    """Generate separate plots for each measurement column vs time."""
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate relative time in seconds from start
    df['time_seconds'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
    
    # Define columns to plot (exclude timestamp and time_seconds)
    columns_to_plot = [
        ('current_mA', 'Current (mA)'),
        ('shunt_voltage_mV', 'Shunt Voltage (mV)'),
        ('bus_voltage_V', 'Bus Voltage (V)'),
        ('load_voltage_V', 'Load Voltage (V)'),
        ('power_mW', 'Power (mW)')
    ]
    
    # Get plots directory
    plots_dir = os.path.join(os.path.dirname(csv_file), "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # Get base filename without extension
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    
    # Create a plot for each measurement
    for col, label in columns_to_plot:
        if col in df.columns:
            plt.figure(figsize=(10, 6))
            plt.plot(df['time_seconds'], df[col], linewidth=1.5)
            plt.xlabel('Time (seconds)', fontsize=12)
            plt.ylabel(label, fontsize=12)
            plt.title(f'{label} vs Time', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save the plot
            plot_filename = os.path.join(plots_dir, f"{base_name}_{col}.png")
            plt.savefig(plot_filename, dpi=150)
            plt.close()
            print(f"Saved plot: {plot_filename}") 


def log_current():
    out_file = pre_log_checks()

    with serial.Serial(port, baud) as ser, open(out_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "current_mA", "shunt_voltage_mV", "bus_voltage_V", "load_voltage_V", "power_mW"])

        print(f"Logging current measurements to {out_file}... Press Ctrl+C to stop.")
        
        # Buffer to store values for each sample
        data_buffer = {}
        
        try:
            while True:
                line = ser.readline().decode("utf-8").strip()
                
                # Parse each type of measurement
                if line.startswith("Current:"):
                    try:
                        value = float(line.split(":")[1].replace("mA", "").strip())
                        data_buffer['current_mA'] = value
                    except ValueError:
                        print(f"Invalid current value: {line}")
                        
                elif line.startswith("Shunt Voltage:"):
                    try:
                        value = float(line.split(":")[1].replace("mV", "").strip())
                        data_buffer['shunt_voltage_mV'] = value
                    except ValueError:
                        print(f"Invalid shunt voltage value: {line}")
                        
                elif line.startswith("Bus Voltage:"):
                    try:
                        value = float(line.split(":")[1].replace("V", "").strip())
                        data_buffer['bus_voltage_V'] = value
                    except ValueError:
                        print(f"Invalid bus voltage value: {line}")
                        
                elif line.startswith("Load Voltage:"):
                    try:
                        value = float(line.split(":")[1].replace("V", "").strip())
                        data_buffer['load_voltage_V'] = value
                    except ValueError:
                        print(f"Invalid load voltage value: {line}")
                        
                elif line.startswith("Power:"):
                    try:
                        value = float(line.split(":")[1].replace("mW", "").strip())
                        data_buffer['power_mW'] = value
                        
                        # Power is the last value, so write the complete row
                        if len(data_buffer) == 5:
                            timestamp = datetime.now().isoformat()
                            writer.writerow([
                                timestamp,
                                data_buffer.get('current_mA', ''),
                                data_buffer.get('shunt_voltage_mV', ''),
                                data_buffer.get('bus_voltage_V', ''),
                                data_buffer.get('load_voltage_V', ''),
                                data_buffer.get('power_mW', '')
                            ])
                            csvfile.flush()  # Ensure data is written to disk
                            print(f"{timestamp} - Current: {data_buffer['current_mA']:.2f} mA, "
                                  f"Power: {data_buffer['power_mW']:.2f} mW")
                            data_buffer.clear()
                    except ValueError:
                        print(f"Invalid power value: {line}")
                        
        except KeyboardInterrupt:
            print("\nLogging stopped by user.")
    
    # Generate plots after logging is complete
    print("\nGenerating plots...")
    auto_gen_plots(out_file)
    print(f"\nData saved to: {out_file}")
    

    



if __name__ == "__main__":
    raise SystemExit(log_current())