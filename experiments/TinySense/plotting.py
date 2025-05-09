# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 00:45:23 2024

@author: zhita
"""

import matplotlib.pyplot as plt
from cycler import cycler
import matplotlib as mpl
import numpy as np

mpl.rcParams['pdf.fonttype'] = 42

# Get the default color cycle
default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']


def plot_data_single_exp(cf_data, ts_data, mocap_data, experiment_num):
    fig, axs = plt.subplots(3, 1, figsize=(10, 8))
    ylabels = ["$vx$ (m/s)", r"$\theta$ $(rad)$", "$z$ $(m)$"]

    axs[0].plot(ts_data["timestamp"], ts_data["gyro(d/s)"], label="Tinysense Gyro", alpha=0.8)
    axs[0].plot(cf_data["timestamp"], cf_data["gyro_pitch_filtered(rad/s)"], label="Crazyflie Gyro", alpha=0.8)
    axs[0].set_ylabel("Gyro measurement (rad/s)")
    axs[0].legend()
    
    axs[1].plot(ts_data["timestamp"], ts_data["optic_flow(rad/s)"], label="Tinysense Optic Flow", alpha=0.8)
    axs[1].plot(cf_data["timestamp"], cf_data["of_x(pixels/frame)"], label="Crazyflie Optic Flow", alpha=0.8)
    axs[1].set_ylabel("Optic flow (pixels/frame)")
    axs[1].legend()
    
    axs[2].plot(ts_data["timestamp"], ts_data["z(m)"], label="Tinysense Altitude", alpha=0.8)
    axs[2].plot(cf_data["timestamp"], cf_data["pz(m)"], label="Crazyflie Altitude", alpha=0.8)
    axs[2].plot(mocap_data["timestamp"], mocap_data["z(m)"], label="Mocap Altitude", linestyle="dashed", alpha=0.8)
    axs[2].set_ylabel("Altitude (m)")
    axs[2].legend()
    
    for ax in axs:
        ax.set_xlabel("Timestamp")
    
    plt.suptitle(f"Experiment {experiment_num} Data")
    plt.tight_layout()
    plt.show()


def plot_data_all_sensors_bw(cf_data, ts_data, mocap_data, axs, col, title):
    # ylabels = ["$vx$ (m/s)", r"$\theta$ $(rad)$", "$z$ $(m)$"]
    YLIM_GYRO = [-5, 5]
    YLIM_OPTIC_FLOW = [-2.6, 2.6]
    YLIM_ALTITUDE = [-3.0, 1.5]

    # Plot gyro
    axs[0, col].plot(cf_data["timestamp"], cf_data["gyro_pitch_filtered(rad/s)"], linewidth="5", color="lightgrey", label="Crazyflie")
    axs[0, col].plot(ts_data["timestamp"], ts_data["gyro(d/s)"], color="black", label="TinySense")
    # axs[0, col].set_ylabel("Angular Velocity(rad/s)")
    axs[0, col].set_ylim(YLIM_GYRO)
    # axs[0, col].legend(loc='upper left')
    # axs[0, col].legend(loc='lower right')
    
    # Plot optic flow
    axs[1, col].plot(cf_data["timestamp"], cf_data["of_x(pixels/frame)"], linewidth="5", color = "lightgrey", label="Crazyflie")
    axs[1, col].plot(ts_data["timestamp"], ts_data["optic_flow(rad/s)"], color = "black", label="TinySense")
    # axs[1, col].set_ylabel("Optical Flow (pixels/frame)")
    axs[1, col].set_ylim(YLIM_OPTIC_FLOW)
    # axs[1, col].legend(loc='upper left')
    # axs[1, col].legend()
    
    # Plot altitude measurements
    axs[2, col].plot(cf_data["timestamp"], cf_data["pz(m)"], linewidth="5", color="lightgrey", label="Crazyflie")
    axs[2, col].plot(ts_data["timestamp"], ts_data["z(m)"], color = "black", label="TinySense")
    axs[2, col].plot(mocap_data["timestamp"], mocap_data["z(m)"], linestyle="dashed", color = "black", linewidth="3", label="Mocap")
    # axs[2, col].set_ylabel("Altitude (m)")
    axs[2, col].set_ylim(YLIM_ALTITUDE)
    # axs[2, col].legend(loc='upper left')
    
    
    if col == 0:
        axs[0, col].set_ylabel(r"Angular Velocity $\omega_m$ (rad/s)")
        # axs[1, col].set_ylabel("Optical Flow $\Omega$ (pixels/frame)")
        axs[1, col].set_ylabel("Optical Flow $\Omega_m$ (rad/s)")
        axs[2, col].set_ylabel("Altitude $z_m$ (m)")
        axs[0, col].legend(loc='upper left')
        axs[1, col].legend(loc='lower right')
        axs[2, col].legend(loc='lower right')
    else:
        axs[0, col].set_yticks([])  # Remove y-axis numbers for the second sand third columns
        axs[1, col].set_yticks([])  # Remove y-axis numbers for the second and third columns
        axs[2, col].set_yticks([])  # Remove y-axis numbers for the second and third columns
    #     axs[0, col].set_yticklabels([])
    #     axs[1, col].set_yticklabels([])
    #     axs[2, col].set_yticklabels([])
        # Remove y-axis labels for the second and third columns
        axs[0, col].set_ylabel('')  # Remove label for gyro
        axs[1, col].set_ylabel('')  # Remove label for optic flow
        axs[2, col].set_ylabel('')  # Remove label for altitude
    
    # for ax in axs[:, col]:
    #     ax.set_xlabel("Timestamp")
    axs[0, col].set_xticks([])
    axs[1, col].set_xticks([])
    axs[2, col].set_xlabel(r"Time $t$ (s)")
    # Add the column title (a), (b), (c)
    axs[0, col].annotate(title, xy=(0.5, 1.1), xytext=(0, 5),
                         xycoords='axes fraction', textcoords='offset points',
                         ha='center', va='baseline', fontsize=14, fontweight='bold')

def plot_data_all_sensors_bw_without_vertical_axis(cf_data, ts_data, mocap_data, axs, col, title):
    # ylabels = ["$vx$ (m/s)", r"$\theta$ $(rad)$", "$z$ $(m)$"]
    YLIM_GYRO = [-5, 5]
    YLIM_OPTIC_FLOW = [-2.6, 2.6]
    YLIM_ALTITUDE = [-2.8, 1.5]

    # Plot gyro
    axs[0, col].plot(cf_data["timestamp"], cf_data["gyro_pitch_filtered(rad/s)"], linewidth="5", color="lightgrey", label="Crazyflie")
    axs[0, col].plot(ts_data["timestamp"], ts_data["gyro(d/s)"], color="black", label="Tinysense")
    # axs[0, col].set_ylabel("Angular Velocity(rad/s)")
    axs[0, col].set_ylim(YLIM_GYRO)
    axs[0, col].legend(loc='upper left')
    
    # Plot optic flow
    axs[1, col].plot(cf_data["timestamp"], cf_data["of_x(pixels/frame)"], linewidth="5", color = "lightgrey", label="Crazyflie")
    axs[1, col].plot(ts_data["timestamp"], ts_data["optic_flow(rad/s)"], color = "black", label="Tinysense")
    # axs[1, col].set_ylabel("Optical Flow (pixels/frame)")
    axs[1, col].set_ylim(YLIM_OPTIC_FLOW)
    axs[1, col].legend(loc='upper left')
    # axs[1, col].legend()
    
    # Plot altitude measurements
    axs[2, col].plot(cf_data["timestamp"], cf_data["pz(m)"], linewidth="5", color="lightgrey", label="Crazyflie")
    axs[2, col].plot(ts_data["timestamp"], ts_data["z(m)"], color = "black", label="Tinysense")
    axs[2, col].plot(mocap_data["timestamp"], mocap_data["z(m)"], linestyle="dashed", color = "black", linewidth="3", label="Mocap")
    # axs[2, col].set_ylabel("Altitude (m)")
    axs[2, col].set_ylim(YLIM_ALTITUDE)
    axs[2, col].legend(loc='upper left')
    
    for ax in axs[:, col]: 
        ax.set_xlabel("Time (s)")

    # Add the column title (a), (b), (c)
    axs[0, col].annotate(title, xy=(0.5, 1.1), xytext=(0, 5),
                          xycoords='axes fraction', textcoords='offset points',
                          ha='center', va='baseline', fontsize=14, fontweight='bold')

def plot_estimates_all(cf_data, ts_data, mocap_data, q_est, axs, col, title, zero_idx, zero_idx_cf, zero_idx_mocap):
    
    YLIM_VX = [-1.5, 1.5]
    YLIM_THETA = [-30, 30]
    YLIM_ALTITUDE = [-2.8, 1.5] 
    
    
    # Plot vx
    axs[0, col].plot(cf_data[zero_idx_cf:, 0], -cf_data[zero_idx_cf:, 5], linewidth="5", color="lightgrey", label="Crazyflie")
    # axs[0, col].plot(ts_data[:, 0], q_est[:, 2], color="black", label="Tinysense")
    # axs[0, col].plot(q_est[:, 0], q_est[:, 2], color="black", label="Tinysense")
    axs[0, col].plot(q_est[zero_idx:, 0], q_est[zero_idx:, 2], color="black", label="TinySense")
    axs[0, col].plot(mocap_data[zero_idx_mocap:, 0], mocap_data[zero_idx_mocap:, 1], linestyle="dashed", color="black", label="Mocap")
    # axs[0, col].set_ylabel("Velocity vx (m/s)")
    axs[0, col].set_ylim(YLIM_VX)
    # axs[0, col].legend(loc='upper left')
    
    # Plot theta
    axs[1, col].plot(cf_data[zero_idx_cf:, 0], np.degrees(cf_data[zero_idx_cf:, 6]), linewidth="5", color="lightgrey", label="Crazyflie")
    # axs[1, col].plot(ts_data[:, 0], -q_est[:, 1], color="black", label="Tinysense")
    # axs[1, col].plot(q_est[:, 0], -q_est[:, 1], color="black", label="Tinysense")
    axs[1, col].plot(q_est[zero_idx:, 0], -np.degrees(q_est[zero_idx:, 1]), color="black", label="TinySense")
    axs[1, col].plot(mocap_data[zero_idx_mocap:, 0], np.degrees(mocap_data[zero_idx_mocap:, 2]), linestyle="dashed", color="black", label="Mocap")
    # axs[1, col].set_ylabel("Pitch angle (rad)")
    axs[1, col].set_ylim(YLIM_THETA)
    # axs[1, col].legend(loc='upper left')
    
    # Plot altitude estimates
    axs[2, col].plot(cf_data[zero_idx_cf:, 0], cf_data[zero_idx_cf:, 3], linewidth="5", color="lightgrey", label="Crazyflie")
    # axs[2, col].plot(ts_data[:, 0], q_est[:, 3], color="black", label="Tinysense")
    # axs[2, col].plot(q_est[:, 0], q_est[:, 3], color="black", label="Tinysense")
    axs[2, col].plot(q_est[zero_idx:, 0], q_est[zero_idx:, 3], color="black", label="TinySense")
    axs[2, col].plot(mocap_data[zero_idx_mocap:, 0], mocap_data[zero_idx_mocap:, 3], linestyle="dashed", color="black", label="Mocap")
    # axs[2, col].set_ylabel("Altitude (m)")
    axs[2, col].set_ylim(YLIM_ALTITUDE)
    # axs[2, col].legend(loc='upper left')
    
    if col == 0:
        axs[0, col].set_ylabel(r"Velocity $\hat v_x$ (m/s)")
        axs[1, col].set_ylabel(r"Pitch angle $\hat \theta$ (deg)")
        axs[2, col].set_ylabel(r"Altitude $\hat z$ (m)")
        axs[0, col].legend(loc='upper left')
        axs[1, col].legend(loc='upper left')
        axs[2, col].legend(loc='lower right')
    else:
        axs[0, col].set_yticks([])  # Remove y-axis numbers for the second and third columns
        axs[1, col].set_yticks([])  # Remove y-axis numbers for the second and third columns
        axs[2, col].set_yticks([])  # Remove y-axis numbers for the second and third columns
        axs[0, col].set_yticklabels([])
        axs[1, col].set_yticklabels([])
        axs[2, col].set_yticklabels([])
    
    

    # for ax in axs[:, col]:
    #     ax.set_xlabel("Timestamp")
    axs[0, col].set_xticks([])
    axs[1, col].set_xticks([])
    axs[2, col].set_xlabel(r"Time $t$ (s)")
    # Add the column title (a), (b), (c)
    # axs[2, col].annotate(title, xy=(0.5, -0.1), xytext=(0, -5),
    #                      xycoords='axes fraction', textcoords='offset points',
    #                      ha='center', va='baseline', fontsize=14, fontweight='bold')


    axs[0, col].annotate(title, xy=(0.5, 1.1), xytext=(0, 5),
                         xycoords='axes fraction', textcoords='offset points',
                         ha='center', va='baseline', fontsize=14, fontweight='bold')
    
def plot_estimates_all_without_vertical_axis(cf_data, ts_data, mocap_data, q_est, axs, col, title):
    
    YLIM_VX = [-1.5, 1.5]
    YLIM_THETA = [-0.5, 0.5]
    YLIM_ALTITUDE = [-2.8, 1.5] 
    
    
    # Plot vx
    axs[0, col].plot(cf_data[:, 0], -cf_data[:, 5], linewidth="5", color="lightgrey", label="Crazyflie")
    axs[0, col].plot(ts_data[:, 0], q_est[:, 2], color="black", label="Tinysense")
    axs[0, col].plot(mocap_data[:, 0], mocap_data[:, 1], linestyle="dashed", color="black", label="Mocap")
    # axs[0, col].set_ylabel("Velocity vx (m/s)")
    axs[0, col].set_ylim(YLIM_VX)
    axs[0, col].legend(loc='upper left')
    
    # Plot theta
    axs[1, col].plot(cf_data[:, 0], cf_data[:, 6], linewidth="5", color="lightgrey", label="Crazyflie")
    axs[1, col].plot(ts_data[:, 0], -q_est[:, 1], color="black", label="Tinysense")
    axs[1, col].plot(mocap_data[:, 0], mocap_data[:, 2], linestyle="dashed", color="black", label="Mocap")
    # axs[1, col].set_ylabel("Pitch angle (rad)")
    axs[1, col].set_ylim(YLIM_THETA)
    axs[1, col].legend(loc='upper left')
    
    # Plot altitude estimates
    axs[2, col].plot(cf_data[:, 0], cf_data[:, 3], linewidth="5", color="lightgrey", label="Crazyflie")
    axs[2, col].plot(ts_data[:, 0], q_est[:, 3], color="black", label="Tinysense")
    axs[2, col].plot(mocap_data[:, 0], mocap_data[:, 3], linestyle="dashed", color="black", label="Mocap")
    # axs[2, col].set_ylabel("Altitude (m)")
    axs[2, col].set_ylim(YLIM_ALTITUDE)
    axs[2, col].legend(loc='upper left')
    
    for ax in axs[:, col]:
        ax.set_xlabel("Timestamp")

    # Add the column title (a), (b), (c)
    axs[0, col].annotate(title, xy=(0.5, 1.1), xytext=(0, 5),
                          xycoords='axes fraction', textcoords='offset points',
                          ha='center', va='baseline', fontsize=14, fontweight='bold')
    
def plot_data_all_sensors_colored(cf_data, ts_data, mocap_data, axs, col, title):
    ylabels = ["$vx$ (m/s)", r"$\theta$ $(rad)$", "$z$ $(m)$"]
    YLIM_GYRO = [-5, 5]
    YLIM_OPTIC_FLOW = [-2.6, 2.6]
    YLIM_ALTITUDE = [-1.1, 1.3]

    # Plot gyro
    axs[0, col].plot(cf_data["timestamp"], cf_data["gyro_pitch_filtered(rad/s)"], linewidth="4", label="Crazyflie Gyro")
    axs[0, col].plot(ts_data["timestamp"], ts_data["gyro(d/s)"], label="Tinysense Gyro")
    axs[0, col].set_ylabel("Gyro Reading (rad/s)")
    axs[0, col].set_ylim(YLIM_GYRO)
    axs[0, col].legend()
    
    # Plot optic flow
    axs[1, col].plot(cf_data["timestamp"], cf_data["of_x(pixels/frame)"], linewidth="4", label="Crazyflie Optic Flow")
    axs[1, col].plot(ts_data["timestamp"], ts_data["optic_flow(rad/s)"], label="Tinysense Optic Flow")
    axs[1, col].set_ylabel("Optical Flow (pixels/frame)")
    axs[1, col].set_ylim(YLIM_OPTIC_FLOW)
    axs[1, col].legend()
    
    # Plot altitude measurements
    axs[2, col].plot(cf_data["timestamp"], cf_data["pz(m)"], linewidth="4", label="Crazyflie Altitude")
    axs[2, col].plot(ts_data["timestamp"], ts_data["z(m)"], label="Tinysense Altitude")
    axs[2, col].plot(mocap_data["timestamp"], mocap_data["z(m)"], linestyle="dashed", linewidth="3", label="Mocap Altitude")
    axs[2, col].set_ylabel("Altitude (m)")
    axs[2, col].set_ylim(YLIM_ALTITUDE)
    axs[2, col].legend()
    
    for ax in axs[:, col]:
        ax.set_xlabel("Timestamp")
    
    # Add the column title (a), (b), (c)
    axs[0, col].annotate(title, xy=(0.5, 1.1), xytext=(0, 5),
                          xycoords='axes fraction', textcoords='offset points',
                          ha='center', va='baseline', fontsize=14, fontweight='bold')
    
    
# def plot_data_all_sensors_try(cf_data, ts_data, mocap_data, axs, col, title):
#     ylabels = ["$vx$ (m/s)", r"$\theta$ $(rad)$", "$z$ $(m)$"]
#     YLIM_GYRO = [-5, 5]
#     YLIM_OPTIC_FLOW = [-2.6, 2.6]
#     YLIM_ALTITUDE = [-1.1, 1.3]

#     # Plot gyro
#     axs[0, col].plot(cf_data["timestamp"], cf_data["gyro_pitch_filtered(rad/s)"], linewidth="4", color = 'lightblue', label="Crazyflie Gyro")
#     axs[0, col].plot(ts_data["timestamp"], ts_data["gyro(d/s)"], color=default_colors[1], label="Tinysense Gyro")
#     axs[0, col].set_ylabel("Gyro Reading (rad/s)")
#     axs[0, col].set_ylim(YLIM_GYRO)
#     axs[0, col].legend()
    
#     # Plot optic flow
#     axs[1, col].plot(cf_data["timestamp"], cf_data["of_x(pixels/frame)"], linewidth="4", label="Crazyflie Optic Flow")
#     axs[1, col].plot(ts_data["timestamp"], ts_data["optic_flow(rad/s)"], label="Tinysense Optic Flow")
#     axs[1, col].set_ylabel("Optical Flow (pixels/frame)")
#     axs[1, col].set_ylim(YLIM_OPTIC_FLOW)
#     axs[1, col].legend()
    
#     # Plot altitude measurements
#     axs[2, col].plot(cf_data["timestamp"], cf_data["pz(m)"], linewidth="4", label="Crazyflie Altitude")
#     axs[2, col].plot(ts_data["timestamp"], ts_data["z(m)"], label="Tinysense Altitude")
#     axs[2, col].plot(mocap_data["timestamp"], mocap_data["z(m)"], linestyle="dashed", linewidth="3", label="Mocap Altitude")
#     axs[2, col].set_ylabel("Altitude (m)")
#     axs[2, col].set_ylim(YLIM_ALTITUDE)
#     axs[2, col].legend()
    
#     for ax in axs[:, col]:
#         ax.set_xlabel("Timestamp")
    
#     # Add the column title (a), (b), (c)
#     axs[0, col].annotate(title, xy=(0.5, 1.1), xytext=(0, 5),
#                          xycoords='axes fraction', textcoords='offset points',
#                          ha='center', va='baseline', fontsize=14, fontweight='bold')