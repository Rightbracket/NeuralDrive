*This chapter is for everyone.*

# TUI Dashboard

The Dashboard is the central monitoring hub of NeuralDrive. It is designed to provide immediate visual feedback on the health and workload of your system.

## Layout and Sections

The dashboard is divided into three functional areas:

### 1. Header and System Info
Located at the very top, this section displays the version of NeuralDrive, the current hostname, system uptime, and the primary IP address. A live system clock is displayed in the upper-right corner, showing the exact time of the last data refresh.

### 2. Hardware Resource Monitor
This section provides real-time metrics for your hardware.

- **GPU:** Displays the detected GPU model name, total VRAM capacity, driver version, and CUDA compute capability.
- **VRAM:** Shows the current VRAM usage (e.g., 12.4/24.0 GB) and a percentage bar.
- **Temp:** Current GPU temperature in Celsius.
- **CPU:** Real-time CPU utilization percentage.
- **RAM:** System memory usage (e.g., 18.2/64.0 GB).
- **Disk:** Total disk space used on the persistence partition (e.g., 45.2 GB).

- **Refresh Rate:** Hardware metrics refresh every **2 seconds**. You can press **R** at any time to trigger a manual refresh of all dashboard data.

### 3. Loaded Models List
This list displays the models currently residing in memory and ready for immediate inference.

- **Status Indicator:** A solid circle (●) indicates the model is currently loaded in memory. An open circle (○) indicates the model is cached on disk but not currently loaded.
- **Backend:** Shows if the model is running on the **[GPU]** or **[CPU]**.
- **VRAM Footprint:** The amount of memory the model is currently occupying.

- **Refresh Rate:** The model list metrics refresh every **10 seconds**.

## Interaction
The Dashboard is accessed via **F1** from any other screen. While it is primarily for monitoring, you can transition to other management screens using the function keys (F2-F5) shown at the bottom. Use the **R** key to manually refresh the displayed information.

