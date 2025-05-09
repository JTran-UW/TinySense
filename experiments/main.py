# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 00:46:52 2024

@author: zhita
"""

from TinySense.data_processing import (
    preprocess_data, interpolate_mocap, kalman_filter_from_1cm_optic
)
from TinySense.plotting import plot_data_all_sensors_bw, plot_estimates_all
import matplotlib.pyplot as plt
from sklearn.metrics import root_mean_squared_error
import numpy as np
import matplotlib as mpl

# Set plot configurations
mpl.rcParams['pdf.fonttype'] = 42
plt.rcParams.update({'font.size': 17})
plt.rcParams['font.family'] = 'Open Sans'

# File paths for three flight experiments
experiments = [
    ('data/exp1/crazyflie/cf_first.csv', 
     'data/exp1/tinySense/ts_first.csv', 
     'data/exp1/mocap/mocap_first.csv'),
     
    ('data/exp2/crazyflie/cf_second.csv', 
     'data/exp2/tinysense/ts_second.csv', 
     'data/exp2/mocap/mocap_second.csv'),
     
    ('data/exp3/crazyflie/cf_third.csv', 
     'data/exp3/tinysense/ts_third.csv', 
     'data/exp3/mocap/mocap_third.csv')
]

# Titles for each experiment's subplot
titles = ["(a)", "(b)", "(c)"]

# Initialize plots for sensor data and state estimates
fig_all, axs = plt.subplots(3, 3, figsize=(22, 12))
fig_all_est, axs_est = plt.subplots(3, 3, figsize=(22, 12))

# Initialize lists for RMS calculations
ts_mocap_vx_RMS_list, ts_mocap_theta_RMS_list, ts_mocap_altitude_RMS_list = [], [], []
cf_mocap_vx_RMS_list, cf_mocap_theta_RMS_list, cf_mocap_altitude_RMS_list = [], [], []

# Process and plot each experiment
for i, (cf_path, ts_path, mocap_path) in enumerate(experiments):
    print(f"Processing experiment {i+1}")
    cf_data, ts_data, mocap_data = preprocess_data(cf_path, ts_path, mocap_path, i)
    mocap_data = interpolate_mocap(mocap_data)
    
    # Plot sensor data
    plot_data_all_sensors_bw(cf_data, ts_data, mocap_data, axs, i, titles[i])

    # Apply Kalman filter and plot estimates
    cf_data, ts_data, mocap_data, q_est, zero_idx, zero_idx_cf, zero_idx_mocap, K = kalman_filter_from_1cm_optic(cf_data, ts_data, mocap_data)
    plot_estimates_all(cf_data, ts_data, mocap_data, q_est, axs_est, i, titles[i], zero_idx, zero_idx_cf, zero_idx_mocap)
    
    # Truncate data to start from the same time point
    q_est = q_est[zero_idx:]
    cf_data = cf_data[zero_idx_cf:]
    mocap_data = mocap_data[zero_idx_mocap:]

    # Downsample q_est and mocap to match cf_data timestamps
    downsampled_qest_data = np.zeros((cf_data.shape[0], q_est.shape[1]))
    downsampled_mocap_data = np.zeros((cf_data.shape[0], mocap_data.shape[1]))

    for i, cf_time in enumerate(cf_data[:, 0]):
        closest_idx_qest = np.argmin(np.abs(q_est[:, 0] - cf_time))
        downsampled_qest_data[i] = q_est[closest_idx_qest]
        
        closest_idx_mocap = np.argmin(np.abs(mocap_data[:, 0] - cf_time))
        downsampled_mocap_data[i] = mocap_data[closest_idx_mocap]
    
    # Calculate RMS errors (TinySense vs Crazyflie and TinySense vs mocap)
    ts_cf_vx_RMS = root_mean_squared_error(-cf_data[:, 5], downsampled_qest_data[:, 2])
    ts_cf_theta_RMS = root_mean_squared_error(cf_data[:, 6], -downsampled_qest_data[:, 1])
    ts_cf_altitude_RMS = root_mean_squared_error(cf_data[:, 3], downsampled_qest_data[:, 3])

    ts_mocap_vx_RMS = root_mean_squared_error(downsampled_mocap_data[:, 1], downsampled_qest_data[:, 2])
    ts_mocap_theta_RMS = root_mean_squared_error(np.degrees(downsampled_mocap_data[:, 2]), -np.degrees(downsampled_qest_data[:, 1]))
    ts_mocap_altitude_RMS = root_mean_squared_error(downsampled_mocap_data[:, 3], downsampled_qest_data[:, 3])

    # Append results to lists
    ts_mocap_vx_RMS_list.append(ts_mocap_vx_RMS)
    ts_mocap_theta_RMS_list.append(ts_mocap_theta_RMS)
    ts_mocap_altitude_RMS_list.append(ts_mocap_altitude_RMS)

    cf_mocap_vx_RMS = root_mean_squared_error(-cf_data[:, 5], downsampled_mocap_data[:, 1])
    cf_mocap_theta_RMS = root_mean_squared_error(np.degrees(cf_data[:, 6]), np.degrees(downsampled_mocap_data[:, 2]))
    cf_mocap_altitude_RMS = root_mean_squared_error(cf_data[:, 3], downsampled_mocap_data[:, 3])

    cf_mocap_vx_RMS_list.append(cf_mocap_vx_RMS)
    cf_mocap_theta_RMS_list.append(cf_mocap_theta_RMS)
    cf_mocap_altitude_RMS_list.append(cf_mocap_altitude_RMS)

# Calculate mean and standard deviation for the RMS values
cf_mocap_vx_RMS_mean, cf_mocap_vx_RMS_std = np.mean(cf_mocap_vx_RMS_list), np.std(cf_mocap_vx_RMS_list)
cf_mocap_theta_RMS_mean, cf_mocap_theta_RMS_std = np.mean(cf_mocap_theta_RMS_list), np.std(cf_mocap_theta_RMS_list)
cf_mocap_altitude_RMS_mean, cf_mocap_altitude_RMS_std = np.mean(cf_mocap_altitude_RMS_list), np.std(cf_mocap_altitude_RMS_list)

ts_mocap_vx_RMS_mean, ts_mocap_vx_RMS_std = np.mean(ts_mocap_vx_RMS_list), np.std(ts_mocap_vx_RMS_list)
ts_mocap_theta_RMS_mean, ts_mocap_theta_RMS_std = np.mean(ts_mocap_theta_RMS_list), np.std(ts_mocap_theta_RMS_list)
ts_mocap_altitude_RMS_mean, ts_mocap_altitude_RMS_std = np.mean(ts_mocap_altitude_RMS_list), np.std(ts_mocap_altitude_RMS_list)

# Save results to a text file
with open("results.txt", "w") as file:
    file.write(f"cf_mocap_vx_RMS_mean: {cf_mocap_vx_RMS_mean:.3f}\n")
    file.write(f"cf_mocap_vx_RMS_std: {cf_mocap_vx_RMS_std:.3f}\n")
    file.write(f"cf_mocap_theta_RMS_mean: {cf_mocap_theta_RMS_mean:.3f}\n")
    file.write(f"cf_mocap_theta_RMS_std: {cf_mocap_theta_RMS_std:.3f}\n")
    file.write(f"cf_mocap_altitude_RMS_mean: {cf_mocap_altitude_RMS_mean:.3f}\n")
    file.write(f"cf_mocap_altitude_RMS_std: {cf_mocap_altitude_RMS_std:.3f}\n")
    
    file.write(f"ts_mocap_vx_RMS_mean: {ts_mocap_vx_RMS_mean:.3f}\n")
    file.write(f"ts_mocap_vx_RMS_std: {ts_mocap_vx_RMS_std:.3f}\n")
    file.write(f"ts_mocap_theta_RMS_mean: {ts_mocap_theta_RMS_mean:.3f}\n")
    file.write(f"ts_mocap_theta_RMS_std: {ts_mocap_theta_RMS_std:.3f}\n")
    file.write(f"ts_mocap_altitude_RMS_mean: {ts_mocap_altitude_RMS_mean:.3f}\n")
    file.write(f"ts_mocap_altitude_RMS_std: {ts_mocap_altitude_RMS_std:.3f}\n")
    file.write(f"Kalman gain K: {K}\n")

# Adjust layout for both figures and save plots
fig_all.tight_layout()  # Adjust layout for sensor data plot
fig_all_est.tight_layout()  # Adjust layout for state estimates plot

# Display and save both figures
fig_all.show()
fig_all_est.show()

fig_all.savefig("sensorMeasure.png")
fig_all_est.savefig("stateEstimation.png")


